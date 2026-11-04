# University ERP — Phase Development Status Matrix

**Project:** Jeppiaar University ERP  
**Document Version:** 1.0  
**Last Updated:** November 4, 2026  
**Overall Project Status:** In Active Development (Phase 1 Complete → Phase 2 Ready)  
**Architecture Baseline:** Modular Monolith (FastAPI + SQLAlchemy 2.x + Pydantic v2 + Alembic | React 19 + TypeScript + Tailwind CSS + Capacitor 7 Native Android APK | PostgreSQL 17 | Valkey 8 | Celery)

---

## 1. Executive Summary & Phase Matrix

The University ERP development lifecycle follows a disciplined 12-phase incremental delivery roadmap. Each phase strictly adheres to a 7-step execution process: **Objective → Architecture → Structure → Implementation → Testing → Documentation → Exit Criteria**.

### Master Status Matrix

| Phase | Phase Name | Status | Progress | Key Deliverables & Artifacts | Exit Criteria Verification |
|:---:|:---|:---:|:---:|:---|:---|
| **Phase 0** | **Development Preparation** | `COMPLETED` | 100% | 13 Master Architecture Docs, Frozen Tech Baseline, Modular Monolith Layout (8 Platform + 15 Domain modules scaffolded). | Architecture frozen; contracts scaffolded; no unresolved technology ambiguities. |
| **Phase 1** | **Infrastructure & Environment** | `COMPLETED` | 100% | `compose.yaml` (PostgreSQL 17, Valkey 8, FastAPI, Celery, Vite), `.env.example`, `.env`, Dockerfiles, Python venv, Node/pnpm toolchain, Capacitor 7 native Android platform (`frontend/android/`). | Container configurations validated; Python venv verified; frontend Vite build passing; Capacitor Android sync operational. |
| **Phase 2** | **Backend Foundation** | `COMPLETED` | 100% | Stages 2.1–2.8 complete: `core/config.py`, `core/logging.py`, `core/middleware.py`, `database/`, `schemas/response.py`, `repositories/base.py`, `services/base.py`, `alembic.ini`, `migrations/`, live PostgreSQL 17. | 60 automated regression tests passing (100%); modular API routing (/api/v1); pagination & envelopes active; structured logging & correlation tracing; bidirectional Alembic migrations; safe error masking; full E2E lifespan verified. |
| **Phase 3** | **Identity & Organization** | `COMPLETED` | 100% | Stages 3.1–3.8 complete: `platform/organization/`, `platform/identity/`, `domains/students/`, and `domains/staff/` (models, schemas, repositories, services, routers), Argon2id hashing, JWT access & refresh token lifecycle, token rotation & revocation blacklist, zero-cascade deactivation safety, Alembic migrations `66c51afc91e9`, `5fcf29116fc7`, `811b898f76be`, `22fcfab3fa69`, `2d7665a1a918`, & `3460f1d24165`, live PostgreSQL 17. | 118 automated regression tests passing (100%); complete institutional hierarchy, student admissions & academic history, staff appointments & dossiers, user credential linkages, multi-organizational memberships, joint affiliations, authentication, token rotation, blacklisting, account lifecycle, zero-cascade preservation, and full end-to-end integration verified. |
| **Phase 4** | **RBAC & Authorization** | `READY` | 0% | Role hierarchy, granular permissions, organizational scoping, role delegation, ABAC rules, separation of duties. | Centralized permission engine validates cross-department data isolation and role boundaries. |
| **Phase 5** | **Governance & Workflow Engine** | `PLANNED` | 0% | Multi-step approval state machine, SLA routing, audit event logging, in-app/push/email notifications. | Approval workflows execute end-to-end; immutable audit trails recorded for all state mutations. |
| **Phase 6** | **Frontend Foundation** | `PLANNED` | 0% | Design system tokens (Emerald/Gold), institutional layouts, navigation rails, TanStack Query API layer, mobile safe area responsive layouts. | Responsive web layout + native Android APK render portal skeleton cleanly with dark/light tokens. |
| **Phase 7** | **Core ERP Modules** | `PLANNED` | 0% | Academics, Students, Employees, Attendance, Examinations, Finance modules. | Core university operations (student lifecycle, course registration, grading, fee collection) fully functional. |
| **Phase 8** | **Advanced Institutional Modules** | `PLANNED` | 0% | Placements, IQAC compliance, Research grants, Mentorship & Wellbeing (isolated counselling), Operations (Hostel, Transport, Library). | Specialized school requirements, student support isolation, and campus facility management operational. |
| **Phase 9** | **Integration & Intelligence** | `PLANNED` | 0% | Analytics dashboards, executive KPI reporting, messaging engine, biometric device integrations. | Real-time reporting active; multi-channel communication pipelines operational. |
| **Phase 10** | **Security & Quality Assurance** | `PLANNED` | 0% | End-to-end test suites, load testing (10,000+ concurrent users), penetration testing, vulnerability scanning. | Zero critical/high vulnerabilities; 99.9% uptime test; latency < 200ms at p95 under standard load. |
| **Phase 11** | **Production Deployment** | `PLANNED` | 0% | Hardened production containers, TLS/HTTPS, automated daily backups, disaster recovery drills, CI/CD pipelines. | Production deployment running; monitoring/alerting active; verified automated backup restoration. |

---

## 2. Detailed Phase Breakdown

### Phase 0: Development Preparation
- **Status:** `COMPLETED (100%)`
- **Objective:** Establish the foundation of the ERP by finalizing all institutional requirements, system specifications, data boundaries, and software design principles.
- **Key Artifacts:**
  - System Architecture Specification (`Architecture.md`)
  - Institutional Organizational Structure (`organizational_structure.md`)
  - Role-Based Access Control Specification (`RBAC.MD`)
  - Database & Data Model Design (`Database_design.md`)
  - Security Architecture & Data Protection (`Security_architecture.md`)
  - Workflow & Approval State Machine Engine (`workflow_architecture.md`)
  - REST API Standards & OpenAPI Contracts (`API_Documentation.md`)
  - Frontend Student Portal & UI Architecture (`frontendplan.md`)
  - Infrastructure & Deployment Plan (`DEPLOYMENT.md`)
  - Roles & Responsibilities Matrix (`Role & Responsibilities.md`)
  - Frontend Aesthetic & UI Rules (`rules_for_frontend.MD`)
  - University Institutional Vision (`vision.MD`)
- **Scaffolded Modules:**
  - **8 Platform Modules:** `identity`, `access_control`, `organization`, `workflows`, `audit`, `notifications`, `documents`, `configuration`.
  - **15 Domain Modules:** `students`, `staff`, `admissions`, `academics`, `attendance`, `examinations`, `finance`, `placements`, `mentorship`, `wellbeing`, `communications`, `library`, `hostel`, `transport`, `research`.

---

### Phase 1: Infrastructure & Environment
- **Status:** `COMPLETED (100%)`
- **Objective:** Provision local containerized infrastructure, backend Python environment, and frontend build pipeline supporting both Web and native Android APK.
- **Key Artifacts:**
  - `compose.yaml`: Multi-container orchestration (PostgreSQL 17, Valkey 8, FastAPI, Celery Worker, Vite Frontend).
  - `.env.example` & `.env`: Canonical development environment configuration.
  - `backend/Dockerfile`: Multi-stage Python 3.12-slim build with system dependencies.
  - `frontend/Dockerfile`: Node 20 Alpine container with pnpm package manager.
  - `backend/.venv`: Python virtual environment with FastAPI 0.162, SQLAlchemy 2.1, Pydantic v2, Alembic, Psycopg, Celery, Redis, PyJWT, Bcrypt.
  - `frontend/`: React 19 + TypeScript + Vite + Tailwind CSS 3.4. Verified clean build (`tsc -b && vite build` in ~2.3s).
  - `frontend/capacitor.config.ts`: Capacitor 7 cross-platform native bridge (`in.ac.jeppiaaruniversity.erp`).
  - `frontend/android/`: Complete native Android Gradle project with build scripts (`pnpm build:apk`, `pnpm cap:sync`, `pnpm cap:open:android`).
  - `.vscode/settings.json` & `.vscode/extensions.json`: Tailwind CSS linting and syntax recognition.

---

### Phase 2: Backend Foundation
- **Status:** `COMPLETED (100% — All 8 Stages Verified)`
- **Objective:** Construct the runtime backbone of the FastAPI application—strongly typed configuration, database session lifecycle, base model entities, global exception handling, database migrations, structured logging with correlation tracing, and complete end-to-end verification.

#### Stage Breakdown & Status:
| Stage | Stage Name | Status | Automated Test Suite | Result |
|:---:|:---|:---:|:---|:---:|
| **2.1** | **FastAPI Application Bootstrap** | `COMPLETED` | `backend/tests/test_bootstrap.py` | 6 passed |
| **2.2** | **Configuration Management** | `COMPLETED` | `backend/tests/test_config.py` | 6 passed |
| **2.3** | **Database Integration** | `COMPLETED` | `backend/tests/test_database.py` | 9 passed |
| **2.4** | **Database Migrations (Alembic)** | `COMPLETED` | `backend/tests/test_migrations.py` | 5 passed |
| **2.5** | **API Architecture & Routing** | `COMPLETED` | `backend/tests/test_api_v1.py` | 6 passed |
| **2.6** | **Validation & Global Exceptions** | `COMPLETED` | `backend/tests/test_exceptions.py` | 10 passed |
| **2.7** | **Logging & Observability** | `COMPLETED` | `backend/tests/test_logging.py` | 13 passed |
| **2.8** | **Phase 2 Test Verification** | `COMPLETED` | `backend/tests/test_foundation_e2e.py` | 5 passed (60/60 full suite) |

#### Completed Stages Detail:

##### Stage 2.1: FastAPI Application Bootstrap (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/main.py`: FastAPI application factory with modern `@asynccontextmanager` startup/shutdown lifecycle, CORS middleware, latency tracking, root documentation redirect (`/` → `/docs`), and global `/health` probe.
  - `backend/app/api/v1/health.py`: Pydantic-validated health probe (`GET /api/v1/health`) returning timestamp, version, environment, API operational status, and database connectivity.
  - `backend/app/api/v1/router.py`: Centralized API v1 router mounting platform & domain sub-routers.
  - `backend/app/core/middleware.py`: Pure ASGI latency measurement (`X-Process-Time`) and distributed tracing (`X-Request-ID`).
  - `backend/app/core/logging.py`: Structured logging formatting timestamp, module, function name, and line numbers.
- **Repeatable Automated Regression Suite (`tests/test_bootstrap.py`):** 6 tests passing.

##### Stage 2.2: Configuration Management (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/core/config.py`: Centralized `Settings` powered by Pydantic Settings v2 reading `.env` and environment variables.
  - Case-sensitive environment variable mapping with `.env` precedence.
  - Robust CORS list parser handling comma-delimited strings and native array inputs.
  - Automatic `DATABASE_URL` assembly with `postgresql+asyncpg://` dialect enforcement.
  - LRU caching (`get_settings()`) ensuring singleton configuration access across the application lifecycle.
- **Repeatable Automated Regression Suite (`tests/test_config.py`):** 6 tests passing.

##### Stage 2.3: Database Integration (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/database/base.py`: SQLAlchemy 2.x `DeclarativeBase` with strict PostgreSQL constraint naming conventions (`ix`, `uq`, `ck`, `fk`, `pk`), automatic lowercase snake_case tablenames, `UUIDPrimaryKeyMixin` with UUIDv4 defaults, and `TimestampMixin` (`created_at`, `updated_at`).
  - `backend/app/database/session.py`: Asynchronous SQLAlchemy engine (`create_async_engine`) using `asyncpg` driver, connection pooling (`pool_size=10`, `max_overflow=20`), `NullPool` testing support, `async_sessionmaker`, and lifecycle functions (`check_database_connection()`, `close_database_connections()`).
  - `backend/app/database/dependencies.py`: Request-scoped `get_db` FastAPI dependency yielding isolated `AsyncSession` with automatic rollback on error and guaranteed closure.
  - `backend/app/db/`: Re-exports all database classes for backward compatibility.
  - Database health monitoring wired into application startup/shutdown and `/health` probes.
  - PostgreSQL 17 Alpine container (`erp_postgres`) provisioned and running on port `5434`.
- **Repeatable Automated Regression Suite (`tests/test_database.py`):** 9 tests passing.

##### Stage 2.4: Database Migration Architecture (`COMPLETED`)
- **Implemented Components:**
  - `backend/alembic.ini`: Configured with chronological timestamped revision naming (`YYYYMMDD_HHMM_<rev>_<slug>.py`), path separators, and dynamic database URL resolution.
  - `backend/migrations/env.py`: Async migration runner wiring `Base.metadata` to Alembic, dynamic settings injection, and `compare_type=True`, `compare_server_default=True`.
  - Initial baseline migration `20261104_0612_dd84e2e88e3b_initial_baseline.py` generated and applied.
  - Full bidirectional migration lifecycle (`upgrade head`, `downgrade base`, `downgrade -1`) verified.
- **Repeatable Automated Regression Suite (`tests/test_migrations.py`):** 5 tests passing.

##### Stage 2.5: API Architecture & Routing (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/schemas/response.py`: Standardized API response envelopes (`APIResponse[T]`, `PaginatedResponse[T]`, `PaginationParams`, `PaginationMetadata`, `MessageResponse`).
  - `backend/app/repositories/base.py`: Generic asynchronous repository (`BaseRepository`) abstracting data access and CRUD operations.
  - `backend/app/services/base.py`: Generic business service layer (`BaseService`) keeping business logic strictly outside route handlers.
  - `backend/app/api/v1/endpoints/system.py`: Modular endpoint implementing `/api/v1/system/info` and `/api/v1/system/modules` with pagination and correlation tracking.
  - `backend/app/api/v1/router.py`: Centralized registration of v1 routes.
- **Repeatable Automated Regression Suite (`tests/test_api_v1.py`):** 6 tests passing.

##### Stage 2.6: Validation & Exception Architecture (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/core/exceptions.py`: Application exception hierarchy (`BaseAppException`, `ValidationException`, `AuthenticationException`, `AuthorizationException`, `NotFoundException`, `ConflictException`, `BadRequestException`, `DatabaseException`).
  - `ErrorResponse` and `ErrorDetail` schemas conforming to institutional specification (`success=false`, `error.code`, `error.message`, `error.details`, `request_id`).
  - `setup_exception_handlers(app)`: Global handlers for `BaseAppException`, `RequestValidationError`, `StarletteHTTPException`, `IntegrityError`, `DBAPIError`, `SQLAlchemyError`, and uncaught 500 exceptions.
  - Safe error masking preventing leakage of stack traces, local paths, raw SQL queries, or internal database secrets.
- **Repeatable Automated Regression Suite (`tests/test_exceptions.py`):**
  1. `test_not_found_exception_envelope`: Asserts 404 with `RESOURCE_NOT_FOUND`.
  2. `test_authentication_exception_envelope`: Asserts 401 with `AUTHENTICATION_REQUIRED`.
  3. `test_authorization_exception_envelope`: Asserts 403 with `PERMISSION_DENIED`.
  4. `test_conflict_exception_envelope`: Asserts 409 with `RESOURCE_CONFLICT`.
  5. `test_bad_request_exception_envelope`: Asserts 400 with `BAD_REQUEST`.
  6. `test_database_integrity_error_safety`: Asserts 409 without leaking raw SQL query internals.
  7. `test_unhandled_crash_safe_masking`: Asserts 500 without leaking stack traces or internal secrets.
  8. `test_pydantic_validation_error_envelope`: Asserts 422 with structured field details.
  9. `test_starlette_404_routing_error`: Asserts route-not-found returns standardized error envelope.
  10. `test_request_id_in_error_envelope`: Asserts correlation id is preserved in error response and header.

##### Stage 2.7: Logging & Observability (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/core/logging.py`: Structured JSON logging (`JSONLogFormatter`) for production and readable console formatting (`ConsoleLogFormatter`) for development; `CorrelationIdFilter` extracting correlation IDs from contextvars; `SensitiveDataFilter` scrubbing passwords, Bearer tokens, credentials, credit card numbers, SSNs, and Aadhaar identifiers.
  - `backend/app/core/middleware.py`: Pure ASGI `RequestLoggingMiddleware` managing `correlation_id_ctx`, injecting `X-Request-ID` and `X-Process-Time` into response headers, and performing access logging.
  - `backend/app/core/config.py`: Environment-driven logging configuration (`LOG_LEVEL` and `LOG_FORMAT: "text" | "json" | "auto"`).
- **Repeatable Automated Regression Suite (`tests/test_logging.py`):** 13 tests passing:
  1. `test_correlation_id_context_lifecycle`: Contextvar isolation and lifecycle.
  2. `test_mask_sensitive_data_dictionary`: Redaction of sensitive dictionary keys.
  3. `test_mask_sensitive_data_bearer_token`: Redaction of Bearer tokens.
  4. `test_mask_sensitive_data_database_url`: Redaction of database credentials in connection URLs.
  5. `test_mask_sensitive_data_financial_and_pii`: Redaction of credit card numbers, SSNs, and Aadhaar numbers.
  6. `test_correlation_id_filter`: LogRecord enrichment with `request_id`.
  7. `test_sensitive_data_filter`: LogRecord message and argument sanitization.
  8. `test_json_log_formatter`: Structured JSON output with extra field redaction.
  9. `test_console_log_formatter`: Formatted human-readable output with request ID tags.
  10. `test_environment_dependent_setup_logging`: Dynamic configuration based on environment.
  11. `test_request_logging_middleware_tracing_headers`: Response header propagation.
  12. `test_custom_request_id_preserved_and_propagated`: Client-provided ID preservation.
  13. `test_generated_request_id_matches_envelope_without_client_header`: Header/body request ID parity.

##### Stage 2.8: Testing & Verification (`COMPLETED`)
- **Implemented Components:**
  - `backend/tests/test_foundation_e2e.py`: End-to-end integration tests verifying FastAPI lifespan, request correlation cycle, database session transaction integrity, validation pipelines, and live database Alembic schema stamping.
  - Complete backend test suite execution: **60/60 tests passing across 8 test suites** in 3.64 seconds with active foundation coverage exceeding 90%.
  - Phase 2 exit criteria formally audited and verified 100% complete.

---

### Phase 3: Identity & Organization
- **Status:** `IN PROGRESS (Stages 3.1 & 3.2 Complete — 25% Overall Phase Progress)`
- **Objective:** Establish the institutional identity layer—modeling who exists in the university, what organizational entity they belong to, and how their institutional identity is maintained (kept strictly separate from authorization/RBAC).

#### Stage Breakdown & Status:
| Stage | Stage Name | Status | Automated Test Suite | Result |
|:---:|:---|:---:|:---|:---:|
| **3.1** | **Institutional Organization Model** | `COMPLETED` | `backend/tests/test_organization.py` | 8 passed |
| **3.2** | **User Identity Management** | `COMPLETED` | `backend/tests/test_identity.py` | 10 passed |
| **3.3** | **Student Identity** | `COMPLETED` | `backend/tests/test_students.py` | 10 passed |
| **3.4** | **Staff Identity** | `COMPLETED` | `backend/tests/test_staff.py` | 10 passed |
| **3.5** | **Identity Relationships** | `COMPLETED` | `backend/tests/test_relationships.py` | 7 passed |
| **3.6** | **Identity Lifecycle** | `COMPLETED` | `backend/tests/test_lifecycle.py` | 4 passed |
| **3.7** | **Authentication Foundation** | `COMPLETED` | `backend/tests/test_auth.py` | 8 passed |
| **3.8** | **Integration & Verification** | `COMPLETED` | `backend/tests/test_phase3_e2e.py` | 1 passed (118/118 full suite) |

#### Completed Stages Detail:

##### Stage 3.1: Institutional Organization Model (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/platform/organization/models.py`: 10 SQLAlchemy 2.x declarative entities inheriting from `AuditBaseModel`:
    1. `University`: Apex institutional authority charter.
    2. `OrganizationalUnit`: Schools, Departments, Functional Units (COE, Finance, IQAC, Placement), and Administrative Units with recursive self-referential hierarchy.
    3. `OrganizationalRelationship`: Explicit non-hierarchical, matrix, and coordination relationships (`ADMINISTRATIVE_PARENT`, `FUNCTIONAL_COORDINATION`, `REPORTING_TO`, `ACADEMIC_COORDINATION`, `AFFILIATION`).
    4. `AcademicYear`: Multi-year containers with active/current tracking.
    5. `Semester`: Discrete academic sessions (`ODD`, `EVEN`, `SUMMER`).
    6. `AcademicProgram`: Degree curricula anchored to departments.
    7. `Specialization`: Disciplinary concentrations and minors.
    8. `Course`: Master course catalog with credits and contact hours.
    9. `AcademicBatch`: Student cohorts mapped to graduation years.
    10. `Section`: Operational classroom divisions.
  - `backend/app/platform/organization/schemas.py`: Comprehensive Pydantic v2 validation and response schemas.
  - `backend/app/platform/organization/repositories.py`: Dedicated asynchronous repositories extending `BaseRepository`.
  - `backend/app/platform/organization/services.py`: Domain service enforcing parent-child ownership, referential validation, and recursive tree generation (`get_organization_tree`).
  - `backend/app/platform/organization/router.py`: REST endpoints mounted under `/api/v1/organization`.
  - `backend/migrations/versions/20261104_0705_66c51afc91e9_create_institutional_organization_tables.py`: Alembic migration generated and applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_organization.py`):** 8 tests passing:
  1. `test_create_and_get_university`: Charter creation and retrieval.
  2. `test_duplicate_university_code_conflict`: 409 conflict safety.
  3. `test_school_and_department_hierarchy_and_tree`: Recursive tree generation.
  4. `test_explicit_cross_unit_relationships`: Non-hierarchical coordination mapping.
  5. `test_academic_year_and_semesters`: Academic calendar lifecycle.
  6. `test_program_and_specialization`: Degree and specialization registration.
  7. `test_course_catalog`: Course registration and department listing.
  8. `test_batches_and_sections`: Batch cohorts and section allocations.

##### Stage 3.2: User Identity Management (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/platform/identity/models.py`: 4 SQLAlchemy 2.x declarative entities:
    1. `User`: Central institutional identity with unique username, institutional email, phone, Argon2id password hash, account status (`PENDING_ACTIVATION`, `ACTIVE`, `SUSPENDED`, `DEACTIVATED`, `LOCKED`), and lockout markers.
    2. `UserProfile`: Personal and demographic records (first/last names, DOB, gender, blood group, avatar, full address, and emergency contact details).
    3. `UserRecoveryToken`: SHA-256 hashed cryptographic tokens for account activation, password reset, and MFA recovery.
    4. `UserLifecycleEvent`: Immutable audit log recording every identity transition with timestamps, actor IDs, reasons, and JSON metadata.
  - `backend/app/core/security.py`: Argon2id password hashing via `PasswordHasher` (OWASP recommended parameters: 64 MiB memory, 3 iterations, 4 parallelism), constant-time verification, cryptographic token generation (`secrets.token_urlsafe`), and SHA-256 digest hashing.
  - `backend/app/platform/identity/schemas.py`: Pydantic v2 schemas for registration, profile updates, password modification, status transitions, token activation, and lifecycle auditing.
  - `backend/app/platform/identity/repositories.py`: Asynchronous repositories (`UserRepository`, `UserProfileRepository`, `UserRecoveryTokenRepository`, `UserLifecycleEventRepository`).
  - `backend/app/platform/identity/services.py`: `UserIdentityService` implementing account creation, token activation, status updates, password changes, and password recovery workflows.
  - `backend/app/platform/identity/router.py`: REST endpoints mounted under `/api/v1/identity`.
  - `backend/migrations/versions/20261104_0715_5fcf29116fc7_create_user_identity_tables.py`: Alembic migration applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_identity.py`):** 10 tests passing:
  1. `test_argon2id_hashing_and_verification`: Argon2id hash generation and verification.
  2. `test_token_generation_and_hashing`: Cryptographic token entropy and digest hashing.
  3. `test_user_registration_argon2_hashing_and_pending_activation`: Registration, pending state, and profile linkage.
  4. `test_duplicate_username_and_email_prevention`: 409 conflict safety on unique fields.
  5. `test_account_activation_workflow`: One-time activation token consumption and reuse prevention.
  6. `test_user_profile_update`: Demographic and emergency contact profile updates.
  7. `test_account_lifecycle_status_transitions`: Suspension, deactivation, and reinstatement state transitions.
  8. `test_password_change_lifecycle`: Current password validation and Argon2id re-hashing.
  9. `test_password_reset_recovery_workflow`: Secure out-of-band recovery token workflow.
  10. `test_identity_lifecycle_audit_trail`: Immutable audit trail verification.

##### Stage 3.3: Student Identity (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/domains/students/models.py`: 4 SQLAlchemy 2.x declarative entities decoupled from authentication credentials:
    1. `Student`: Institutional student master entity with unique admission number, optional register number, roll number, demographic data (DOB, gender, blood group, nationality, community, religion), parent/guardian details, contact info, academic hierarchy linkages (department, program, batch, section), current semester, and student lifecycle status (`ADMITTED`, `ACTIVE`, `ON_LEAVE`, `SUSPENDED`, `DISCONTINUED`, `ALUMNI`, `WITHDRAWN`).
    2. `StudentAcademicRecord`: Prior educational records (10th, 12th/HSC, Diplomas) with institution, board, year of passing, and score/CGPA for admission verification.
    3. `StudentEnrollment`: Semester-by-semester academic enrollment history linking students to academic years, semesters, programs, batches, and sections.
    4. `StudentLifecycleEvent`: Immutable audit log capturing status transitions (`ADMISSION`, `STATUS_CHANGE`, `ENROLLMENT`, `SECTION_ASSIGNED`, etc.) with timestamps, reasons, and approving actors.
  - `backend/app/domains/students/schemas.py`: Pydantic v2 schemas for student registration, profile updates, status changes, section assignment, academic record creation, and semester enrollment.
  - `backend/app/domains/students/repositories.py`: Dedicated async repositories (`StudentRepository`, `StudentAcademicRecordRepository`, `StudentEnrollmentRepository`, `StudentLifecycleEventRepository`).
  - `backend/app/domains/students/services.py`: `StudentService` implementing admission validation, duplicate prevention, status transitions, batch/section assignment, academic history management, and semester progression.
  - `backend/app/domains/students/router.py`: REST endpoints mounted under `/api/v1/students`.
  - `backend/migrations/versions/20261104_0818_811b898f76be_create_student_identity_tables.py`: Alembic migration applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_students.py`):** 10 tests passing:
  1. `test_student_admission_and_profile_creation`: Admission, demographic persistence, initial academic history, and initial lifecycle event logging.
  2. `test_duplicate_admission_number_conflict`: 409 conflict safety on unique admission numbers.
  3. `test_duplicate_register_number_conflict`: 409 conflict safety on university register numbers.
  4. `test_get_student_and_not_found`: Profile summary retrieval and safe 404 behavior.
  5. `test_list_students_paginated_and_filters`: Paginated listing, department filtering, and text search across names and identifiers.
  6. `test_update_student_profile`: Partial profile updates (contact, address, emergency contact).
  7. `test_assign_batch_and_section`: Section assignment and roll number allocation.
  8. `test_student_lifecycle_status_transitions`: Status state machine progression and invalid state rejection.
  9. `test_add_academic_record_and_enrollment_progression`: Adding educational history and semester enrollment progression.
  10. `test_student_identity_distinct_from_credentials`: Verification that student identity remains strictly distinct from authentication credentials.

##### Stage 3.4: Staff Identity (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/domains/staff/models.py`: 4 SQLAlchemy 2.x declarative entities maintaining strict architectural separation between institutional designation and RBAC authorization roles:
    1. `Staff`: Institutional employment master entity with unique permanent `staff_id`, `biometric_id`, `institutional_email`, demographic data, contact info, employment type (`REGULAR`, `PROBATION`, `CONTRACT`, etc.), staff type (`TEACHING`, `NON_TEACHING`, `ADMINISTRATIVE`, `TECHNICAL`, etc.), designation (institutional title/rank), department and school associations, joining date, probation period, notice period, and employment status (`ACTIVE`, `PROBATION`, `ON_LEAVE`, `SUSPENDED`, `RESIGNED`, `RETIRED`, `TERMINATED`, `RELIEVED`).
    2. `StaffQualification`: Academic and professional credentials (Ph.D., M.Tech, NET/SLET, etc.) with institution, awarding university, year of passing, and certificates.
    3. `StaffExperience`: Previous teaching, industrial, research, or administrative employment records with roles and relieving details.
    4. `StaffLifecycleEvent`: Immutable audit log capturing all employment events (`APPOINTMENT`, `STATUS_CHANGE`, `DESIGNATION_CHANGE`, `DEPARTMENT_TRANSFER`, `PROBATION_CONFIRMATION`, `RELIEVED`, etc.) with reasons and approving actors.
  - `backend/app/domains/staff/schemas.py`: Pydantic v2 schemas for staff appointment, profile updates, status changes, promotion/redesignation, department transfer, qualification addition, and experience addition.
  - `backend/app/domains/staff/repositories.py`: Dedicated async repositories (`StaffRepository`, `StaffQualificationRepository`, `StaffExperienceRepository`, `StaffLifecycleEventRepository`).
  - `backend/app/domains/staff/services.py`: `StaffService` enforcing unique employee identifiers, biometric ID, and institutional email, handling appointment, promotion/redesignation, department transfer, qualification and experience archival, and employment status transitions.
  - `backend/app/domains/staff/router.py`: REST endpoints mounted under `/api/v1/staff`.
  - `backend/migrations/versions/20261104_0833_22fcfab3fa69_create_staff_identity_tables.py`: Alembic migration applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_staff.py`):** 10 tests passing:
  1. `test_staff_appointment_and_profile_creation`: Appointment, demographic and employment persistence, initial credentials, initial experience, and initial lifecycle logging.
  2. `test_duplicate_staff_id_and_email_conflicts`: 409 conflict safety on staff_id, biometric_id, and institutional email.
  3. `test_get_staff_and_not_found`: Profile summary retrieval and safe 404 behavior.
  4. `test_list_staff_paginated_and_filters`: Paginated listing, department/staff_type filtering, and text search across names and codes.
  5. `test_update_staff_profile`: Partial profile updates (contact, address, emergency contact).
  6. `test_staff_designation_update`: Promotion / redesignation workflow and audit event logging.
  7. `test_staff_department_transfer`: Department transfer order workflow and audit logging.
  8. `test_staff_lifecycle_status_transitions`: Status progression (PROBATION -> ACTIVE -> ON_LEAVE -> RELIEVED) and invalid state rejection.
  9. `test_add_qualifications_and_experience`: Adding educational degrees and industry experience post-appointment.
  10. `test_staff_designation_distinct_from_rbac_roles`: Verification that staff designation does not conflate with application RBAC roles or credentials.

##### Stage 3.5: Identity Relationships (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/platform/identity/models.py`:
    - `UserOrganizationMembership`: Explicit multi-membership association supporting concurrent memberships across academic schools, departments, research centres of excellence, and administrative wings (`PRIMARY`, `MEMBER`, `AFFILIATE`, `REPRESENTATIVE`, `CHAIR`, `COMMITTEE_MEMBER`).
    - Bidirectional SQLAlchemy 2.x relationships on `User`: `student` (`uselist=False`), `staff` (`uselist=False`), `organization_memberships` (`cascade="all, delete-orphan"`).
  - `backend/app/domains/students/models.py`: Added bidirectional `user` relationship on `Student`.
  - `backend/app/domains/staff/models.py`:
    - `StaffDepartmentAffiliation`: Association entity for secondary, joint, adjunct, and administrative appointments across departments alongside primary department.
    - Bidirectional SQLAlchemy 2.x relationships on `Staff`: `user` (`uselist=False`), `department_affiliations` (`cascade="all, delete-orphan"`).
  - `backend/app/platform/identity/schemas.py`: Schemas for `UserOrganizationMembershipCreate`, `UserOrganizationMembershipResponse`, `UserLinkStudentRequest`, `UserLinkStaffRequest`, `StaffDepartmentAffiliationCreate`, `StaffDepartmentAffiliationResponse`, and `IdentityFootprintResponse`.
  - `backend/app/platform/identity/services.py` & `backend/app/domains/staff/services.py`:
    - Business methods for student credential linkage & unlinking (`link_student`, `unlink_student`).
    - Business methods for staff credential linkage & unlinking (`link_staff`, `unlink_staff`).
    - Multi-membership provisioning and revocation (`add_organization_membership`, `remove_organization_membership`).
    - Secondary/joint department affiliation workflows (`add_department_affiliation`, `remove_department_affiliation`).
    - Unified identity footprint resolver (`get_identity_footprint`) consolidating user profile, linked student record, linked staff appointment, and all organizational memberships.
  - `backend/app/platform/identity/router.py` & `backend/app/domains/staff/router.py`:
    - `/api/v1/identity/relationships/link-student` & `/unlink-student/{student_id}`.
    - `/api/v1/identity/relationships/link-staff` & `/unlink-staff/{staff_id}`.
    - `/api/v1/identity/relationships/memberships/user/{user_id}` & `/memberships/{id}`.
    - `/api/v1/identity/relationships/footprint/{user_id}`.
    - `/api/v1/staff/{staff_id}/affiliations` & `/staff/affiliations/{id}`.
  - `backend/migrations/versions/20261104_0841_2d7665a1a918_create_identity_relationship_tables.py`: Alembic migration applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_relationships.py`):** 7 tests passing:
  1. `test_user_and_student_linkage`: Linking User to Student and footprint resolution.
  2. `test_user_student_double_link_conflict`: 409 conflict safety preventing duplicate user or student linkages.
  3. `test_user_and_student_unlinking`: Unlinking user and student records, and rejecting invalid unlinking.
  4. `test_user_and_staff_linkage_and_unlinking`: Full link and unlink lifecycle for staff records.
  5. `test_multiple_user_organization_memberships`: Concurrent memberships across departments and centres.
  6. `test_duplicate_membership_conflict`: 409 conflict safety preventing duplicate active memberships in the same unit.
  7. `test_staff_department_affiliations`: Secondary research affiliations and administrative appointments for staff.

##### Stage 3.6: Identity Lifecycle (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/platform/identity/models.py`:
    - `UserLifecycleEvent`: Model captures event type (`CREATED`, `ACTIVATED`, `SUSPENDED`, `REINSTATED`, `DEACTIVATED`, `LOCKED_OUT`, `UNLOCKED`, `PASSWORD_CHANGED`, `PASSWORD_RESET_REQUESTED`, `PROFILE_UPDATED`, `LINK_STUDENT`, `UNLINK_STUDENT`, `LINK_STAFF`, `UNLINK_STAFF`, `MEMBERSHIP_GRANTED`, `MEMBERSHIP_REVOKED`), actor ID, reason string, and JSON metadata.
    - Zero Cascade Safety: Foreign keys to `User` in `Student` and `Staff` tables enforce `ondelete="SET NULL"`. Account deactivation transitions user credentials to `DEACTIVATED` without cascading or deleting student academic records, enrollments, staff qualifications, or affiliations.
  - `backend/app/platform/identity/schemas.py`: `UserActionReasonRequest` schema for administrative actions (suspension, reinstatement, deactivation, unlocking).
  - `backend/app/platform/identity/repositories.py`: `UserLifecycleEventRepository.list_events` with pagination, event type filtering, user ID scoping, and date range filters (`from_date`, `to_date`).
  - `backend/app/platform/identity/services.py`:
    - `suspend_user`: Status transition to `SUSPENDED` with validation preventing duplicate suspension.
    - `reinstate_user`: Reinstatement back to `ACTIVE` from suspended, locked, or deactivated states.
    - `deactivate_user`: Graceful institutional deactivation stamping `deactivated_at`, preserving all associated academic and staff records intact.
    - `unlock_user`: Administrative lockout reset clearing `failed_login_attempts` and `locked_until`.
    - `update_profile`: Tracks updated field keys in lifecycle event metadata.
    - `list_lifecycle_events`: Paginated query across institutional audit log.
  - `backend/app/platform/identity/router.py`:
    - `POST /api/v1/identity/users/{user_id}/suspend`
    - `POST /api/v1/identity/users/{user_id}/reinstate`
    - `POST /api/v1/identity/users/{user_id}/deactivate`
    - `POST /api/v1/identity/users/{user_id}/unlock`
    - `GET /api/v1/identity/lifecycle/events` (paginated audit trail search)
- **Repeatable Automated Regression Suite (`tests/test_lifecycle.py`):** 4 tests passing:
  1. `test_user_status_transitions_lifecycle`: Verification of full status progression (`PENDING_ACTIVATION` → `ACTIVE` → `SUSPENDED` → `REINSTATED` → `LOCKED` → `UNLOCKED`) and lifecycle event logging.
  2. `test_deactivation_zero_cascade_safety`: Critical institutional verification confirming account deactivation leaves student admission data, prior academic records, enrollments, staff employee data, qualifications, and affiliations 100% intact.
  3. `test_profile_update_and_audit_event`: Verifying `PROFILE_UPDATED` event logging with metadata listing modified fields.
  4. `test_search_institutional_audit_trail`: Global audit log querying with pagination, user ID filtering, and event type filtering.

##### Stage 3.7: Authentication Foundation (`COMPLETED`)
- **Implemented Components:**
  - `backend/app/core/config.py`: Added JWT configuration (`JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES = 60`, `REFRESH_TOKEN_EXPIRE_DAYS = 7`, `jwt_secret` property).
  - `backend/app/core/security.py`:
    - `create_access_token`: Signed JWT token with claims (`sub`, `username`, `email`, `user_type`, `jti`, `iat`, `exp`, `type="access"`).
    - `create_refresh_token`: Extended signed JWT token with claims (`sub`, `jti`, `iat`, `exp`, `type="refresh"`).
    - `decode_jwt`: JWT signature and expiration verification with explicit `AuthenticationException` handling.
  - `backend/app/platform/identity/models.py`:
    - `UserRefreshToken`: Persisted refresh token sessions with SHA-256 token hashing, client device/IP tracking, and revocation state.
    - `RevokedToken`: Blacklisted token repository indexed by unique `jti` ensuring immediate access invalidation prior to expiration.
  - `backend/app/platform/identity/schemas.py`: `LoginRequest`, `TokenResponse`, `RefreshTokenRequest`, `LogoutRequest`, `TokenRevokeRequest`.
  - `backend/app/platform/identity/repositories.py`:
    - `UserRefreshTokenRepository`: Active token lookup by SHA-256 hash, JTI lookup, session revocation.
    - `RevokedTokenRepository`: Real-time JTI blacklist verification and token invalidation.
  - `backend/app/platform/identity/services.py`:
    - `authenticate`: Login via username or institutional email, Argon2id verification, brute-force protection (lockout after 5 failed attempts for 15 minutes), token pair generation, audit events (`LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOCKED_OUT`).
    - `refresh_tokens`: Validates refresh token, rotates session (marks old token revoked, issues new token pair), audit event (`TOKEN_REFRESH`).
    - `logout`: Immediate access token blacklisting and refresh token revocation, audit event (`LOGOUT`).
    - `revoke_token`: Arbitrary token invalidation by JTI, audit event (`TOKEN_REVOKED`).
    - `get_current_user_from_token`: Resolves active user from unrevoked Bearer token.
  - `backend/app/platform/identity/dependencies.py`: `get_current_user` FastAPI dependency for protected routes.
  - `backend/app/platform/identity/auth_router.py`:
    - `POST /api/v1/auth/login`
    - `POST /api/v1/auth/refresh`
    - `POST /api/v1/auth/logout`
    - `GET /api/v1/auth/me`
    - `GET /api/v1/auth/footprint`
    - `POST /api/v1/auth/revoke`
  - `backend/migrations/versions/20261104_1130_3460f1d24165_create_auth_token_tables.py`: Alembic migration applied to live PostgreSQL 17.
- **Repeatable Automated Regression Suite (`tests/test_auth.py`):** 8 tests passing:
  1. `test_login_success_and_jwt_claims`: Login via username and email, returning signed JWT tokens with claims and logging `LOGIN_SUCCESS`.
  2. `test_login_invalid_password_and_failed_event`: Invalid password returns 401 and logs `LOGIN_FAILED` event with attempt counter.
  3. `test_brute_force_lockout_trigger`: 5 consecutive failed attempts trigger account lockout (`LOCKED_OUT`), subsequent logins blocked until administrative unlock.
  4. `test_login_blocked_for_inactive_statuses`: Inactive statuses (`PENDING_ACTIVATION`, `SUSPENDED`, `DEACTIVATED`) cannot log in.
  5. `test_protected_me_and_footprint_endpoints`: Protected routes require valid Bearer token.
  6. `test_refresh_token_rotation_and_revocation`: Refresh token rotation and rejection of already-used refresh tokens.
  7. `test_logout_blacklists_access_token_and_revokes_refresh`: Immediate token invalidation on logout.
  8. `test_manual_token_revocation`: Explicit token revocation renders access token immediately unusable.

##### Stage 3.8: Integration & Verification (`COMPLETED`)
- **Implemented Components:**
  - `backend/tests/test_phase3_e2e.py`: Comprehensive end-to-end institutional workflow suite validating complete cross-domain integration across all Phase 3 subsystems:
    1. Apex Institutional Hierarchy provisioning (University, Schools, Departments, Research Centres, Programs, Academic Years, Semesters, Batches, Sections).
    2. Student Admission & Academic Progression (Admission, prior 10th/12th educational records, section allocation, roll number assignment, and semester enrollment).
    3. Staff Appointment & Dossier (Appointment, designations, Ph.D. qualifications, and cross-department joint research affiliations).
    4. User Account Provisioning & Linkage (Student & Staff portal user accounts, bidirectional ORM linkage, multi-organizational memberships).
    5. Authentication & Session Lifecycles (Argon2id password verification, JWT access tokens, `/me` profile retrieval, `/footprint` consolidated institutional footprint resolution, refresh token rotation, and logout token revocation).
    6. Identity Lifecycle & Zero-Cascade Safety (Account suspension, reinstatement, and safe deactivation guaranteeing 100% preservation of student academic history, enrollments, staff employment records, qualifications, and affiliations).
- **Automated Regression Test Suite:**
  - Full suite execution: **118 passed out of 118 tests across all 16 test files** in `backend/tests/` (100% passing).
  - Test suites:
    1. `tests/test_api_v1.py` (6 passed)
    2. `tests/test_auth.py` (8 passed)
    3. `tests/test_bootstrap.py` (6 passed)
    4. `tests/test_config.py` (6 passed)
    5. `tests/test_database.py` (9 passed)
    6. `tests/test_exceptions.py` (10 passed)
    7. `tests/test_foundation_e2e.py` (5 passed)
    8. `tests/test_identity.py` (10 passed)
    9. `tests/test_lifecycle.py` (4 passed)
    10. `tests/test_logging.py` (13 passed)
    11. `tests/test_migrations.py` (5 passed)
    12. `tests/test_organization.py` (8 passed)
    13. `tests/test_phase3_e2e.py` (1 passed)
    14. `tests/test_relationships.py` (7 passed)
    15. `tests/test_staff.py` (10 passed)
    16. `tests/test_students.py` (10 passed)
- **Phase 3 Exit Criteria Audit:**
  - [x] Institutional organization model operational with recursive unit tree.
  - [x] Central user identity operational with Argon2id password hashing.
  - [x] Student identity operational with prior records and semester enrollments.
  - [x] Staff identity operational with qualifications and experience, strictly decoupled from RBAC roles.
  - [x] Identity relationships operational with multi-unit memberships and cross-unit affiliations.
  - [x] Identity lifecycle operational with zero cascade deletion on account deactivation.
  - [x] Authentication foundation operational with JWT access tokens, refresh token rotation, and JTI blacklist revocation.
  - [x] Zero hardcoded secrets, full environment-driven configuration.
  - [x] Bidirectional Alembic schema evolution preserved with migrations up to `3460f1d24165`.
  - [x] Repeatable automated regression tests pass (118/118).

---

### Phase 4: RBAC & Authorization
- **Status:** `PLANNED`
- **Objective:** Enforce the enterprise access control model defined in `RBAC.MD`.
- **Key Modules:**
  - `app/platform/access_control/`: Role definitions, permission catalogues, organizational scopes (Global, School, Department, Programme, Batch, Personal).
  - Scope resolver dependencies (`require_permission`, `check_scope`).
  - Delegation engine (temporary administrative coverage).
  - Strict isolation for sensitive records (e.g., student wellbeing & counselling notes).

---

### Phase 5: Governance & Workflow Engine
- **Status:** `PLANNED`
- **Objective:** Implement the configurable multi-step approval state machine and compliance auditing defined in `workflow_architecture.md`.
- **Key Modules:**
  - `app/platform/workflows/`: State transition engine, approval policies, step assignment, timeout escalation.
  - `app/platform/audit/`: Immutable audit trail for all transactional operations.
  - `app/platform/notifications/`: Multi-channel notification dispatch (in-app, push via Capacitor, email).

---

### Phase 6: Frontend Foundation
- **Status:** `PLANNED`
- **Objective:** Build the core design system, role-based shell, navigation systems, and API client layer.
- **Scope:**
  - Institutional Theme: Deep Emerald (`#064E3B`), Royal Gold (`#C5A04B`), Canvas Ivory (`#FDFBF7`).
  - Component library: Tailwind CSS + Lucide React icon system.
  - Authentication flow: Login, MFA challenge, session restore, silent token refresh.
  - Dual-target packaging: Responsive web portal + compilation into native Android APK (`app-debug.apk`).

---

### Phases 7 – 11: Core Domains, Advanced Features & Production
- **Phase 7 (Core ERP Modules):** Student enrollment, faculty workload, course catalog, timetable, attendance tracking, exams & grading, student fee invoicing & payment gateway.
- **Phase 8 (Advanced Institutional Modules):** Corporate placement drives, IQAC accreditation records, research grant management, student mentorship, campus operations (hostels, transport routes, library catalog).
- **Phase 9 (Integration & Intelligence):** Centralized analytics dashboards, scheduled reporting, automated SMS/email communications, hardware biometric attendance sync.
- **Phase 10 (Security & QA):** Automated unit, integration, and end-to-end test suites; vulnerability auditing; load and stress testing.
- **Phase 11 (Production Deployment):** High-availability deployment, database replication, automated daily backups, SSL/TLS reverse proxy, disaster recovery validation.

---

## 3. Technology Stack Reference Baseline

| Component | Selected Technology | Version | Purpose |
|---|---|---|---|
| **Backend Framework** | FastAPI | `^0.115` (`0.162.0`) | High-performance async REST API & OpenAPI docs |
| **ORM / Database Access**| SQLAlchemy | `^2.0` (`2.1.6`) | Database abstraction, typing, and relationship mapping |
| **Data Validation** | Pydantic | `^2.10` (`2.14.2`) | Schema enforcement, request/response serialization |
| **Schema Migrations** | Alembic | `^1.14` (`1.20.1`) | Version-controlled database schema evolution |
| **Primary Database** | PostgreSQL | `17` | Relational transactional persistence |
| **Cache & Broker** | Valkey / Redis | `8.x` | In-memory cache, rate limiting, and message queue |
| **Background Processing**| Celery | `^5.4` (`5.6.3`) | Asynchronous task execution & scheduled jobs |
| **Frontend Framework** | React | `19.0.0` | Declarative component UI |
| **Language & Typings** | TypeScript | `5.8.2` | Static type safety across all frontend components |
| **Bundler & Tooling** | Vite | `6.2.1` | Ultra-fast development server & production bundler |
| **Styling & Tokens** | Tailwind CSS | `3.4.17` | Utility-first institutional design system |
| **Mobile Runtime** | Capacitor | `7.0.1` | Cross-platform bridge compiling to Native Android APK |
| **Icons System** | Lucide React | `1.16.0` | Accessible, clean line-art UI iconography |
| **Local Orchestration** | Docker Compose | `v2` | Service containerization and local dev isolation |

---

## 4. Phase Execution Framework

Every phase in this roadmap is executed using this strict 7-step quality lifecycle:

```
[1. Objective] ──> [2. Architecture] ──> [3. Structure] ──> [4. Implementation] 
                                                                    │
[7. Exit Criteria] <── [6. Documentation] <── [5. Testing] <────────┘
```

1. **Objective:** Define explicit business and technical requirements for the phase.
2. **Architecture:** Formulate schemas, sequence flows, and component interactions before coding.
3. **Structure:** Establish exact directory layouts, filenames, and interface contracts.
4. **Implementation:** Develop features incrementally with clean typing and zero mock strings.
5. **Testing:** Verify with automated tests, health checks, and end-to-end validation.
6. **Documentation:** Update architectural specs, API documentation, and phase logs.
7. **Exit Criteria:** Formally audit all completion conditions before unlocking subsequent phases.

