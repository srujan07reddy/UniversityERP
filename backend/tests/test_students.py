import uuid
import httpx
import pytest
from app.main import app


async def setup_academic_hierarchy(client: httpx.AsyncClient):
    """Helper to set up University, Department, Program, Batch, Section, Academic Year, and Semester."""
    suffix = uuid.uuid4().hex[:6].upper()

    # University
    u_res = await client.post(
        "/api/v1/organization/universities",
        json={"code": f"UNIV-{suffix}", "name": f"University {suffix}"},
    )
    assert u_res.status_code == 201
    univ_id = u_res.json()["data"]["id"]

    # Department
    d_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"CSE-{suffix}",
            "name": f"Computer Science and Engineering {suffix}",
            "unit_type": "DEPARTMENT",
        },
    )
    assert d_res.status_code == 201
    dept_id = d_res.json()["data"]["id"]

    # Academic Program
    p_res = await client.post(
        "/api/v1/organization/programs",
        json={
            "department_id": dept_id,
            "program_code": f"BE-CSE-{suffix}",
            "program_name": "B.E. Computer Science and Engineering",
            "program_type": "UNDERGRADUATE",
            "duration_years": 4,
            "total_semesters": 8,
        },
    )
    assert p_res.status_code == 201
    prog_id = p_res.json()["data"]["id"]

    # Academic Year
    ay_res = await client.post(
        "/api/v1/organization/academic-years",
        json={
            "university_id": univ_id,
            "year_name": f"2026-2027-{suffix}",
            "start_date": "2026-06-01",
            "end_date": "2027-05-31",
            "is_current": True,
        },
    )
    assert ay_res.status_code == 201
    ay_id = ay_res.json()["data"]["id"]

    # Semesters
    sem1_res = await client.post(
        "/api/v1/organization/semesters",
        json={
            "academic_year_id": ay_id,
            "semester_number": 1,
            "semester_name": "Semester 1",
            "semester_type": "ODD",
            "start_date": "2026-06-01",
            "end_date": "2026-11-30",
            "is_current": True,
        },
    )
    assert sem1_res.status_code == 201
    sem1_id = sem1_res.json()["data"]["id"]

    sem2_res = await client.post(
        "/api/v1/organization/semesters",
        json={
            "academic_year_id": ay_id,
            "semester_number": 2,
            "semester_name": "Semester 2",
            "semester_type": "EVEN",
            "start_date": "2026-12-01",
            "end_date": "2027-05-31",
            "is_current": False,
        },
    )
    assert sem2_res.status_code == 201
    sem2_id = sem2_res.json()["data"]["id"]

    # Batch
    b_res = await client.post(
        "/api/v1/organization/batches",
        json={
            "program_id": prog_id,
            "academic_year_id": ay_id,
            "batch_name": f"Batch 2026-2030-{suffix}",
            "admission_year": 2026,
            "graduation_year": 2030,
            "current_semester_number": 1,
        },
    )
    assert b_res.status_code == 201
    batch_id = b_res.json()["data"]["id"]

    # Section
    s_res = await client.post(
        "/api/v1/organization/sections",
        json={
            "batch_id": batch_id,
            "program_id": prog_id,
            "academic_year_id": ay_id,
            "section_name": "A",
            "capacity": 60,
        },
    )
    assert s_res.status_code == 201
    sec_id = s_res.json()["data"]["id"]

    return {
        "univ_id": univ_id,
        "dept_id": dept_id,
        "prog_id": prog_id,
        "ay_id": ay_id,
        "sem1_id": sem1_id,
        "sem2_id": sem2_id,
        "batch_id": batch_id,
        "sec_id": sec_id,
    }


# ==============================================================================
# 1. Student Registration & Validation
# ==============================================================================

@pytest.mark.asyncio
async def test_student_admission_and_profile_creation():
    """Verify student admission, demographic persistence, and initial lifecycle logging."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)
        adm_no = f"ADM-2026-{uuid.uuid4().hex[:6].upper()}"

        payload = {
            "admission_number": adm_no,
            "register_number": f"REG-{uuid.uuid4().hex[:6].upper()}",
            "first_name": "Priya",
            "middle_name": "Dharshini",
            "last_name": "Rajaraman",
            "date_of_birth": "2008-05-14",
            "gender": "FEMALE",
            "blood_group": "B+",
            "nationality": "Indian",
            "community": "BC",
            "religion": "Hindu",
            "personal_email": "priya.raj@example.com",
            "institutional_email": f"priya.{uuid.uuid4().hex[:4]}@jeppiaar.ac.in",
            "phone_number": "+91-9876543210",
            "emergency_contact_name": "Rajaraman S",
            "emergency_contact_phone": "+91-9876543211",
            "emergency_contact_relationship": "Father",
            "permanent_address": "42 Anna Salai, Chennai, TN",
            "current_address": "Hostel Block B, Room 102",
            "father_name": "Rajaraman S",
            "father_phone": "+91-9876543211",
            "father_occupation": "Engineer",
            "mother_name": "Lakshmi R",
            "mother_phone": "+91-9876543212",
            "mother_occupation": "Teacher",
            "department_id": infra["dept_id"],
            "program_id": infra["prog_id"],
            "batch_id": infra["batch_id"],
            "section_id": infra["sec_id"],
            "admission_date": "2026-06-15",
            "admission_category": "REGULAR",
            "current_semester": 1,
            "student_status": "ADMITTED",
            "initial_academic_records": [
                {
                    "qualification": "Secondary (10th)",
                    "institution_name": "St. Joseph Matriculation School",
                    "board_or_university": "Tamil Nadu State Board",
                    "year_of_passing": 2024,
                    "percentage_or_cgpa": "95.6%",
                },
                {
                    "qualification": "Higher Secondary (12th / HSC)",
                    "institution_name": "St. Joseph Higher Secondary School",
                    "board_or_university": "Tamil Nadu State Board",
                    "year_of_passing": 2026,
                    "percentage_or_cgpa": "96.2%",
                },
            ],
        }

        res = await client.post("/api/v1/students", json=payload)
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["admission_number"] == adm_no
        assert data["first_name"] == "Priya"
        assert data["student_status"] == "ADMITTED"
        assert data["current_semester"] == 1
        student_id = data["id"]

        # Verify full dossier contains initial academic records and admission lifecycle event
        dossier_res = await client.get(f"/api/v1/students/{student_id}/detail")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()["data"]
        assert len(dossier["academic_records"]) == 2
        assert len(dossier["lifecycle_events"]) >= 1
        assert dossier["lifecycle_events"][0]["event_type"] == "ADMISSION"


@pytest.mark.asyncio
async def test_duplicate_admission_number_conflict():
    """Verify duplicate admission numbers trigger a 409 Conflict exception."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)
        shared_adm = f"ADM-DUP-{uuid.uuid4().hex[:6].upper()}"

        base_payload = {
            "admission_number": shared_adm,
            "first_name": "Student",
            "last_name": "One",
            "date_of_birth": "2008-01-01",
            "gender": "MALE",
            "department_id": infra["dept_id"],
            "program_id": infra["prog_id"],
            "admission_date": "2026-06-15",
        }

        res1 = await client.post("/api/v1/students", json=base_payload)
        assert res1.status_code == 201

        res2 = await client.post(
            "/api/v1/students",
            json={**base_payload, "first_name": "Student", "last_name": "Two"},
        )
        assert res2.status_code == 409
        body = res2.json()
        assert body["success"] is False
        assert body["error"]["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_duplicate_register_number_conflict():
    """Verify duplicate university register numbers trigger a 409 Conflict exception."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)
        shared_reg = f"3115{uuid.uuid4().hex[:8].upper()}"

        res1 = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-A-{uuid.uuid4().hex[:6].upper()}",
                "register_number": shared_reg,
                "first_name": "Alpha",
                "last_name": "User",
                "date_of_birth": "2008-02-02",
                "gender": "MALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        assert res1.status_code == 201

        res2 = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-B-{uuid.uuid4().hex[:6].upper()}",
                "register_number": shared_reg,
                "first_name": "Beta",
                "last_name": "User",
                "date_of_birth": "2008-03-03",
                "gender": "FEMALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        assert res2.status_code == 409
        assert res2.json()["error"]["code"] == "RESOURCE_CONFLICT"


# ==============================================================================
# 2. Retrieval, Search, and Filtering
# ==============================================================================

@pytest.mark.asyncio
async def test_get_student_and_not_found():
    """Verify single student retrieval and 404 behavior."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)
        adm_no = f"ADM-GET-{uuid.uuid4().hex[:6].upper()}"

        create_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": adm_no,
                "first_name": "Deepak",
                "last_name": "Sundaram",
                "date_of_birth": "2008-04-10",
                "gender": "MALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        assert create_res.status_code == 201
        sid = create_res.json()["data"]["id"]

        get_res = await client.get(f"/api/v1/students/{sid}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["admission_number"] == adm_no

        # Unknown ID returns 404
        fake_id = str(uuid.uuid4())
        nf_res = await client.get(f"/api/v1/students/{fake_id}")
        assert nf_res.status_code == 404
        assert nf_res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_students_paginated_and_filters():
    """Verify paginated listing, department filtering, and text search."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)
        unique_token = uuid.uuid4().hex[:5]

        # Create two students with distinct names
        s1_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-{unique_token}-01",
                "first_name": f"Kavitha_{unique_token}",
                "last_name": "Natarajan",
                "date_of_birth": "2008-01-10",
                "gender": "FEMALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
                "student_status": "ADMITTED",
            },
        )
        assert s1_res.status_code == 201

        s2_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-{unique_token}-02",
                "first_name": f"Vikram_{unique_token}",
                "last_name": "Rathore",
                "date_of_birth": "2008-02-12",
                "gender": "MALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
                "student_status": "ACTIVE",
            },
        )
        assert s2_res.status_code == 201

        # Search by unique first name
        search_res = await client.get(f"/api/v1/students?search=Kavitha_{unique_token}")
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert len(search_data["data"]) == 1
        assert search_data["data"][0]["first_name"] == f"Kavitha_{unique_token}"

        # Filter by department
        dept_res = await client.get(f"/api/v1/students?department_id={infra['dept_id']}")
        assert dept_res.status_code == 200
        assert len(dept_res.json()["data"]) >= 2

        # Filter by status ACTIVE
        status_res = await client.get(
            f"/api/v1/students?department_id={infra['dept_id']}&student_status=ACTIVE"
        )
        assert status_res.status_code == 200
        active_list = status_res.json()["data"]
        for s in active_list:
            assert s["student_status"] == "ACTIVE"


# ==============================================================================
# 3. Profile Updates and Section Assignment
# ==============================================================================

@pytest.mark.asyncio
async def test_update_student_profile():
    """Verify partial updates to contact, address, and demographic info."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)

        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-UPD-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Suresh",
                "last_name": "Babu",
                "date_of_birth": "2008-07-20",
                "gender": "MALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        assert s_res.status_code == 201
        sid = s_res.json()["data"]["id"]

        # Update contact and emergency details
        patch_res = await client.patch(
            f"/api/v1/students/{sid}",
            json={
                "phone_number": "+91-9940123456",
                "current_address": "Flat 3A, Ocean Towers, OMR, Chennai",
                "blood_group": "O+",
                "emergency_contact_name": "Babu K",
                "emergency_contact_phone": "+91-9940123457",
            },
        )
        assert patch_res.status_code == 200
        updated = patch_res.json()["data"]
        assert updated["phone_number"] == "+91-9940123456"
        assert updated["blood_group"] == "O+"
        assert updated["emergency_contact_name"] == "Babu K"


@pytest.mark.asyncio
async def test_assign_batch_and_section():
    """Verify section allocation and roll number assignment."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)

        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-SEC-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Meena",
                "last_name": "Kumari",
                "date_of_birth": "2008-08-15",
                "gender": "FEMALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        sid = s_res.json()["data"]["id"]

        assign_res = await client.post(
            f"/api/v1/students/{sid}/assign-section",
            json={
                "batch_id": infra["batch_id"],
                "section_id": infra["sec_id"],
                "roll_number": "26CSE042",
                "reason": "Allocated to Section A by academic coordinator",
            },
        )
        assert assign_res.status_code == 200
        assigned = assign_res.json()["data"]
        assert assigned["batch_id"] == infra["batch_id"]
        assert assigned["section_id"] == infra["sec_id"]
        assert assigned["roll_number"] == "26CSE042"

        # Check dossier reflects lifecycle event
        dossier = (await client.get(f"/api/v1/students/{sid}/detail")).json()["data"]
        events = dossier["lifecycle_events"]
        assert any(e["event_type"] == "SECTION_ASSIGNED" for e in events)


# ==============================================================================
# 4. Lifecycle Transitions and Audit Events
# ==============================================================================

@pytest.mark.asyncio
async def test_student_lifecycle_status_transitions():
    """Verify valid status progression and rejection of invalid status."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)

        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-LC-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Naveen",
                "last_name": "Prasad",
                "date_of_birth": "2008-09-09",
                "gender": "MALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        sid = s_res.json()["data"]["id"]

        # 1. Transition ADMITTED -> ACTIVE
        act_res = await client.post(
            f"/api/v1/students/{sid}/status",
            json={"new_status": "ACTIVE", "reason": "Completed fee payment and registration"},
        )
        assert act_res.status_code == 200
        assert act_res.json()["data"]["student_status"] == "ACTIVE"

        # 2. Transition ACTIVE -> ON_LEAVE
        leave_res = await client.post(
            f"/api/v1/students/{sid}/status",
            json={"new_status": "ON_LEAVE", "reason": "Medical leave approved for 1 semester"},
        )
        assert leave_res.status_code == 200
        assert leave_res.json()["data"]["student_status"] == "ON_LEAVE"

        # 3. Transition ON_LEAVE -> ACTIVE
        reinstate_res = await client.post(
            f"/api/v1/students/{sid}/status",
            json={"new_status": "ACTIVE", "reason": "Returned from medical leave"},
        )
        assert reinstate_res.status_code == 200
        assert reinstate_res.json()["data"]["student_status"] == "ACTIVE"

        # 4. Attempt invalid status
        bad_res = await client.post(
            f"/api/v1/students/{sid}/status",
            json={"new_status": "EXPELLED_PERMANENTLY", "reason": "Invalid test status"},
        )
        assert bad_res.status_code == 400
        assert bad_res.json()["error"]["code"] == "BAD_REQUEST"

        # 5. Check lifecycle audit history
        dossier = (await client.get(f"/api/v1/students/{sid}/detail")).json()["data"]
        events = dossier["lifecycle_events"]
        status_events = [e for e in events if e["event_type"] == "STATUS_CHANGE"]
        assert len(status_events) == 3


# ==============================================================================
# 5. Academic Records and Semester Enrollments
# ==============================================================================

@pytest.mark.asyncio
async def test_add_academic_record_and_enrollment_progression():
    """Verify recording prior academic achievements and semester progression enrollments."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_academic_hierarchy(client)

        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-ENR-{uuid.uuid4().hex[:6].upper()}",
                "first_name": "Ananya",
                "last_name": "Ramesh",
                "date_of_birth": "2008-11-25",
                "gender": "FEMALE",
                "department_id": infra["dept_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        sid = s_res.json()["data"]["id"]

        # Add Academic Record
        rec_res = await client.post(
            f"/api/v1/students/{sid}/academic-records",
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
        assert rec_res.json()["data"]["qualification"] == "Higher Secondary (12th / HSC)"

        # Semester 1 Enrollment
        enr1_res = await client.post(
            f"/api/v1/students/{sid}/enrollments",
            json={
                "academic_year_id": infra["ay_id"],
                "semester_id": infra["sem1_id"],
                "program_id": infra["prog_id"],
                "batch_id": infra["batch_id"],
                "section_id": infra["sec_id"],
                "semester_number": 1,
                "enrollment_date": "2026-06-20",
                "enrollment_status": "ENROLLED",
            },
        )
        assert enr1_res.status_code == 201
        assert enr1_res.json()["data"]["semester_number"] == 1

        # Semester 2 Enrollment (advances current_semester to 2)
        enr2_res = await client.post(
            f"/api/v1/students/{sid}/enrollments",
            json={
                "academic_year_id": infra["ay_id"],
                "semester_id": infra["sem2_id"],
                "program_id": infra["prog_id"],
                "batch_id": infra["batch_id"],
                "section_id": infra["sec_id"],
                "semester_number": 2,
                "enrollment_date": "2026-12-05",
                "enrollment_status": "ENROLLED",
            },
        )
        assert enr2_res.status_code == 201

        # Verify student current_semester has advanced to 2
        student_check = (await client.get(f"/api/v1/students/{sid}")).json()["data"]
        assert student_check["current_semester"] == 2

        # Duplicate enrollment for semester 2 triggers conflict
        dup_enr = await client.post(
            f"/api/v1/students/{sid}/enrollments",
            json={
                "academic_year_id": infra["ay_id"],
                "semester_id": infra["sem2_id"],
                "program_id": infra["prog_id"],
                "semester_number": 2,
                "enrollment_date": "2026-12-05",
            },
        )
        assert dup_enr.status_code == 409
        assert dup_enr.json()["error"]["code"] == "RESOURCE_CONFLICT"


# ==============================================================================
# 6. Independence from Authentication Credentials
# ==============================================================================

def test_student_identity_distinct_from_credentials():
    """Verify Student entity does not contain authentication credentials or login logic."""
    from app.domains.students.models import Student

    student_columns = {c.name for c in Student.__table__.columns}

    # Strict architectural boundaries: credentials belong to User, not Student
    assert "password_hash" not in student_columns
    assert "password" not in student_columns
    assert "failed_login_attempts" not in student_columns
    assert "locked_until" not in student_columns
    assert "mfa_enabled" not in student_columns

    # Institutional identity identifiers must exist
    assert "admission_number" in student_columns
    assert "register_number" in student_columns
    assert "department_id" in student_columns
    assert "program_id" in student_columns
    assert "student_status" in student_columns
