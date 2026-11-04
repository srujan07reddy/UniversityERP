import uuid
import httpx
import pytest
from app.main import app


async def setup_staff_hierarchy(client: httpx.AsyncClient):
    """Helper to set up University, School, and Department for staff testing."""
    suffix = uuid.uuid4().hex[:6].upper()

    # University
    u_res = await client.post(
        "/api/v1/organization/universities",
        json={"code": f"UNIV-STF-{suffix}", "name": f"Staff Test University {suffix}"},
    )
    assert u_res.status_code == 201
    univ_id = u_res.json()["data"]["id"]

    # School
    s_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"SCH-ENG-{suffix}",
            "name": f"School of Engineering {suffix}",
            "unit_type": "SCHOOL",
        },
    )
    assert s_res.status_code == 201
    school_id = s_res.json()["data"]["id"]

    # Department 1 (under school)
    d1_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "parent_unit_id": school_id,
            "code": f"DEPT-CSE-{suffix}",
            "name": f"Department of CSE {suffix}",
            "unit_type": "DEPARTMENT",
        },
    )
    assert d1_res.status_code == 201
    dept1_id = d1_res.json()["data"]["id"]

    # Department 2 (for transfer testing)
    d2_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "parent_unit_id": school_id,
            "code": f"DEPT-ECE-{suffix}",
            "name": f"Department of ECE {suffix}",
            "unit_type": "DEPARTMENT",
        },
    )
    assert d2_res.status_code == 201
    dept2_id = d2_res.json()["data"]["id"]

    return {
        "univ_id": univ_id,
        "school_id": school_id,
        "dept1_id": dept1_id,
        "dept2_id": dept2_id,
    }


# ==============================================================================
# 1. Staff Appointment and Registration
# ==============================================================================

@pytest.mark.asyncio
async def test_staff_appointment_and_profile_creation():
    """Verify staff member appointment, qualifications, experience, and appointment lifecycle logging."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)
        staff_code = f"FAC-CSE-{uuid.uuid4().hex[:6].upper()}"

        payload = {
            "staff_id": staff_code,
            "biometric_id": f"BIO-{uuid.uuid4().hex[:6].upper()}",
            "first_name": "Dr. Anand",
            "middle_name": "Kumar",
            "last_name": "Seshadri",
            "date_of_birth": "1980-08-20",
            "gender": "MALE",
            "blood_group": "A+",
            "nationality": "Indian",
            "pan_number": "ABCDE1234F",
            "personal_email": "anand.seshadri@example.com",
            "institutional_email": f"anand.{uuid.uuid4().hex[:4]}@jeppiaar.ac.in",
            "phone_number": "+91-9840123456",
            "emergency_contact_name": "Sita Anand",
            "emergency_contact_phone": "+91-9840123457",
            "emergency_contact_relationship": "Spouse",
            "permanent_address": "15 Green Garden, Adyar, Chennai",
            "current_address": "15 Green Garden, Adyar, Chennai",
            "staff_type": "TEACHING",
            "employment_type": "REGULAR",
            "designation": "Associate Professor",
            "highest_qualification": "Ph.D. in Computer Science",
            "specialization_area": "Distributed Systems and Cloud Computing",
            "department_id": infra["dept1_id"],
            "school_id": infra["school_id"],
            "date_of_joining": "2026-06-01",
            "probation_end_date": "2027-05-31",
            "notice_period_days": 60,
            "employment_status": "ACTIVE",
            "initial_qualifications": [
                {
                    "degree": "Ph.D.",
                    "discipline_or_field": "Computer Science & Engineering",
                    "institution_name": "Indian Institute of Technology Madras",
                    "board_or_university": "IIT Madras",
                    "year_of_passing": 2015,
                    "remarks": "Gold Medalist",
                },
                {
                    "degree": "M.Tech",
                    "discipline_or_field": "Computer Science",
                    "institution_name": "Anna University CEG",
                    "board_or_university": "Anna University",
                    "year_of_passing": 2008,
                    "percentage_or_cgpa": "9.1 CGPA",
                },
            ],
            "initial_experience": [
                {
                    "organization_name": "National Institute of Technology Trichy",
                    "designation": "Assistant Professor",
                    "experience_type": "TEACHING",
                    "start_date": "2015-07-01",
                    "end_date": "2026-05-15",
                    "roles_and_responsibilities": "Teaching Cloud Computing, Distributed Systems research",
                    "relieving_reason": "Relocated to Chennai",
                }
            ],
        }

        res = await client.post("/api/v1/staff", json=payload)
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["staff_id"] == staff_code
        assert data["designation"] == "Associate Professor"
        assert data["employment_status"] == "ACTIVE"
        staff_id = data["id"]

        # Verify complete dossier
        dossier_res = await client.get(f"/api/v1/staff/{staff_id}/detail")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()["data"]
        assert len(dossier["qualifications"]) == 2
        assert len(dossier["experience_records"]) == 1
        assert len(dossier["lifecycle_events"]) >= 1
        assert dossier["lifecycle_events"][0]["event_type"] == "APPOINTMENT"


@pytest.mark.asyncio
async def test_duplicate_staff_id_and_email_conflicts():
    """Verify duplicate staff_id, biometric_id, and institutional_email trigger 409 Conflict."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)
        shared_staff_id = f"FAC-DUP-{uuid.uuid4().hex[:6].upper()}"
        shared_bio_id = f"BIO-DUP-{uuid.uuid4().hex[:6].upper()}"
        shared_email = f"shared.{uuid.uuid4().hex[:4]}@jeppiaar.ac.in"

        base_payload = {
            "staff_id": shared_staff_id,
            "biometric_id": shared_bio_id,
            "institutional_email": shared_email,
            "first_name": "Faculty",
            "last_name": "Alpha",
            "date_of_birth": "1985-01-01",
            "gender": "FEMALE",
            "staff_type": "TEACHING",
            "designation": "Assistant Professor",
            "department_id": infra["dept1_id"],
            "date_of_joining": "2026-06-01",
        }

        res1 = await client.post("/api/v1/staff", json=base_payload)
        assert res1.status_code == 201

        # Duplicate staff_id
        res2 = await client.post(
            "/api/v1/staff",
            json={**base_payload, "biometric_id": "NEW-BIO-1", "institutional_email": "new1@jeppiaar.ac.in"},
        )
        assert res2.status_code == 409
        assert res2.json()["error"]["code"] == "RESOURCE_CONFLICT"

        # Duplicate biometric_id
        res3 = await client.post(
            "/api/v1/staff",
            json={
                **base_payload,
                "staff_id": f"FAC-NEW-{uuid.uuid4().hex[:4]}",
                "institutional_email": "new2@jeppiaar.ac.in",
            },
        )
        assert res3.status_code == 409
        assert res3.json()["error"]["code"] == "RESOURCE_CONFLICT"

        # Duplicate email
        res4 = await client.post(
            "/api/v1/staff",
            json={
                **base_payload,
                "staff_id": f"FAC-NEW-{uuid.uuid4().hex[:4]}",
                "biometric_id": f"BIO-NEW-{uuid.uuid4().hex[:4]}",
            },
        )
        assert res4.status_code == 409
        assert res4.json()["error"]["code"] == "RESOURCE_CONFLICT"


# ==============================================================================
# 2. Retrieval, Listing, and Search
# ==============================================================================

@pytest.mark.asyncio
async def test_get_staff_and_not_found():
    """Verify single staff retrieval and safe 404 behavior."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)
        code = f"STF-GET-{uuid.uuid4().hex[:6].upper()}"

        create_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": code,
                "first_name": "Ramesh",
                "last_name": "Chandran",
                "date_of_birth": "1990-03-15",
                "gender": "MALE",
                "staff_type": "NON_TEACHING",
                "designation": "Lab Superintendent",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
            },
        )
        assert create_res.status_code == 201
        sid = create_res.json()["data"]["id"]

        get_res = await client.get(f"/api/v1/staff/{sid}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["staff_id"] == code

        fake_id = str(uuid.uuid4())
        nf_res = await client.get(f"/api/v1/staff/{fake_id}")
        assert nf_res.status_code == 404
        assert nf_res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_staff_paginated_and_filters():
    """Verify paginated listing, department/staff_type filtering, and text search."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)
        token = uuid.uuid4().hex[:5]

        # 1 Teaching staff
        s1_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"TCH-{token}",
                "first_name": f"Karthik_{token}",
                "last_name": "Venkatesh",
                "date_of_birth": "1987-04-12",
                "gender": "MALE",
                "staff_type": "TEACHING",
                "designation": "Assistant Professor",
                "department_id": infra["dept1_id"],
                "school_id": infra["school_id"],
                "date_of_joining": "2026-06-01",
                "employment_status": "ACTIVE",
            },
        )
        assert s1_res.status_code == 201

        # 1 Technical staff
        s2_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"TEC-{token}",
                "first_name": f"Bala_{token}",
                "last_name": "Murugan",
                "date_of_birth": "1992-06-25",
                "gender": "MALE",
                "staff_type": "TECHNICAL",
                "designation": "Network Systems Engineer",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
                "employment_status": "ACTIVE",
            },
        )
        assert s2_res.status_code == 201

        # Search by unique first name
        search_res = await client.get(f"/api/v1/staff?search=Karthik_{token}")
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert len(search_data["data"]) == 1
        assert search_data["data"][0]["first_name"] == f"Karthik_{token}"

        # Filter by staff_type TECHNICAL
        tech_res = await client.get(
            f"/api/v1/staff?department_id={infra['dept1_id']}&staff_type=TECHNICAL"
        )
        assert tech_res.status_code == 200
        for item in tech_res.json()["data"]:
            assert item["staff_type"] == "TECHNICAL"


# ==============================================================================
# 3. Profile Updates, Designation Updates, and Department Transfers
# ==============================================================================

@pytest.mark.asyncio
async def test_update_staff_profile():
    """Verify partial updates to contact, address, and demographic info."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)

        s_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-UPD-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Saravanan",
                "last_name": "Govindan",
                "date_of_birth": "1983-11-10",
                "gender": "MALE",
                "staff_type": "TEACHING",
                "designation": "Assistant Professor",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
            },
        )
        assert s_res.status_code == 201
        sid = s_res.json()["data"]["id"]

        patch_res = await client.patch(
            f"/api/v1/staff/{sid}",
            json={
                "phone_number": "+91-9988776655",
                "current_address": "402 Faculty Quarters, Jeppiaar Campus",
                "blood_group": "AB+",
                "highest_qualification": "Ph.D. (Pursuing)",
                "emergency_contact_name": "Revathi S",
            },
        )
        assert patch_res.status_code == 200
        updated = patch_res.json()["data"]
        assert updated["phone_number"] == "+91-9988776655"
        assert updated["blood_group"] == "AB+"
        assert updated["emergency_contact_name"] == "Revathi S"


@pytest.mark.asyncio
async def test_staff_designation_update():
    """Verify promotion/re-designation and audit logging."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)

        s_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-DES-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Geetha",
                "last_name": "Mani",
                "date_of_birth": "1978-02-14",
                "gender": "FEMALE",
                "staff_type": "TEACHING",
                "designation": "Associate Professor",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2020-01-01",
            },
        )
        sid = s_res.json()["data"]["id"]

        desig_res = await client.post(
            f"/api/v1/staff/{sid}/designation",
            json={
                "new_designation": "Professor",
                "reason": "Promoted to Professor under Career Advancement Scheme (CAS)",
                "effective_date": "2026-07-01",
            },
        )
        assert desig_res.status_code == 200
        assert desig_res.json()["data"]["designation"] == "Professor"

        dossier = (await client.get(f"/api/v1/staff/{sid}/detail")).json()["data"]
        events = dossier["lifecycle_events"]
        assert any(e["event_type"] == "DESIGNATION_CHANGE" for e in events)


@pytest.mark.asyncio
async def test_staff_department_transfer():
    """Verify inter-departmental transfer and audit logging."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)

        s_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-TRF-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Mohan",
                "last_name": "Das",
                "date_of_birth": "1985-05-18",
                "gender": "MALE",
                "staff_type": "TEACHING",
                "designation": "Assistant Professor",
                "department_id": infra["dept1_id"],
                "school_id": infra["school_id"],
                "date_of_joining": "2026-06-01",
            },
        )
        sid = s_res.json()["data"]["id"]

        transfer_res = await client.post(
            f"/api/v1/staff/{sid}/transfer",
            json={
                "new_department_id": infra["dept2_id"],
                "new_school_id": infra["school_id"],
                "reason": "Transferred to ECE department for multidisciplinary IoT teaching",
            },
        )
        assert transfer_res.status_code == 200
        assert transfer_res.json()["data"]["department_id"] == infra["dept2_id"]

        dossier = (await client.get(f"/api/v1/staff/{sid}/detail")).json()["data"]
        events = dossier["lifecycle_events"]
        assert any(e["event_type"] == "DEPARTMENT_TRANSFER" for e in events)


# ==============================================================================
# 4. Lifecycle Status Transitions
# ==============================================================================

@pytest.mark.asyncio
async def test_staff_lifecycle_status_transitions():
    """Verify employment status changes (PROBATION -> ACTIVE -> ON_LEAVE -> RELIEVED)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)

        s_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-LC-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Vijay",
                "last_name": "Kumar",
                "date_of_birth": "1989-12-04",
                "gender": "MALE",
                "staff_type": "TEACHING",
                "designation": "Assistant Professor",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
                "employment_status": "PROBATION",
            },
        )
        sid = s_res.json()["data"]["id"]

        # 1. Transition PROBATION -> ACTIVE
        act_res = await client.post(
            f"/api/v1/staff/{sid}/status",
            json={"new_status": "ACTIVE", "reason": "Successful completion of 1-year probation"},
        )
        assert act_res.status_code == 200
        assert act_res.json()["data"]["employment_status"] == "ACTIVE"

        # 2. Transition ACTIVE -> ON_LEAVE
        leave_res = await client.post(
            f"/api/v1/staff/{sid}/status",
            json={"new_status": "ON_LEAVE", "reason": "Sabbatical leave for postdoctoral fellowship"},
        )
        assert leave_res.status_code == 200
        assert leave_res.json()["data"]["employment_status"] == "ON_LEAVE"

        # 3. Transition ON_LEAVE -> RELIEVED
        relieve_res = await client.post(
            f"/api/v1/staff/{sid}/status",
            json={
                "new_status": "RELIEVED",
                "reason": "Resignation accepted with full notice served",
                "date_of_relieving": "2027-06-30",
            },
        )
        assert relieve_res.status_code == 200
        relieved_data = relieve_res.json()["data"]
        assert relieved_data["employment_status"] == "RELIEVED"
        assert relieved_data["date_of_relieving"] == "2027-06-30"

        # 4. Attempt invalid status
        bad_res = await client.post(
            f"/api/v1/staff/{sid}/status",
            json={"new_status": "INVALID_STATE", "reason": "Test rejection"},
        )
        assert bad_res.status_code == 400
        assert bad_res.json()["error"]["code"] == "BAD_REQUEST"


# ==============================================================================
# 5. Qualifications & Experience Management
# ==============================================================================

@pytest.mark.asyncio
async def test_add_qualifications_and_experience():
    """Verify adding additional qualifications and experience records post-appointment."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_staff_hierarchy(client)

        s_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"STF-EXP-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Divya",
                "last_name": "Chandran",
                "date_of_birth": "1991-07-22",
                "gender": "FEMALE",
                "staff_type": "TEACHING",
                "designation": "Assistant Professor",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
            },
        )
        sid = s_res.json()["data"]["id"]

        # Add Qualification
        q_res = await client.post(
            f"/api/v1/staff/{sid}/qualifications",
            json={
                "degree": "Ph.D.",
                "discipline_or_field": "VLSI Design & Embedded Systems",
                "institution_name": "College of Engineering Guindy",
                "board_or_university": "Anna University",
                "year_of_passing": 2023,
                "percentage_or_cgpa": "8.9 CGPA",
                "remarks": "Doctoral thesis defended with high commendation",
            },
        )
        assert q_res.status_code == 201
        assert q_res.json()["data"]["degree"] == "Ph.D."

        # Add Experience
        exp_res = await client.post(
            f"/api/v1/staff/{sid}/experience",
            json={
                "organization_name": "Texas Instruments India",
                "designation": "Senior VLSI Engineer",
                "experience_type": "INDUSTRY",
                "start_date": "2023-08-01",
                "end_date": "2026-05-20",
                "roles_and_responsibilities": "SoC physical design and timing closure",
                "relieving_reason": "Transitioning to academic research",
            },
        )
        assert exp_res.status_code == 201
        assert exp_res.json()["data"]["designation"] == "Senior VLSI Engineer"

        # Check in detail dossier
        dossier = (await client.get(f"/api/v1/staff/{sid}/detail")).json()["data"]
        assert len(dossier["qualifications"]) == 1
        assert len(dossier["experience_records"]) == 1


# ==============================================================================
# 6. Independence of Designation from RBAC Authorization Roles
# ==============================================================================

def test_staff_designation_distinct_from_rbac_roles():
    """
    Verify Staff model does NOT conflate institutional job title (designation)
    with application authorization roles or credentials.
    """
    from app.domains.staff.models import Staff

    staff_columns = {c.name for c in Staff.__table__.columns}

    # Strict architectural decoupling: authorization permissions & credentials belong to User & RBAC (Phase 4)
    assert "password_hash" not in staff_columns
    assert "role" not in staff_columns
    assert "roles" not in staff_columns
    assert "permissions" not in staff_columns
    assert "is_admin" not in staff_columns
    assert "is_superuser" not in staff_columns

    # Institutional employment fields must be present
    assert "designation" in staff_columns
    assert "staff_id" in staff_columns
    assert "department_id" in staff_columns
    assert "staff_type" in staff_columns
    assert "employment_status" in staff_columns
    assert "date_of_joining" in staff_columns

