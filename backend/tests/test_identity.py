import uuid
import httpx
import pytest
from app.core.security import (
    generate_secure_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.main import app


# ==============================================================================
# Unit Tests: Security & Password Hashing
# ==============================================================================

def test_argon2id_hashing_and_verification():
    """Verify password hashing produces Argon2id hashes and validates properly."""
    raw_password = "SecureInstitutionalPassword2026!"
    hashed = get_password_hash(raw_password)

    # Must be valid Argon2id hash format
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


def test_token_generation_and_hashing():
    """Verify token entropy and cryptographic hashing."""
    token = generate_secure_token(32)
    assert len(token) >= 40
    digest = hash_token(token)
    assert len(digest) == 64  # SHA-256 hex length
    assert hash_token(token) == digest


# ==============================================================================
# Integration Tests: User Identity Lifecycle
# ==============================================================================

@pytest.mark.asyncio
async def test_user_registration_argon2_hashing_and_pending_activation():
    """Verify user registration stores Argon2id hash and starts in PENDING_ACTIVATION."""
    uname = f"usr_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"
    password = "MyStrongPassword123!"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": uname,
                "email": email,
                "password": password,
                "user_type": "STUDENT",
                "profile": {
                    "first_name": "Arun",
                    "last_name": "Kumar",
                    "city": "Chennai",
                    "country": "India",
                },
            },
        )
        assert res.status_code == 201
        body = res.json()
        assert body["success"] is True
        data = body["data"]

        assert data["username"] == uname
        assert data["email"] == email
        assert data["account_status"] == "PENDING_ACTIVATION"
        assert data["email_verified"] is False
        assert "password" not in data
        assert "password_hash" not in data

        # Profile attached
        assert data["profile"]["first_name"] == "Arun"
        assert data["profile"]["last_name"] == "Kumar"
        assert data["profile"]["city"] == "Chennai"


@pytest.mark.asyncio
async def test_duplicate_username_and_email_prevention():
    """Verify username and email collisions trigger 409 Conflict."""
    uname = f"dup_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Register first instance
        res1 = await client.post(
            "/api/v1/identity/users",
            json={"username": uname, "email": email, "password": "Password123!"},
        )
        assert res1.status_code == 201

        # Duplicate username
        res2 = await client.post(
            "/api/v1/identity/users",
            json={"username": uname, "email": f"other_{email}", "password": "Password123!"},
        )
        assert res2.status_code == 409
        assert res2.json()["error"]["code"] == "RESOURCE_CONFLICT"

        # Duplicate email
        res3 = await client.post(
            "/api/v1/identity/users",
            json={"username": f"other_{uname}", "email": email, "password": "Password123!"},
        )
        assert res3.status_code == 409
        assert res3.json()["error"]["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_account_activation_workflow():
    """Verify one-time token activation and reuse prevention."""
    uname = f"act_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        reg_res = await client.post(
            "/api/v1/identity/users",
            json={"username": uname, "email": email, "password": "Password123!"},
        )
        assert reg_res.status_code == 201
        msg = reg_res.json()["message"]
        assert "Activation token: " in msg
        token = msg.split("Activation token: ")[1].strip()

        # Activate
        act_res = await client.post(f"/api/v1/identity/users/activate?token={token}")
        assert act_res.status_code == 200
        user_data = act_res.json()["data"]
        assert user_data["account_status"] == "ACTIVE"
        assert user_data["email_verified"] is True
        assert user_data["activated_at"] is not None

        # Reusing token must fail
        act_res2 = await client.post(f"/api/v1/identity/users/activate?token={token}")
        assert act_res2.status_code == 400
        assert act_res2.json()["error"]["code"] == "BAD_REQUEST"


@pytest.mark.asyncio
async def test_user_profile_update():
    """Verify updating personal profile attributes."""
    uname = f"prof_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/identity/users",
            params={"auto_activate": True},
            json={
                "username": uname,
                "email": email,
                "password": "Password123!",
                "profile": {"first_name": "Deepak", "last_name": "R"},
            },
        )
        user_id = reg.json()["data"]["id"]

        # Update profile
        patch_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/profile",
            json={
                "blood_group": "O+",
                "city": "Chennai",
                "emergency_contact_name": "Ramesh",
                "emergency_contact_phone": "+919988776655",
            },
        )
        assert patch_res.status_code == 200
        pdata = patch_res.json()["data"]
        assert pdata["blood_group"] == "O+"
        assert pdata["city"] == "Chennai"
        assert pdata["emergency_contact_name"] == "Ramesh"


@pytest.mark.asyncio
async def test_account_lifecycle_status_transitions():
    """Verify suspension, deactivation, and reinstatement transitions."""
    uname = f"life_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/identity/users",
            params={"auto_activate": True},
            json={"username": uname, "email": email, "password": "Password123!"},
        )
        user_id = reg.json()["data"]["id"]

        # 1. Suspend
        sus_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "SUSPENDED", "reason": "Administrative fee audit pending"},
        )
        assert sus_res.status_code == 200
        assert sus_res.json()["data"]["account_status"] == "SUSPENDED"

        # 2. Deactivate
        deact_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "DEACTIVATED", "reason": "Employee retired"},
        )
        assert deact_res.status_code == 200
        data = deact_res.json()["data"]
        assert data["account_status"] == "DEACTIVATED"
        assert data["deactivated_at"] is not None
        assert data["deactivation_reason"] == "Employee retired"

        # 3. Reinstate back to ACTIVE
        rein_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "ACTIVE", "reason": "Reinstated by HR"},
        )
        assert rein_res.status_code == 200
        rdata = rein_res.json()["data"]
        assert rdata["account_status"] == "ACTIVE"
        assert rdata["deactivated_at"] is None
        assert rdata["deactivation_reason"] is None


@pytest.mark.asyncio
async def test_password_change_lifecycle():
    """Verify user password change validates current credentials."""
    uname = f"pwd_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"
    old_pwd = "OldPassword123!"
    new_pwd = "NewSecurePassword456!"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/identity/users",
            params={"auto_activate": True},
            json={"username": uname, "email": email, "password": old_pwd},
        )
        user_id = reg.json()["data"]["id"]

        # Invalid current password
        bad_change = await client.post(
            f"/api/v1/identity/users/{user_id}/password",
            json={"current_password": "WrongOldPassword!", "new_password": new_pwd},
        )
        assert bad_change.status_code == 400
        assert bad_change.json()["error"]["code"] == "BAD_REQUEST"

        # Valid password change
        good_change = await client.post(
            f"/api/v1/identity/users/{user_id}/password",
            json={"current_password": old_pwd, "new_password": new_pwd},
        )
        assert good_change.status_code == 200
        assert good_change.json()["success"] is True


@pytest.mark.asyncio
async def test_password_reset_recovery_workflow():
    """Verify password recovery workflow via secure reset token."""
    uname = f"reset_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"
    old_pwd = "InitialPassword123!"
    brand_new_pwd = "ResetBrandNewPassword789!"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/identity/users",
            params={"auto_activate": True},
            json={"username": uname, "email": email, "password": old_pwd},
        )
        user_id = reg.json()["data"]["id"]

        # Request reset
        req_res = await client.post(
            "/api/v1/identity/users/password-reset/request",
            json={"identifier": email},
        )
        assert req_res.status_code == 200
        msg = req_res.json()["message"]
        assert "Test Token: " in msg
        token = msg.split("Test Token: ")[1].strip(" )")

        # Confirm reset
        conf_res = await client.post(
            "/api/v1/identity/users/password-reset/confirm",
            json={"token": token, "new_password": brand_new_pwd},
        )
        assert conf_res.status_code == 200
        assert conf_res.json()["success"] is True

        # Verify old token cannot be reused
        conf_res2 = await client.post(
            "/api/v1/identity/users/password-reset/confirm",
            json={"token": token, "new_password": "AnotherPassword999!"},
        )
        assert conf_res2.status_code == 400


@pytest.mark.asyncio
async def test_identity_lifecycle_audit_trail():
    """Verify full chronological lifecycle event audit trail."""
    uname = f"audit_{uuid.uuid4().hex[:8]}"
    email = f"{uname}@jeppiaar.ac.in"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create
        reg = await client.post(
            "/api/v1/identity/users",
            params={"auto_activate": False},
            json={"username": uname, "email": email, "password": "Password123!"},
        )
        user_id = reg.json()["data"]["id"]
        token = reg.json()["message"].split("Activation token: ")[1].strip()

        # 2. Activate
        await client.post(f"/api/v1/identity/users/activate?token={token}")

        # 3. Update profile
        await client.patch(
            f"/api/v1/identity/users/{user_id}/profile",
            json={"first_name": "Audited", "last_name": "Student"},
        )

        # 4. Suspend
        await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "SUSPENDED", "reason": "Investigation"},
        )

        # Query lifecycle audit history
        hist_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert hist_res.status_code == 200
        events = hist_res.json()["data"]

        event_types = [e["event_type"] for e in events]
        assert "CREATED" in event_types
        assert "ACTIVATED" in event_types
        assert "PROFILE_UPDATED" in event_types
        assert "SUSPENDED" in event_types

