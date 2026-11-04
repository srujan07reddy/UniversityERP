import uuid
import httpx
import pytest
from app.main import app


async def setup_test_org(client: httpx.AsyncClient):
    """Helper to set up University, Department, and Program for lifecycle tests."""
    suffix = uuid.uuid4().hex[:6].upper()

    u_res = await client.post(
        "/api/v1/organization/universities",
        json={"code": f"UNIV-LC-{suffix}", "name": f"Lifecycle University {suffix}"},
    )
    assert u_res.status_code == 201
    univ_id = u_res.json()["data"]["id"]

    d_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"DEPT-LC-{suffix}",
            "name": f"Lifecycle Department {suffix}",
            "unit_type": "DEPARTMENT",
        },
    )
    assert d_res.status_code == 201
    dept_id = d_res.json()["data"]["id"]

    p_res = await client.post(
        "/api/v1/organization/programs",
        json={
            "department_id": dept_id,
            "program_code": f"PROG-LC-{suffix}",
            "program_name": f"Lifecycle Program {suffix}",
            "program_type": "UNDERGRADUATE",
        },
    )
    assert p_res.status_code == 201
    prog_id = p_res.json()["data"]["id"]

    ay_res = await client.post(
        "/api/v1/organization/academic-years",
        json={
            "university_id": univ_id,
            "code": f"AY-LC-{suffix}",
            "year_name": f"AY {suffix}",
            "start_date": "2026-08-01",
            "end_date": "2027-05-31",
        },
    )
    assert ay_res.status_code == 201
    ay_id = ay_res.json()["data"]["id"]

    sem_res = await client.post(
        "/api/v1/organization/semesters",
        json={
            "academic_year_id": ay_id,
            "semester_number": 1,
            "semester_name": f"Semester 1 {suffix}",
            "term_type": "ODD",
            "start_date": "2026-08-01",
            "end_date": "2026-12-15",
        },
    )
    assert sem_res.status_code == 201
    sem_id = sem_res.json()["data"]["id"]

    return {
        "univ_id": univ_id,
        "dept_id": dept_id,
        "prog_id": prog_id,
        "sem_id": sem_id,
    }


@pytest.mark.asyncio
async def test_user_status_transitions_lifecycle():
    """Verify user account status transitions: Creation -> Activation -> Suspension -> Reinstatement -> Lockout Unlock."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        user_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"user_lc_{suffix}",
                "email": f"user_lc_{suffix}@jeppiaar.edu",
                "phone_number": f"+9198765{suffix[:5]}",
                "user_type": "STAFF",
                "password": "Password123!Secure",
                "first_name": "Lifecycle",
                "last_name": "Tester",
            },
        )
        assert user_res.status_code == 201
        user_data = user_res.json()["data"]
        user_id = user_data["id"]
        assert user_data["account_status"] == "PENDING_ACTIVATION"

        # 1. Activate via status update
        act_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "ACTIVE", "reason": "Verification completed by Admin"},
        )
        assert act_res.status_code == 200
        assert act_res.json()["data"]["account_status"] == "ACTIVE"

        # 2. Suspend user
        susp_res = await client.post(
            f"/api/v1/identity/users/{user_id}/suspend",
            json={"reason": "Disciplinary review pending"},
        )
        assert susp_res.status_code == 200
        assert susp_res.json()["data"]["account_status"] == "SUSPENDED"

        # Redundant suspension should return 409 Conflict
        susp_dup = await client.post(
            f"/api/v1/identity/users/{user_id}/suspend",
            json={"reason": "Attempting second suspension"},
        )
        assert susp_dup.status_code == 409

        # 3. Reinstate user
        reinst_res = await client.post(
            f"/api/v1/identity/users/{user_id}/reinstate",
            json={"reason": "Disciplinary review cleared with no findings"},
        )
        assert reinst_res.status_code == 200
        assert reinst_res.json()["data"]["account_status"] == "ACTIVE"

        # Reinstate when already active should return 400
        reinst_dup = await client.post(
            f"/api/v1/identity/users/{user_id}/reinstate",
            json={"reason": "Attempting redundant reinstate"},
        )
        assert reinst_dup.status_code == 400

        # 4. Lock account via patch then unlock via unlock endpoint
        lock_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/status",
            json={"account_status": "LOCKED", "reason": "Exceeded maximum failed attempts"},
        )
        assert lock_res.status_code == 200
        assert lock_res.json()["data"]["account_status"] == "LOCKED"

        unlock_res = await client.post(f"/api/v1/identity/users/{user_id}/unlock")
        assert unlock_res.status_code == 200
        assert unlock_res.json()["data"]["account_status"] == "ACTIVE"

        # Verify lifecycle events for this user
        events_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert events_res.status_code == 200
        event_types = [e["event_type"] for e in events_res.json()["data"]]
        assert "CREATED" in event_types
        assert "ACTIVATED" in event_types
        assert "SUSPENDED" in event_types
        assert "REINSTATED" in event_types
        assert "LOCKED_OUT" in event_types
        assert "UNLOCKED" in event_types


@pytest.mark.asyncio
async def test_deactivation_zero_cascade_safety():
    """
    CRITICAL INSTITUTIONAL SAFETY TEST:
    Verify that deactivating a User account NEVER deletes or cascades into
    academic records, student profiles, or staff employment records.
    """
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        env = await setup_test_org(client)
        suffix = uuid.uuid4().hex[:6].upper()

        # 1. Create a Student record with academic record
        std_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-DEACT-{suffix}",
                "register_number": f"REG-DEACT-{suffix}",
                "first_name": "Kavitha",
                "last_name": "Raman",
                "date_of_birth": "2008-05-15",
                "gender": "FEMALE",
                "department_id": env["dept_id"],
                "program_id": env["prog_id"],
                "admission_date": "2026-08-01",
                "academic_year_entry": "2026-2027",
                "current_semester": 1,
            },
        )
        assert std_res.status_code == 201
        student_id = std_res.json()["data"]["id"]

        rec_res = await client.post(
            f"/api/v1/students/{student_id}/academic-records",
            json={
                "qualification": "Higher Secondary (12th / HSC)",
                "institution_name": "DAV Senior Secondary School",
                "board_or_university": "CBSE",
                "year_of_passing": 2026,
                "percentage_or_cgpa": "97.4%",
                "stream_or_specialization": "Computer Science (MPC)",
            },
        )
        assert rec_res.status_code == 201

        # 2. Create a Staff record with qualification
        stf_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-DEACT-{suffix}",
                "first_name": "Dr. Suresh",
                "last_name": "Kumar",
                "date_of_birth": "1980-08-12",
                "gender": "MALE",
                "department_id": env["dept_id"],
                "designation": "Associate Professor",
                "staff_type": "TEACHING",
                "date_of_joining": "2026-01-01",
            },
        )
        assert stf_res.status_code == 201
        staff_id = stf_res.json()["data"]["id"]

        qual_res = await client.post(
            f"/api/v1/staff/{staff_id}/qualifications",
            json={
                "degree": "Ph.D.",
                "discipline_or_field": "Computer Science",
                "institution_name": "Jeppiaar University",
                "board_or_university": "Jeppiaar University",
                "year_of_passing": 2020,
            },
        )
        assert qual_res.status_code == 201

        # 3. Create User account & link both
        usr_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"user_deact_{suffix}",
                "email": f"user_deact_{suffix}@jeppiaar.edu",
                "phone_number": f"+9198765{suffix[:5]}",
                "user_type": "STAFF",
                "password": "Password123!Secure",
                "first_name": "Cascading",
                "last_name": "Safety",
            },
            params={"auto_activate": True},
        )
        assert usr_res.status_code == 201
        user_id = usr_res.json()["data"]["id"]

        link_std = await client.post(
            "/api/v1/identity/relationships/link-student",
            json={"user_id": user_id, "student_id": student_id},
        )
        assert link_std.status_code == 200

        link_stf = await client.post(
            "/api/v1/identity/relationships/link-staff",
            json={"user_id": user_id, "staff_id": staff_id},
        )
        assert link_stf.status_code == 200

        # Verify footprint before deactivation
        fp_res = await client.get(f"/api/v1/identity/relationships/footprint/{user_id}")
        assert fp_res.status_code == 200
        assert fp_res.json()["data"]["linked_student"]["id"] == student_id
        assert fp_res.json()["data"]["linked_staff"]["id"] == staff_id

        # 4. Deactivate User Account
        deact_res = await client.post(
            f"/api/v1/identity/users/{user_id}/deactivate",
            json={"reason": "Employee and student left institution permanently"},
        )
        assert deact_res.status_code == 200
        deact_data = deact_res.json()["data"]
        assert deact_data["account_status"] == "DEACTIVATED"
        assert deact_data["deactivated_at"] is not None
        assert deact_data["deactivation_reason"] == "Employee and student left institution permanently"

        # Attempting to deactivate again returns 409 Conflict
        deact_dup = await client.post(
            f"/api/v1/identity/users/{user_id}/deactivate",
            json={"reason": "Redundant deactivation"},
        )
        assert deact_dup.status_code == 409

        # 5. ZERO CASCADE VERIFICATION:
        # Check student record and dossier still exists intact
        std_verify = await client.get(f"/api/v1/students/{student_id}/detail")
        assert std_verify.status_code == 200
        assert std_verify.json()["data"]["admission_number"] == f"ADM-DEACT-{suffix}"
        assert len(std_verify.json()["data"]["academic_records"]) == 1

        # Check staff record and dossier still exists intact
        stf_verify = await client.get(f"/api/v1/staff/{staff_id}/detail")
        assert stf_verify.status_code == 200
        assert stf_verify.json()["data"]["staff_id"] == f"STF-DEACT-{suffix}"
        assert len(stf_verify.json()["data"]["qualifications"]) == 1


@pytest.mark.asyncio
async def test_profile_update_and_audit_event():
    """Verify profile updates record a PROFILE_UPDATED lifecycle event with modified fields."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        user_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"prof_user_{suffix}",
                "email": f"prof_user_{suffix}@jeppiaar.edu",
                "phone_number": f"+9198765{suffix[:5]}",
                "user_type": "STUDENT",
                "password": "Password123!Secure",
                "first_name": "Initial",
                "last_name": "Name",
            },
            params={"auto_activate": True},
        )
        assert user_res.status_code == 201
        user_id = user_res.json()["data"]["id"]

        # Update profile
        prof_res = await client.patch(
            f"/api/v1/identity/users/{user_id}/profile",
            json={
                "first_name": "UpdatedFirst",
                "city": "Chennai",
                "country": "India",
            },
        )
        assert prof_res.status_code == 200
        assert prof_res.json()["data"]["first_name"] == "UpdatedFirst"
        assert prof_res.json()["data"]["city"] == "Chennai"

        # Check lifecycle event
        events_res = await client.get(f"/api/v1/identity/users/{user_id}/lifecycle")
        assert events_res.status_code == 200
        events = events_res.json()["data"]
        prof_event = next((e for e in events if e["event_type"] == "PROFILE_UPDATED"), None)
        assert prof_event is not None
        assert "first_name" in prof_event["metadata_json"]["updated_fields"]
        assert "city" in prof_event["metadata_json"]["updated_fields"]


@pytest.mark.asyncio
async def test_search_institutional_audit_trail():
    """Verify querying and filtering across the global institutional identity audit trail."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6]
        user_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"audit_user_{suffix}",
                "email": f"audit_user_{suffix}@jeppiaar.edu",
                "phone_number": f"+9198765{suffix[:5]}",
                "user_type": "STAFF",
                "password": "Password123!Secure",
                "first_name": "Audit",
                "last_name": "Trail",
            },
            params={"auto_activate": True},
        )
        assert user_res.status_code == 201
        user_id = user_res.json()["data"]["id"]

        # Suspend then reinstate to generate distinct events
        await client.post(
            f"/api/v1/identity/users/{user_id}/suspend",
            json={"reason": "Audit test suspension"},
        )
        await client.post(
            f"/api/v1/identity/users/{user_id}/reinstate",
            json={"reason": "Audit test reinstatement"},
        )

        # 1. Query all events with pagination
        all_events = await client.get("/api/v1/identity/lifecycle/events?page=1&page_size=10")
        assert all_events.status_code == 200
        data = all_events.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        assert data["pagination"]["total_items"] >= 3

        # 2. Filter by user_id
        user_events = await client.get(f"/api/v1/identity/lifecycle/events?user_id={user_id}")
        assert user_events.status_code == 200
        assert user_events.json()["pagination"]["total_items"] >= 3
        for e in user_events.json()["data"]:
            assert e["user_id"] == user_id

        # 3. Filter by event_type
        susp_events = await client.get(
            f"/api/v1/identity/lifecycle/events?user_id={user_id}&event_type=SUSPENDED"
        )
        assert susp_events.status_code == 200
        assert len(susp_events.json()["data"]) == 1
        assert susp_events.json()["data"][0]["event_type"] == "SUSPENDED"
        assert susp_events.json()["data"][0]["reason"] == "Audit test suspension"
