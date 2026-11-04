import uuid
import httpx
import pytest
from app.core.security import decode_jwt
from app.main import app


@pytest.mark.asyncio
async def test_login_success_and_jwt_claims():
    """Verify login with username and email, returning signed JWT tokens with claims."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"auth_user_{suffix}"
        email = f"auth_{suffix}@jeppiaar.edu"
        password = "Password123!Secure"

        # 1. Register and auto-activate user
        reg_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": email,
                "phone_number": f"+9198765{suffix[:5]}",
                "user_type": "STUDENT",
                "password": password,
                "first_name": "Auth",
                "last_name": "Tester",
            },
            params={"auto_activate": True},
        )
        assert reg_res.status_code == 201
        user_id = reg_res.json()["data"]["id"]

        # 2. Login via username
        login_res1 = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": username,
                "password": password,
                "device_info": "Pytest Test Suite",
            },
        )
        assert login_res1.status_code == 200
        data1 = login_res1.json()["data"]
        assert "access_token" in data1
        assert "refresh_token" in data1
        assert data1["token_type"] == "bearer"
        assert data1["user"]["id"] == user_id

        # Verify JWT claims
        access_payload = decode_jwt(data1["access_token"])
        assert access_payload["sub"] == user_id
        assert access_payload["username"] == username
        assert access_payload["email"] == email
        assert access_payload["user_type"] == "STUDENT"
        assert access_payload["type"] == "access"
        assert "exp" in access_payload
        assert "jti" in access_payload

        # 3. Login via email
        login_res2 = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": email,
                "password": password,
            },
        )
        assert login_res2.status_code == 200
        assert "access_token" in login_res2.json()["data"]

        # 4. Verify LOGIN_SUCCESS audit event
        events_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert events_res.status_code == 200
        events = events_res.json()["data"]
        assert any(e["event_type"] == "LOGIN_SUCCESS" for e in events)


@pytest.mark.asyncio
async def test_login_invalid_password_and_failed_event():
    """Verify invalid credentials return 401 and log LOGIN_FAILED event."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"auth_inv_{suffix}"
        email = f"auth_inv_{suffix}@jeppiaar.edu"

        reg_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": email,
                "user_type": "STAFF",
                "password": "CorrectPassword123!",
            },
            params={"auto_activate": True},
        )
        assert reg_res.status_code == 201
        user_id = reg_res.json()["data"]["id"]

        # Attempt with wrong password
        bad_res = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": username,
                "password": "WrongPassword999!",
            },
        )
        assert bad_res.status_code == 401
        err = bad_res.json()["error"]
        assert err["code"] == "AUTHENTICATION_REQUIRED"

        # Check LOGIN_FAILED event
        events_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert events_res.status_code == 200
        events = events_res.json()["data"]
        fail_event = next((e for e in events if e["event_type"] == "LOGIN_FAILED"), None)
        assert fail_event is not None
        assert fail_event["metadata_json"]["attempt_count"] == 1


@pytest.mark.asyncio
async def test_brute_force_lockout_trigger():
    """Verify 5 consecutive failed login attempts trigger account lockout."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"lock_{suffix}"

        reg_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": f"lock_{suffix}@jeppiaar.edu",
                "user_type": "STUDENT",
                "password": "OriginalPassword123!",
            },
            params={"auto_activate": True},
        )
        assert reg_res.status_code == 201
        user_id = reg_res.json()["data"]["id"]

        # Submit 5 incorrect passwords
        for i in range(1, 6):
            res = await client.post(
                "/api/v1/auth/login",
                json={"username_or_email": username, "password": f"BadPassword{i}!"},
            )
            assert res.status_code == 401

        # 6th attempt should explicitly indicate lockout
        res_locked = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": "OriginalPassword123!"},
        )
        assert res_locked.status_code == 401
        assert "temporarily locked" in res_locked.json()["error"]["message"].lower()

        # Check LOCKED_OUT event
        events_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert events_res.status_code == 200
        event_types = [e["event_type"] for e in events_res.json()["data"]]
        assert "LOCKED_OUT" in event_types

        # Admin unlocks account
        unlock_res = await client.post(f"/api/v1/identity/users/{user_id}/unlock")
        assert unlock_res.status_code == 200
        assert unlock_res.json()["data"]["account_status"] == "ACTIVE"

        # Login should now succeed
        retry_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": "OriginalPassword123!"},
        )
        assert retry_res.status_code == 200


@pytest.mark.asyncio
async def test_login_blocked_for_inactive_statuses():
    """Verify login is blocked for PENDING_ACTIVATION, SUSPENDED, and DEACTIVATED accounts."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        password = "Password123!Secure"

        # 1. PENDING_ACTIVATION
        res1 = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"pending_{suffix}",
                "email": f"pending_{suffix}@jeppiaar.edu",
                "user_type": "STUDENT",
                "password": password,
            },
            params={"auto_activate": False},
        )
        assert res1.status_code == 201
        u1_id = res1.json()["data"]["id"]

        login_pending = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": f"pending_{suffix}", "password": password},
        )
        assert login_pending.status_code == 401
        assert "pending activation" in login_pending.json()["error"]["message"].lower()

        # 2. SUSPENDED
        await client.patch(
            f"/api/v1/identity/users/{u1_id}/status",
            json={"account_status": "SUSPENDED", "reason": "Disciplinary action"},
        )
        login_susp = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": f"pending_{suffix}", "password": password},
        )
        assert login_susp.status_code == 401
        assert "suspended" in login_susp.json()["error"]["message"].lower()

        # 3. DEACTIVATED
        await client.post(
            f"/api/v1/identity/users/{u1_id}/deactivate",
            json={"reason": "Left university"},
        )
        login_deact = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": f"pending_{suffix}", "password": password},
        )
        assert login_deact.status_code == 401
        assert "deactivated" in login_deact.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_protected_me_and_footprint_endpoints():
    """Verify /me and /footprint protected endpoints require valid Bearer token."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"prot_{suffix}"
        password = "Password123!Secure"

        await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": f"prot_{suffix}@jeppiaar.edu",
                "user_type": "STUDENT",
                "password": password,
                "first_name": "Protected",
                "last_name": "User",
            },
            params={"auto_activate": True},
        )

        # 1. Access without token -> 401
        no_auth = await client.get("/api/v1/auth/me")
        assert no_auth.status_code == 401

        # 2. Access with malformed token -> 401
        bad_auth = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not-a-valid-jwt-token"},
        )
        assert bad_auth.status_code == 401

        # 3. Login and access /me with valid token -> 200
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": password},
        )
        token = login_res.json()["data"]["access_token"]

        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        me_data = me_res.json()["data"]
        assert me_data["username"] == username
        assert me_data["account_status"] == "ACTIVE"

        # 4. Access /footprint with valid token -> 200
        fp_res = await client.get(
            "/api/v1/auth/footprint",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert fp_res.status_code == 200
        assert fp_res.json()["data"]["username"] == username


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_revocation():
    """Verify refresh token rotation and rejection of already-used refresh tokens."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"rot_{suffix}"
        password = "Password123!Secure"

        await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": f"rot_{suffix}@jeppiaar.edu",
                "user_type": "FACULTY",
                "password": password,
            },
            params={"auto_activate": True},
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": password},
        )
        old_refresh_token = login_res.json()["data"]["refresh_token"]

        # 1. Rotate refresh token
        rotate_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": old_refresh_token, "device_info": "Rotated Device"},
        )
        assert rotate_res.status_code == 200
        new_data = rotate_res.json()["data"]
        assert "access_token" in new_data
        assert "refresh_token" in new_data
        new_refresh_token = new_data["refresh_token"]
        assert new_refresh_token != old_refresh_token

        # 2. Attempting to use the OLD (rotated) refresh token must fail (401)
        reused_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": old_refresh_token},
        )
        assert reused_res.status_code == 401

        # 3. New refresh token can be used again
        second_rotate = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_refresh_token},
        )
        assert second_rotate.status_code == 200


@pytest.mark.asyncio
async def test_logout_blacklists_access_token_and_revokes_refresh():
    """Verify logout blacklists access token JTI and invalidates refresh token."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"logout_{suffix}"
        password = "Password123!Secure"

        await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": f"logout_{suffix}@jeppiaar.edu",
                "user_type": "STAFF",
                "password": password,
            },
            params={"auto_activate": True},
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": password},
        )
        access_token = login_res.json()["data"]["access_token"]
        refresh_token = login_res.json()["data"]["refresh_token"]

        # Verify access token works
        check_before = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert check_before.status_code == 200

        # Perform logout
        logout_res = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token},
        )
        assert logout_res.status_code == 200
        assert logout_res.json()["success"] is True

        # Verify access token is now rejected (blacklisted)
        check_after = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert check_after.status_code == 401
        assert "revoked" in check_after.json()["error"]["message"].lower()

        # Verify refresh token is also revoked
        ref_after = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert ref_after.status_code == 401


@pytest.mark.asyncio
async def test_manual_token_revocation():
    """Verify manual / administrative token revocation immediately invalidates access."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        username = f"rev_{suffix}"
        password = "Password123!Secure"

        await client.post(
            "/api/v1/identity/users",
            json={
                "username": username,
                "email": f"rev_{suffix}@jeppiaar.edu",
                "user_type": "STUDENT",
                "password": password,
            },
            params={"auto_activate": True},
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": password},
        )
        access_token = login_res.json()["data"]["access_token"]

        # Revoke the access token
        revoke_res = await client.post(
            "/api/v1/auth/revoke",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"token": access_token, "reason": "Compromised device report"},
        )
        assert revoke_res.status_code == 200

        # Subsequent call with revoked token must fail
        post_rev = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert post_rev.status_code == 401
        assert "revoked" in post_rev.json()["error"]["message"].lower()

