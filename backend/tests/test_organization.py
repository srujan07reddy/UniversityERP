import uuid
import httpx
import pytest
from app.main import app


@pytest.mark.asyncio
async def test_create_and_get_university():
    """Verify university charter creation and retrieval."""
    univ_code = f"UNIV-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        create_res = await client.post(
            "/api/v1/organization/universities",
            json={
                "code": univ_code,
                "name": "Jeppiaar University",
                "legal_name": "Jeppiaar Educational Trust",
                "establishment_year": 2011,
                "website": "https://jeppiaaruniversity.ac.in",
                "contact_email": "registrar@jeppiaar.ac.in",
                "contact_phone": "+91-44-24502818",
                "address": "Jeppiaar Nagar, Rajiv Gandhi Salai, Chennai, Tamil Nadu 600119",
                "status": "active",
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()["data"]
        univ_id = data["id"]
        assert data["code"] == univ_code
        assert data["name"] == "Jeppiaar University"

        # Get by ID
        get_res = await client.get(f"/api/v1/organization/universities/{univ_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["id"] == univ_id


@pytest.mark.asyncio
async def test_duplicate_university_code_conflict():
    """Verify creating university with duplicate code returns 409 Conflict."""
    univ_code = f"DUP-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res1 = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "First Instance"},
        )
        assert res1.status_code == 201

        res2 = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Duplicate Instance"},
        )
        assert res2.status_code == 409
        body = res2.json()
        assert body["success"] is False
        assert body["error"]["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_school_and_department_hierarchy_and_tree():
    """Verify recursive parent-child hierarchy (University -> School -> Department)."""
    univ_code = f"TREE-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create University
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Hierarchy Test University"},
        )
        univ_id = u_res.json()["data"]["id"]

        # Create School (L3)
        school_code = f"SOE-{uuid.uuid4().hex[:4].upper()}"
        s_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": school_code,
                "name": "School of Engineering and Technology",
                "unit_type": "SCHOOL",
                "status": "active",
            },
        )
        assert s_res.status_code == 201
        school_id = s_res.json()["data"]["id"]

        # Create Department (L4 under School)
        dept_code = f"CSE-{uuid.uuid4().hex[:4].upper()}"
        d_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "parent_unit_id": school_id,
                "code": dept_code,
                "name": "Department of Computer Science and Engineering",
                "unit_type": "DEPARTMENT",
                "status": "active",
            },
        )
        assert d_res.status_code == 201
        dept_id = d_res.json()["data"]["id"]

        # Query tree
        tree_res = await client.get(f"/api/v1/organization/units/tree?university_id={univ_id}")
        assert tree_res.status_code == 200
        tree = tree_res.json()["data"]

        # Find School in root nodes
        school_node = next((n for n in tree if n["id"] == school_id), None)
        assert school_node is not None
        assert school_node["code"] == school_code
        assert len(school_node["children"]) == 1
        assert school_node["children"][0]["id"] == dept_id
        assert school_node["children"][0]["code"] == dept_code


@pytest.mark.asyncio
async def test_explicit_cross_unit_relationships():
    """Verify non-hierarchical matrix relationships (e.g. Functional Unit coordination)."""
    univ_code = f"REL-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create University
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Rel Test University"},
        )
        univ_id = u_res.json()["data"]["id"]

        # Create School
        s_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"SOE-{uuid.uuid4().hex[:4].upper()}",
                "name": "School of Engineering",
                "unit_type": "SCHOOL",
            },
        )
        school_id = s_res.json()["data"]["id"]

        # Create Independent Functional Unit (COE)
        coe_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"COE-{uuid.uuid4().hex[:4].upper()}",
                "name": "Controller of Examinations",
                "unit_type": "FUNCTIONAL_UNIT",
            },
        )
        coe_id = coe_res.json()["data"]["id"]

        # Establish coordination relationship
        rel_res = await client.post(
            "/api/v1/organization/relationships",
            json={
                "source_unit_id": coe_id,
                "target_unit_id": school_id,
                "relationship_type": "FUNCTIONAL_COORDINATION",
                "description": "Examination governance and QP moderation coordination",
                "status": "active",
            },
        )
        assert rel_res.status_code == 201

        # Query relationships for unit
        list_res = await client.get(f"/api/v1/organization/units/{coe_id}/relationships")
        assert list_res.status_code == 200
        rels = list_res.json()["data"]
        assert len(rels) >= 1
        assert rels[0]["relationship_type"] == "FUNCTIONAL_COORDINATION"


@pytest.mark.asyncio
async def test_academic_year_and_semesters():
    """Verify academic years and semester sessions management."""
    univ_code = f"AY-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "AY University"},
        )
        univ_id = u_res.json()["data"]["id"]

        # Create Academic Year
        ay_res = await client.post(
            "/api/v1/organization/academic-years",
            json={
                "university_id": univ_id,
                "year_name": "2026-2027",
                "start_date": "2026-07-01",
                "end_date": "2027-06-30",
                "is_current": True,
                "status": "active",
            },
        )
        assert ay_res.status_code == 201
        ay_id = ay_res.json()["data"]["id"]

        # Create Semester 1
        sem_res = await client.post(
            "/api/v1/organization/semesters",
            json={
                "academic_year_id": ay_id,
                "semester_number": 1,
                "semester_name": "Odd Semester 2026",
                "semester_type": "ODD",
                "start_date": "2026-07-15",
                "end_date": "2026-11-30",
                "is_current": True,
                "status": "active",
            },
        )
        assert sem_res.status_code == 201
        assert sem_res.json()["data"]["semester_number"] == 1

        # List semesters
        list_sem = await client.get(f"/api/v1/organization/academic-years/{ay_id}/semesters")
        assert list_sem.status_code == 200
        assert len(list_sem.json()["data"]) == 1


@pytest.mark.asyncio
async def test_program_and_specialization():
    """Verify academic degree program and discipline specialization."""
    univ_code = f"PROG-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Prog University"},
        )
        univ_id = u_res.json()["data"]["id"]

        d_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"DEPT-{uuid.uuid4().hex[:4].upper()}",
                "name": "Department of CS",
                "unit_type": "DEPARTMENT",
            },
        )
        dept_id = d_res.json()["data"]["id"]

        prog_code = f"BTECH-{uuid.uuid4().hex[:4].upper()}"
        prog_res = await client.post(
            "/api/v1/organization/programs",
            json={
                "department_id": dept_id,
                "program_code": prog_code,
                "program_name": "B.Tech Computer Science and Engineering",
                "program_type": "UNDERGRADUATE",
                "duration_years": 4,
                "total_semesters": 8,
                "degree_awarded": "B.Tech.",
                "status": "active",
            },
        )
        assert prog_res.status_code == 201
        prog_id = prog_res.json()["data"]["id"]

        # Create Specialization
        spec_res = await client.post(
            "/api/v1/organization/specializations",
            json={
                "program_id": prog_id,
                "specialization_code": "AI-ML",
                "specialization_name": "Artificial Intelligence & Machine Learning",
                "status": "active",
            },
        )
        assert spec_res.status_code == 201
        assert spec_res.json()["data"]["specialization_code"] == "AI-ML"


@pytest.mark.asyncio
async def test_course_catalog():
    """Verify course catalog registration and department listing."""
    univ_code = f"CRS-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Course University"},
        )
        univ_id = u_res.json()["data"]["id"]

        d_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"DEPT-{uuid.uuid4().hex[:4].upper()}",
                "name": "Dept of CS",
                "unit_type": "DEPARTMENT",
            },
        )
        dept_id = d_res.json()["data"]["id"]

        course_code = f"CS{uuid.uuid4().hex[:4].upper()}"
        c_res = await client.post(
            "/api/v1/organization/courses",
            json={
                "department_id": dept_id,
                "course_code": course_code,
                "course_name": "Data Structures and Algorithms",
                "course_type": "THEORY",
                "credits": 4,
                "lecture_hours": 3,
                "tutorial_hours": 1,
                "practical_hours": 0,
                "status": "active",
            },
        )
        assert c_res.status_code == 201
        course_id = c_res.json()["data"]["id"]

        get_res = await client.get(f"/api/v1/organization/courses/{course_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["course_code"] == course_code


@pytest.mark.asyncio
async def test_batches_and_sections():
    """Verify academic batches and section allocations."""
    univ_code = f"SEC-{uuid.uuid4().hex[:6].upper()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        u_res = await client.post(
            "/api/v1/organization/universities",
            json={"code": univ_code, "name": "Batch University"},
        )
        univ_id = u_res.json()["data"]["id"]

        d_res = await client.post(
            "/api/v1/organization/units",
            json={
                "university_id": univ_id,
                "code": f"DEPT-{uuid.uuid4().hex[:4].upper()}",
                "name": "Department of CS",
                "unit_type": "DEPARTMENT",
            },
        )
        dept_id = d_res.json()["data"]["id"]

        prog_res = await client.post(
            "/api/v1/organization/programs",
            json={
                "department_id": dept_id,
                "program_code": f"BTECH-{uuid.uuid4().hex[:4].upper()}",
                "program_name": "B.Tech CSE",
                "program_type": "UNDERGRADUATE",
            },
        )
        prog_id = prog_res.json()["data"]["id"]

        # Create Batch
        batch_res = await client.post(
            "/api/v1/organization/batches",
            json={
                "program_id": prog_id,
                "batch_name": "2023-2027",
                "admission_year": 2023,
                "graduation_year": 2027,
                "current_semester_number": 1,
                "status": "active",
            },
        )
        assert batch_res.status_code == 201
        batch_id = batch_res.json()["data"]["id"]

        # Create Section
        sec_res = await client.post(
            "/api/v1/organization/sections",
            json={
                "batch_id": batch_id,
                "program_id": prog_id,
                "section_name": "A",
                "capacity": 60,
                "status": "active",
            },
        )
        assert sec_res.status_code == 201
        assert sec_res.json()["data"]["section_name"] == "A"

        # List sections for batch
        sec_list = await client.get(f"/api/v1/organization/batches/{batch_id}/sections")
        assert sec_list.status_code == 200
        assert len(sec_list.json()["data"]) == 1

