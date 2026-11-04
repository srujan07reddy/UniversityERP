import uuid
import httpx
import pytest
from app.main import app


async def setup_test_org_environment(client: httpx.AsyncClient):
    """Helper to set up University and Departments for relationship testing."""
    suffix = uuid.uuid4().hex[:6].upper()

    u_res = await client.post(
        "/api/v1/organization/universities",
        json={"code": f"UNIV-REL-{suffix}", "name": f"Relationship University {suffix}"},
    )
    assert u_res.status_code == 201
    univ_id = u_res.json()["data"]["id"]

    # Dept 1: Computer Science
    d1_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"DEPT-CSE-{suffix}",
            "name": f"Department of CSE {suffix}",
            "unit_type": "DEPARTMENT",
        },
    )
    assert d1_res.status_code == 201
    dept1_id = d1_res.json()["data"]["id"]

    # Dept 2: Centre for Artificial Intelligence
    d2_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"CENTRE-AI-{suffix}",
            "name": f"Centre for AI {suffix}",
            "unit_type": "FUNCTIONAL_UNIT",
        },
    )
    assert d2_res.status_code == 201
    dept2_id = d2_res.json()["data"]["id"]

    # Dept 3: Examination Cell
    d3_res = await client.post(
        "/api/v1/organization/units",
        json={
            "university_id": univ_id,
            "code": f"COE-{suffix}",
            "name": f"Office of COE {suffix}",
            "unit_type": "ADMINISTRATIVE_UNIT",
        },
    )
    assert d3_res.status_code == 201
    dept3_id = d3_res.json()["data"]["id"]

    # Program
    p_res = await client.post(
        "/api/v1/organization/programs",
        json={
            "department_id": dept1_id,
            "program_code": f"BE-CSE-{suffix}",
            "program_name": "B.E. Computer Science and Engineering",
            "program_type": "UNDERGRADUATE",
        },
    )
    assert p_res.status_code == 201
    prog_id = p_res.json()["data"]["id"]

    return {
        "univ_id": univ_id,
        "dept1_id": dept1_id,
        "dept2_id": dept2_id,
        "dept3_id": dept3_id,
        "prog_id": prog_id,
    }


# ==============================================================================
# 1. User <-> Student Linkage & Unlinking
# ==============================================================================

@pytest.mark.asyncio
async def test_user_and_student_linkage():
    """Verify linking a User account to a Student record and querying identity footprint."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        # 1. Create User
        u_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"student_{token}",
                "email": f"student_{token}@jeppiaar.ac.in",
                "password": "StrongPassword123!",
                "user_type": "STUDENT",
            },
            params={"auto_activate": True},
        )
        assert u_res.status_code == 201
        user_id = u_res.json()["data"]["id"]

        # 2. Create Student
        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-REL-{token.upper()}",
                "first_name": "Rajesh",
                "last_name": "Kannan",
                "date_of_birth": "2008-03-21",
                "gender": "MALE",
                "department_id": infra["dept1_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        assert s_res.status_code == 201
        student_id = s_res.json()["data"]["id"]

        # 3. Link User and Student
        link_res = await client.post(
            "/api/v1/identity/relationships/link-student",
            json={
                "user_id": user_id,
                "student_id": student_id,
                "reason": "Portal account provisioned for student",
            },
        )
        assert link_res.status_code == 200
        assert link_res.json()["data"]["user_id"] == user_id

        # 4. Check Identity Footprint
        fp_res = await client.get(f"/api/v1/identity/relationships/footprint/{user_id}")
        assert fp_res.status_code == 200
        fp = fp_res.json()["data"]
        assert fp["linked_student"] is not None
        assert fp["linked_student"]["id"] == student_id
        assert fp["linked_student"]["admission_number"] == f"ADM-REL-{token.upper()}"


@pytest.mark.asyncio
async def test_user_student_double_link_conflict():
    """Verify double-linking either user or student returns 409 Conflict."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        # User 1 & Student 1
        u1_res = await client.post(
            "/api/v1/identity/users",
            json={"username": f"u1_{token}", "email": f"u1_{token}@test.ac.in", "password": "Password123!"},
            params={"auto_activate": True},
        )
        u1_id = u1_res.json()["data"]["id"]

        s1_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-1-{token.upper()}",
                "first_name": "First",
                "last_name": "Student",
                "date_of_birth": "2008-01-01",
                "gender": "MALE",
                "department_id": infra["dept1_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        s1_id = s1_res.json()["data"]["id"]

        # Link U1 -> S1
        await client.post(
            "/api/v1/identity/relationships/link-student",
            json={"user_id": u1_id, "student_id": s1_id},
        )

        # Student 2
        s2_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-2-{token.upper()}",
                "first_name": "Second",
                "last_name": "Student",
                "date_of_birth": "2008-02-02",
                "gender": "FEMALE",
                "department_id": infra["dept1_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        s2_id = s2_res.json()["data"]["id"]

        # Attempt to link U1 to S2 -> Conflict (User already linked)
        conflict1 = await client.post(
            "/api/v1/identity/relationships/link-student",
            json={"user_id": u1_id, "student_id": s2_id},
        )
        assert conflict1.status_code == 409

        # User 2
        u2_res = await client.post(
            "/api/v1/identity/users",
            json={"username": f"u2_{token}", "email": f"u2_{token}@test.ac.in", "password": "Password123!"},
            params={"auto_activate": True},
        )
        u2_id = u2_res.json()["data"]["id"]

        # Attempt to link U2 to S1 -> Conflict (Student already linked)
        conflict2 = await client.post(
            "/api/v1/identity/relationships/link-student",
            json={"user_id": u2_id, "student_id": s1_id},
        )
        assert conflict2.status_code == 409


@pytest.mark.asyncio
async def test_user_and_student_unlinking():
    """Verify unlinking a user from a student record."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        u_res = await client.post(
            "/api/v1/identity/users",
            json={"username": f"unl_{token}", "email": f"unl_{token}@test.ac.in", "password": "Password123!"},
            params={"auto_activate": True},
        )
        user_id = u_res.json()["data"]["id"]

        s_res = await client.post(
            "/api/v1/students",
            json={
                "admission_number": f"ADM-UNL-{token.upper()}",
                "first_name": "Unlink",
                "last_name": "Test",
                "date_of_birth": "2008-05-05",
                "gender": "MALE",
                "department_id": infra["dept1_id"],
                "program_id": infra["prog_id"],
                "admission_date": "2026-06-15",
            },
        )
        student_id = s_res.json()["data"]["id"]

        await client.post(
            "/api/v1/identity/relationships/link-student",
            json={"user_id": user_id, "student_id": student_id},
        )

        # Unlink
        unl_res = await client.delete(f"/api/v1/identity/relationships/unlink-student/{student_id}")
        assert unl_res.status_code == 200
        assert unl_res.json()["data"]["user_id"] is None

        # Repeat unlink when not linked -> 400 Bad Request
        repeat = await client.delete(f"/api/v1/identity/relationships/unlink-student/{student_id}")
        assert repeat.status_code == 400


# ==============================================================================
# 2. User <-> Staff Linkage & Unlinking
# ==============================================================================

@pytest.mark.asyncio
async def test_user_and_staff_linkage_and_unlinking():
    """Verify linking and unlinking a User account with a Staff record."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        u_res = await client.post(
            "/api/v1/identity/users",
            json={
                "username": f"fac_{token}",
                "email": f"fac_{token}@jeppiaar.ac.in",
                "password": "FacultyPass123!",
                "user_type": "FACULTY",
            },
            params={"auto_activate": True},
        )
        assert u_res.status_code == 201
        user_id = u_res.json()["data"]["id"]

        stf_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"FAC-LNK-{token.upper()}",
                "first_name": "Dr. Subha",
                "last_name": "Ganesan",
                "date_of_birth": "1982-04-18",
                "gender": "FEMALE",
                "staff_type": "TEACHING",
                "designation": "Associate Professor",
                "department_id": infra["dept1_id"],
                "date_of_joining": "2026-06-01",
            },
        )
        assert stf_res.status_code == 201
        staff_id = stf_res.json()["data"]["id"]

        # Link User and Staff
        link_res = await client.post(
            "/api/v1/identity/relationships/link-staff",
            json={"user_id": user_id, "staff_id": staff_id, "reason": "Institutional SSO credentials issued"},
        )
        assert link_res.status_code == 200
        assert link_res.json()["data"]["user_id"] == user_id

        # Verify Footprint contains linked staff
        fp_res = await client.get(f"/api/v1/identity/relationships/footprint/{user_id}")
        assert fp_res.status_code == 200
        fp = fp_res.json()["data"]
        assert fp["linked_staff"] is not None
        assert fp["linked_staff"]["id"] == staff_id
        assert fp["linked_staff"]["designation"] == "Associate Professor"

        # Unlink User and Staff
        unl_res = await client.delete(f"/api/v1/identity/relationships/unlink-staff/{staff_id}")
        assert unl_res.status_code == 200
        assert unl_res.json()["data"]["user_id"] is None


# ==============================================================================
# 3. User Organization Memberships (Multi-organizational Affiliations)
# ==============================================================================

@pytest.mark.asyncio
async def test_multiple_user_organization_memberships():
    """Verify user can hold multiple concurrent organizational unit memberships."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        u_res = await client.post(
            "/api/v1/identity/users",
            json={"username": f"multi_{token}", "email": f"multi_{token}@test.ac.in", "password": "Password123!"},
            params={"auto_activate": True},
        )
        user_id = u_res.json()["data"]["id"]

        # 1. Primary Membership in Department of CSE
        m1 = await client.post(
            f"/api/v1/identity/relationships/memberships/user/{user_id}",
            json={
                "unit_id": infra["dept1_id"],
                "membership_type": "PRIMARY",
                "is_primary": True,
                "effective_from": "2026-06-01",
                "status": "ACTIVE",
            },
        )
        assert m1.status_code == 201
        assert m1.json()["data"]["is_primary"] is True

        # 2. Affiliate Membership in Centre for AI
        m2 = await client.post(
            f"/api/v1/identity/relationships/memberships/user/{user_id}",
            json={
                "unit_id": infra["dept2_id"],
                "membership_type": "AFFILIATE",
                "is_primary": False,
                "effective_from": "2026-07-01",
                "status": "ACTIVE",
                "notes": "Affiliated AI Researcher",
            },
        )
        assert m2.status_code == 201
        m2_id = m2.json()["data"]["id"]

        # 3. Committee Membership in COE Office
        m3 = await client.post(
            f"/api/v1/identity/relationships/memberships/user/{user_id}",
            json={
                "unit_id": infra["dept3_id"],
                "membership_type": "COMMITTEE_MEMBER",
                "is_primary": False,
                "effective_from": "2026-08-01",
                "status": "ACTIVE",
                "notes": "Chief Examination Superintendent",
            },
        )
        assert m3.status_code == 201

        # List all memberships
        list_res = await client.get(f"/api/v1/identity/relationships/memberships/user/{user_id}")
        assert list_res.status_code == 200
        memberships = list_res.json()["data"]
        assert len(memberships) == 3

        # Revoke Affiliate membership
        del_res = await client.delete(f"/api/v1/identity/relationships/memberships/{m2_id}")
        assert del_res.status_code == 200

        # Verify list now has 2
        after_del = await client.get(f"/api/v1/identity/relationships/memberships/user/{user_id}")
        assert len(after_del.json()["data"]) == 2


@pytest.mark.asyncio
async def test_duplicate_membership_conflict():
    """Verify duplicate membership of same type in same unit triggers 409 Conflict."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        u_res = await client.post(
            "/api/v1/identity/users",
            json={"username": f"dup_{token}", "email": f"dup_{token}@test.ac.in", "password": "Password123!"},
            params={"auto_activate": True},
        )
        user_id = u_res.json()["data"]["id"]

        payload = {
            "unit_id": infra["dept1_id"],
            "membership_type": "MEMBER",
            "is_primary": False,
            "effective_from": "2026-06-01",
        }

        res1 = await client.post(f"/api/v1/identity/relationships/memberships/user/{user_id}", json=payload)
        assert res1.status_code == 201

        res2 = await client.post(f"/api/v1/identity/relationships/memberships/user/{user_id}", json=payload)
        assert res2.status_code == 409
        assert res2.json()["error"]["code"] == "RESOURCE_CONFLICT"


# ==============================================================================
# 4. Staff Department Affiliations (Secondary & Joint Appointments)
# ==============================================================================

@pytest.mark.asyncio
async def test_staff_department_affiliations():
    """Verify faculty holding primary department appointment with secondary/joint affiliations."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        infra = await setup_test_org_environment(client)
        token = uuid.uuid4().hex[:6]

        # Staff in CSE primary department
        stf_res = await client.post(
            "/api/v1/staff",
            json={
                "staff_id": f"FAC-AFF-{token.upper()}",
                "first_name": "Dr. Meenakshi",
                "last_name": "Sundaram",
                "date_of_birth": "1979-09-14",
                "gender": "FEMALE",
                "staff_type": "TEACHING",
                "designation": "Professor",
                "department_id": infra["dept1_id"],  # Primary: CSE
                "date_of_joining": "2026-06-01",
            },
        )
        staff_id = stf_res.json()["data"]["id"]

        # Add Secondary Affiliation with Centre for AI
        aff1_res = await client.post(
            f"/api/v1/staff/{staff_id}/affiliations",
            json={
                "department_id": infra["dept2_id"],
                "affiliation_type": "SECONDARY",
                "role_title": "Honorary Research Director",
                "start_date": "2026-07-01",
                "remarks": "Multidisciplinary AI lab head",
            },
        )
        assert aff1_res.status_code == 201
        aff1_id = aff1_res.json()["data"]["id"]

        # Add Administrative Assignment in COE Office
        aff2_res = await client.post(
            f"/api/v1/staff/{staff_id}/affiliations",
            json={
                "department_id": infra["dept3_id"],
                "affiliation_type": "ADMINISTRATIVE_ASSIGNMENT",
                "role_title": "Additional Controller of Examinations",
                "start_date": "2026-08-01",
            },
        )
        assert aff2_res.status_code == 201

        # List affiliations
        list_res = await client.get(f"/api/v1/staff/{staff_id}/affiliations")
        assert list_res.status_code == 200
        affs = list_res.json()["data"]
        assert len(affs) == 2

        # Check in staff detail dossier
        dossier = (await client.get(f"/api/v1/staff/{staff_id}/detail")).json()["data"]
        assert len(dossier["lifecycle_events"]) >= 3  # APPOINTMENT + 2 AFFILIATIONS

        # Remove an affiliation
        del_res = await client.delete(f"/api/v1/staff/affiliations/{aff1_id}")
        assert del_res.status_code == 200

        # Verify list now has 1
        after_del = await client.get(f"/api/v1/staff/{staff_id}/affiliations")
        assert len(after_del.json()["data"]) == 1

