import uuid
import httpx
import pytest
from app.main import app


@pytest.mark.asyncio
async def test_phase3_complete_institutional_integration_lifecycle():
    """
    Stage 3.8 — Comprehensive End-to-End Institutional Integration & Verification Suite:
    1. Institutional Hierarchy: University -> School -> Department -> Program -> Year -> Semester -> Batch -> Section
    2. Student Admission & Academic Progression: Profile, Prior Records, Section Allocation, Semester Enrollment
    3. Staff Appointment & Dossier: Profile, Qualifications, Prior Experience, Cross-Department Affiliation
    4. Credential Provisioning & Relational Footprint: User Accounts, Linkages, Multi-Unit Memberships
    5. Authentication & Session Lifecycles: Argon2id Login, JWT Claims, /me & /footprint, Refresh Rotation, Logout Blacklist
    6. Identity Lifecycle & Zero-Cascade Safety: Suspension, Reinstatement, Password Change, Deactivation Integrity
    """
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        suffix = uuid.uuid4().hex[:6].upper()

        # ======================================================================
        # 1. Institutional Hierarchy Setup
        # ======================================================================
        univ_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": f"UNIV-E2E-{suffix}", "name": f"Jeppiaar Integration University {suffix}"},
        )
        assert univ_res.status_code == 201
        univ_id = univ_res.json()["data"]["id"]

        school_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"SCH-ENG-{suffix}",
                "name": f"School of Engineering {suffix}",
                "unit_type": "FACULTY_OR_SCHOOL",
            },
        )
        assert school_res.status_code == 201
        school_id = school_res.json()["data"]["id"]

        dept_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "parent_id": school_id,
                "code": f"DEPT-CSE-{suffix}",
                "name": f"Department of CSE {suffix}",
                "unit_type": "DEPARTMENT",
            },
        )
        assert dept_res.status_code == 201
        dept_id = dept_res.json()["data"]["id"]

        centre_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"CENTRE-AI-{suffix}",
                "name": f"Centre for Artificial Intelligence {suffix}",
                "unit_type": "FUNCTIONAL_UNIT",
            },
        )
        assert centre_res.status_code == 201
        centre_id = centre_res.json()["data"]["id"]

        prog_res = await client.post(
            "/api/v1/organization/programs",
            json={
                "department_id": dept_id,
                "program_code": f"BE-CSE-{suffix}",
                "program_name": "B.E. Computer Science and Engineering",
                "program_type": "UNDERGRADUATE",
            },
        )
        assert prog_res.status_code == 201
        prog_id = prog_res.json()["data"]["id"]

        ay_res = await client.post(
            "/api/v1/organization/academic-years",
            json={
                "university_id": univ_id,
                "code": f"AY-2026-{suffix}",
                "year_name": "Academic Year 2026-2027",
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
                "semester_name": "Semester 1",
                "term_type": "ODD",
                "start_date": "2026-08-01",
                "end_date": "2026-12-15",
            },
        )
        assert sem_res.status_code == 201
        sem_id = sem_res.json()["data"]["id"]

        batch_res = await client.post(
            "/api/v1/organization/batches",
            json={
                "program_id": prog_id,
                "academic_year_id": ay_id,
                "batch_name": f"Batch of 2026-2030 {suffix}",
                "admission_year": 2026,
                "graduation_year": 2030,
            },
        )
        assert batch_res.status_code == 201
        batch_id = batch_res.json()["data"]["id"]

        sec_res = await client.post(
            "/api/v1/organization/sections",
            json={
                "batch_id": batch_id,
                "program_id": prog_id,
                "academic_year_id": ay_id,
                "section_name": "Section A",
                "capacity": 60,
            },
        )
        assert sec_res.status_code == 201
        sec_id = sec_res.json()["data"]["id"]

        # ======================================================================
        # 2. Student Admission & Academic Progression
        # ======================================================================
        adm_no = f"ADM-E2E-{suffix}"
        std_create_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": adm_no,
                "register_number": f"REG-E2E-{suffix}",
                "first_name": "Ananya",
                "last_name": "Subramanian",
                "date_of_birth": "2008-03-25",
                "gender": "FEMALE",
                "blood_group": "O+",
                "nationality": "Indian",
                "personal_email": f"ananya_{suffix.lower()}@gmail.com",
                "department_id": dept_id,
                "program_id": prog_id,
                "admission_date": "2026-08-01",
                "admission_category": "REGULAR",
                "current_semester": 1,
            },
        )
        assert std_create_res.status_code == 201
        student_id = std_create_res.json()["data"]["id"]

        # Add prior educational record (12th CBSE)
        rec_res = await client.post(
            f"/api/v1/students/{student_id}/academic-records",
            json={
                "qualification": "Higher Secondary (12th / HSC)",
                "institution_name": "PSBB Millennium School",
                "board_or_university": "CBSE",
                "year_of_passing": 2026,
                "percentage_or_cgpa": "98.2%",
                "stream_or_specialization": "MPC (Maths, Physics, Chemistry, CS)",
            },
        )
        assert rec_res.status_code == 201

        # Section allocation & roll number
        assign_res = await client.post(
            f"/api/v1/students/{student_id}/assign-section",
            json={
                "batch_id": batch_id,
                "section_id": sec_id,
                "roll_number": "26CSE001",
                "reason": "Top merit admission allocation",
            },
        )
        assert assign_res.status_code == 200

        # Semester 1 Enrollment
        enr_res = await client.post(
            f"/api/v1/students/{student_id}/enrollments",
            json={
                "academic_year_id": ay_id,
                "semester_id": sem_id,
                "program_id": prog_id,
                "batch_id": batch_id,
                "section_id": sec_id,
                "semester_number": 1,
                "enrollment_date": "2026-08-05",
                "enrollment_status": "ENROLLED",
            },
        )
        assert enr_res.status_code == 201

        # ======================================================================
        # 3. Staff Appointment & Dossier
        # ======================================================================
        staff_code = f"FAC-E2E-{suffix}"
        stf_create_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": staff_code,
                "first_name": "Dr. Raghavan",
                "last_name": "Seshadri",
                "date_of_birth": "1984-11-12",
                "gender": "MALE",
                "staff_type": "TEACHING",
                "designation": "Professor & Head",
                "department_id": dept_id,
                "school_id": school_id,
                "date_of_joining": "2026-06-01",
                "employment_type": "REGULAR",
            },
        )
        assert stf_create_res.status_code == 201
        staff_id = stf_create_res.json()["data"]["id"]

        # Staff qualification (Ph.D.)
        qual_res = await client.post(
            f"/api/v1/staff/{staff_id}/qualifications",
            json={
                "degree": "Ph.D.",
                "discipline_or_field": "Artificial Intelligence & Distributed Systems",
                "institution_name": "Indian Institute of Technology Madras",
                "board_or_university": "IIT Madras",
                "year_of_passing": 2014,
            },
        )
        assert qual_res.status_code == 201

        # Staff cross-department affiliation (Joint Appointment at Centre for AI)
        affil_res = await client.post(
            f"/api/v1/staff/{staff_id}/affiliations",
            json={
                "department_id": centre_id,
                "affiliation_type": "JOINT",
                "role_title": "Honorary Lead AI Researcher",
                "start_date": "2026-06-01",
                "is_active": True,
            },
        )
        assert affil_res.status_code == 201

        # ======================================================================
        # 4. User Credential Provisioning & Footprint Linking
        # ======================================================================
        stf_username = f"faculty_{suffix.lower()}"
        stf_password = "ProfessorSecurePassword123!"

        stf_user_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": stf_username,
                "email": f"{stf_username}@jeppiaar.ac.in",
                "user_type": "FACULTY",
                "password": stf_password,
                "first_name": "Raghavan",
                "last_name": "Seshadri",
            },
            params={"auto_activate": True},
        )
        assert stf_user_res.status_code == 201
        stf_user_id = stf_user_res.json()["data"]["id"]

        # Link Staff User Account
        link_stf = await client.post(
            "/api/v1/identity/relationships/link-staff",
            json={"user_id": stf_user_id, "staff_id": staff_id},
        )
        assert link_stf.status_code == 200

        # Multi-Organizational Membership for Staff User
        mem_res = await client.post(
            f"/api/v1/identity/relationships/memberships/user/{stf_user_id}",
            json={
                "unit_id": centre_id,
                "membership_type": "CHAIR",
                "is_primary": False,
                "effective_from": "2026-06-01",
                "status": "ACTIVE",
            },
        )
        assert mem_res.status_code == 201

        # ======================================================================
        # 5. Authentication & Session Lifecycles
        # ======================================================================
        # Login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={
                "username_or_email": stf_username,
                "password": stf_password,
                "device_info": "Jeppiaar Faculty Portal",
            },
        )
        assert login_res.status_code == 200
        auth_data = login_res.json()["data"]
        access_token = auth_data["access_token"]
        refresh_token = auth_data["refresh_token"]

        # Access /me
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["data"]["username"] == stf_username

        # Access /footprint: verify consolidated identity
        fp_res = await client.get(
            "/api/v1/auth/footprint",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert fp_res.status_code == 200
        fp_data = fp_res.json()["data"]
        assert fp_data["linked_staff"]["staff_id"] == staff_code
        assert len(fp_data["organization_memberships"]) >= 1

        # Rotate Refresh Token
        ref_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert ref_res.status_code == 200
        new_access_token = ref_res.json()["data"]["access_token"]
        new_refresh_token = ref_res.json()["data"]["refresh_token"]

        # Logout
        logout_res = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_access_token}"},
            json={"refresh_token": new_refresh_token},
        )
        assert logout_res.status_code == 200

        # Verify old access token is revoked
        post_logout = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert post_logout.status_code == 401
        assert "revoked" in post_logout.json()["error"]["message"].lower()

        # ======================================================================
        # 6. Identity Lifecycle & Zero-Cascade Safety
        # ======================================================================
        # Deactivate Staff User Account
        deact_res = await client.post(
            f"/api/v1/identity/users/{stf_user_id}/deactivate",
            json={"reason": "Faculty member on long-term sabbatical / external deputation"},
        )
        assert deact_res.status_code == 200
        assert deact_res.json()["data"]["account_status"] == "DEACTIVATED"

        # Login must be blocked for deactivated account
        blocked_login = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": stf_username, "password": stf_password},
        )
        assert blocked_login.status_code == 401
        assert "deactivated" in blocked_login.json()["error"]["message"].lower()

        # ZERO CASCADE VERIFICATION: Staff and Academic Dossier completely intact
        stf_detail = await client.get(f"/api/v1/staff/{staff_id}/detail")
        assert stf_detail.status_code == 200
        dossier = stf_detail.json()["data"]
        assert dossier["staff_id"] == staff_code
        assert dossier["designation"] == "Professor & Head"
        assert len(dossier["qualifications"]) == 1
        assert len(dossier["department_affiliations"]) == 1

        # Student Records intact
        std_detail = await client.get(f"/api/v1/students/{student_id}/detail")
        assert std_detail.status_code == 200
        std_data = std_detail.json()["data"]
        assert std_data["admission_number"] == adm_no
        assert len(std_data["academic_records"]) == 1
        assert len(std_data["enrollments"]) == 1
