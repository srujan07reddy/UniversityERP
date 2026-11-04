# ROLES_AND_RESPONSIBILITIES.md

# Jeppiaar University — Roles, Responsibilities and Authority Framework

| Property | Details |
|---|---|
| Project | University ERP |
| Document | Roles and Responsibilities |
| Version | 1.0 |
| Status | Governance Baseline — Pending Institutional Approval |
| Scope | Entire University |
| Related Documents | ORGANIZATIONAL_STRUCTURE.md, ARCHITECTURE.md, RBAC.md, WORKFLOW_ARCHITECTURE.md |

---

# 1. Purpose

This document defines the roles, responsibilities, operational authority, accountability, reporting relationships and access boundaries of every major stakeholder within the University ERP.

The objective is to establish a clear governance framework that determines:

1. Who is responsible for an operation?
2. Who is authorized to perform it?
3. Who can approve it?
4. Who can review it?
5. Who can access the associated information?
6. Who is accountable for the outcome?
7. Who handles escalation?
8. Who maintains the relevant records?

This document acts as the foundation for:

- Role-Based Access Control (RBAC).
- Organizational scope management.
- Approval workflows.
- User provisioning.
- Dashboard customization.
- Data access restrictions.
- Institutional accountability.
- Audit and compliance.

# 2. Fundamental Governance Principles

## 2.1 Designation Is Not the Same as ERP Role

An institutional designation identifies a person's official position.

An ERP role determines the capabilities assigned to that person within the application.

Example:

| Institutional designation | ERP role |
|---|---|
| Chancellor | Administrator |
| Pro-Chancellor | Administrator |
| Vice-Chancellor | Administrator |
| Pro-Vice-Chancellor | Administrator |
| Registrar | Administrator |

Multiple institutional designations can share one ERP role.

The system must preserve the person's actual institutional designation separately from their ERP role.

## 2.2 Role Is Not the Same as Permission

A role is a collection of permissions.

Example:

A Dean may have:

- View school dashboard.
- View department performance.
- Review faculty workload.
- Review attendance.
- Submit school reports.
- Approve delegated school-level operations.

These permissions must be independently configurable.

## 2.3 Scope Determines the Records a User Can Access

A user must only access records within their authorized organizational scope.

Examples:

- Administrator: University-wide scope.
- Dean: Assigned school.
- HOD: Assigned department.
- Faculty: Assigned courses and students.
- Student: Own records.
- Placement Officer: University-wide placement operations.
- Finance Officer: Authorized financial operations.

## 2.4 Approval Authority Must Be Explicit

A user must not receive approval authority merely because of a designation.

Approval authority must be defined by:

- Institutional policy.
- Delegation.
- Operation type.
- Financial or operational limits, where applicable.
- Organizational scope.
- Approval configuration.

## 2.5 Separation of Duties

The system must separate incompatible responsibilities.

Examples:

- A user who configures permissions should not automatically approve financial transactions.
- A user who creates a payment record should not necessarily verify or reconcile that payment.
- A person entering marks should not automatically receive authority to publish final results.
- A technical administrator should not automatically have authority to approve institutional operations.

# 3. Role Classification

The ERP roles are classified into the following categories.

## 3.1 University Administration

- Administrator.
- ERP Super Admin.

## 3.2 Academic Administration

- Dean.
- HOD.
- Academic Coordinator.
- Program Coordinator.
- Faculty.
- Class Advisor.
- Course Coordinator.

## 3.3 Examination Administration

- Controller of Examinations.
- Additional Controller of Examinations.
- Deputy Controller of Examinations.
- Examination Cell Officer.
- Examination Superintendent.
- Chief Superintendent.
- Department Examination Representative.
- Internal Examiner.
- External Examiner.
- Invigilator.
- Evaluation Personnel.

## 3.4 Finance Administration

- Finance Officer.
- Accountant.
- Fee Management Officer.
- Payment Verification Officer.
- Scholarship Officer.

## 3.5 Placement Administration

- Placement Officer.
- Placement Coordinator.
- Department Placement Coordinator.
- Training Coordinator.

## 3.6 Quality and Research

- IQAC Coordinator.
- IQAC Member.
- Research Coordinator.
- Research Committee Member.
- IIC Coordinator.
- Innovation Coordinator.
- Student Development Coordinator.

## 3.7 Student and Academic Support

- Student Affairs Officer.
- Mentor.
- Counsellor.
- Grievance Officer.
- Student Support Officer.

## 3.8 Operational Administration

- Admission Officer.
- Librarian.
- Library Staff.
- Hostel Warden.
- Hostel Staff.
- Transport Manager.
- Transport Staff.
- Food In-charge.
- IT Administrator.
- Infrastructure Manager.
- Maintenance Staff.
- Legal and Compliance Officer.

## 3.9 University Community

- Student.
- Committee Member.
- External Evaluator.
- External Collaborator, where authorized.

The actual positions, appointments and reporting arrangements must be validated by the university.

# 4. University Administration Roles

## 4.1 Administrator

**Institutional designations represented:**

- Chancellor.
- Pro-Chancellor.
- Vice-Chancellor.
- Pro-Vice-Chancellor.
- Registrar.

**Organizational scope:** University-wide.

**Purpose:** Provide a consolidated institutional administration interface for university leadership.

### Responsibilities

1. Monitor university-wide activities.
2. Review institutional performance.
3. Monitor academic schools.
4. Review administrative operations.
5. Monitor examination operations.
6. Review university-level reports.
7. Monitor financial and operational summaries.
8. Review institutional compliance.
9. Participate in institutional approval workflows.
10. Monitor major university initiatives.
11. Review escalated matters.
12. Oversee institutional operations within delegated authority.

### ERP capabilities

- University dashboard.
- School-wise analytics.
- Administrative reports.
- Academic performance reports.
- Examination summaries.
- Financial summaries.
- Placement analytics.
- IQAC reports.
- Approval inbox.
- Institutional notifications.
- Escalation monitoring.

### Authority boundaries

- Must not automatically receive ERP infrastructure configuration privileges.
- Must not bypass mandatory approval workflows.
- Must not access confidential records without appropriate authorization.
- Must not independently modify audit records.
- Must follow delegated approval limits.

### Important implementation decision

All five designations share the Administrator ERP role.

The institutional designation must remain a separate attribute.

Where official policy requires different authority, the system must implement permission overrides or delegated approval rules without creating five disconnected administrator portals.

## 4.2 ERP Super Admin

**Purpose:** Manage the technical and security administration of the ERP.

**Scope:** Entire ERP platform.

### Responsibilities

1. User account provisioning.
2. User account deactivation.
3. Role configuration.
4. Permission configuration.
5. RBAC policy administration.
6. Organizational configuration.
7. Academic structure configuration.
8. Workflow configuration.
9. System settings.
10. API and integration configuration.
11. Technical monitoring.
12. Database administration coordination.
13. Backup management.
14. System recovery coordination.
15. Security configuration.
16. System maintenance.
17. Technical incident handling.

### Authority boundaries

ERP Super Admin must not automatically:

- Approve institutional financial transactions.
- Publish examination results.
- Approve student admissions.
- Modify academic marks without authorization.
- Override institutional approval policies.
- Access confidential counselling information for ordinary administrative purposes.
- Alter audit history.

### Security requirements

- MFA.
- Privileged account monitoring.
- Administrative audit logs.
- Controlled emergency access.
- Separation of duties.
- Periodic access reviews.

The ERP Super Admin is a technical role, not a university leadership designation.

# 5. Academic Administration Roles

## 5.1 Dean

**Scope:** One assigned academic school.

### Responsibilities

1. Lead school-level academic administration.
2. Monitor all departments under the assigned school.
3. Review HOD performance.
4. Monitor academic progress.
5. Review attendance statistics.
6. Monitor faculty workload.
7. Coordinate school-level academic activities.
8. Review department reports.
9. Coordinate academic requirements.
10. Monitor student academic performance.
11. Review school-level activities.
12. Coordinate with university administration.
13. Submit school-level reports.
14. Handle delegated school-level approvals.

### ERP capabilities

- School dashboard.
- Department-wise analytics.
- Faculty information.
- School student statistics.
- Attendance analytics.
- Academic performance.
- Timetable overview.
- Internal assessment monitoring.
- School-level workflow approvals.
- School reports.

### Authority boundaries

- Restricted to assigned school.
- Cannot independently change university academic regulations.
- Cannot publish university examination results without delegated authority.
- Cannot access unrelated school records by default.
- Cannot modify financial transactions without finance authorization.

## 5.2 Head of Department (HOD)

**Scope:** One assigned department.

### Responsibilities

1. Manage department operations.
2. Coordinate faculty members.
3. Allocate departmental academic responsibilities.
4. Monitor timetable execution.
5. Monitor student attendance.
6. Review internal assessments.
7. Monitor academic progress.
8. Coordinate departmental examinations.
9. Manage department activities.
10. Review student academic issues.
11. Coordinate with the Dean.
12. Submit departmental reports.
13. Coordinate examination representation.
14. Monitor departmental documentation.

### ERP capabilities

- Department dashboard.
- Student records within the department.
- Faculty assignments.
- Timetable management.
- Attendance monitoring.
- Assessment monitoring.
- Academic performance reports.
- Department activity management.
- Department-level approvals where delegated.

### Authority boundaries

- Restricted to assigned department.
- Cannot modify other departments' records.
- Cannot change university-wide curriculum independently.
- Cannot publish final examination results without authorization.
- Cannot modify financial records outside delegated responsibilities.

## 5.3 Academic Coordinator

**Scope:** Assigned academic school, department or program.

### Responsibilities

- Academic schedule coordination.
- Course allocation coordination.
- Curriculum implementation tracking.
- Academic progress monitoring.
- Academic documentation.
- Coordination between faculty and academic leadership.
- Academic activity reporting.

The exact scope depends on the appointment.

## 5.4 Program Coordinator

**Scope:** Assigned academic program.

### Responsibilities

- Program-level academic coordination.
- Curriculum implementation.
- Course mapping.
- Student progression monitoring.
- Program documentation.
- Accreditation evidence coordination.
- Program-level reporting.

## 5.5 Faculty

**Scope:** Assigned courses, classes and students.

### Responsibilities

1. Conduct assigned classes.
2. Manage course content.
3. Record attendance.
4. Conduct internal assessments.
5. Enter assessment marks.
6. Upload learning materials.
7. Manage assignments.
8. Monitor student progress.
9. Provide academic mentoring where assigned.
10. Communicate academic announcements.
11. Submit academic reports.
12. Participate in departmental activities.

### ERP capabilities

- Faculty dashboard.
- Course management.
- Attendance marking.
- Assessment entry.
- Assignment management.
- Learning materials.
- Student progress.
- Mentorship interface.
- Academic notifications.

### Authority boundaries

- Cannot access unrelated student records.
- Cannot alter attendance after closure without authorized correction.
- Cannot publish university examination results.
- Cannot modify official academic regulations.
- Cannot access confidential counselling records through ordinary faculty permissions.

## 5.6 Class Advisor

**Scope:** Assigned class or section.

### Responsibilities

- Monitor assigned class performance.
- Coordinate student attendance.
- Monitor student progression.
- Coordinate with subject faculty.
- Communicate academic information.
- Identify students requiring academic intervention.
- Submit class-level reports.

## 5.7 Course Coordinator

**Scope:** Assigned course or subject.

### Responsibilities

- Course planning.
- Course material coordination.
- Course delivery monitoring.
- Assessment coordination.
- Course outcome documentation.
- Course-level academic reporting.

# 6. Examination Administration Roles

The Examination Cell operates under the Controller of Examinations.

## 6.1 Controller of Examinations (COE)

**Scope:** University-wide examination administration.

### Responsibilities

1. Manage examination operations.
2. Plan examination schedules.
3. Coordinate examination registration.
4. Define examination-related procedures within delegated authority.
5. Verify examination eligibility processes.
6. Manage examination timetables.
7. Coordinate hall allocation.
8. Manage examination personnel assignments.
9. Coordinate question paper administration.
10. Monitor examination conduct.
11. Coordinate evaluation.
12. Manage marks processing.
13. Supervise result processing.
14. Coordinate GPA and CGPA calculations.
15. Manage revaluation processes.
16. Coordinate supplementary examinations.
17. Authorize result publication according to university policy.
18. Maintain examination records.
19. Generate examination reports.
20. Coordinate with Deans and HODs.

### ERP capabilities

- Examination dashboard.
- Examination calendar.
- Registration management.
- Eligibility monitoring.
- Timetable management.
- Hall allocation.
- Invigilation management.
- Marks processing.
- Evaluation monitoring.
- Result management.
- Revaluation.
- Supplementary examination management.
- Examination reports.

### Authority boundaries

- Examination operations must follow approved academic regulations.
- Department-level academic information must not be altered without authorization.
- Examination data must remain protected from unauthorized modification.
- Result publication must follow configured authorization requirements.
- Question papers must have restricted access.

## 6.2 Additional / Deputy Controller

### Responsibilities

- Assist the COE.
- Coordinate assigned examination operations.
- Monitor examination processes.
- Review assigned examination records.
- Handle delegated examination responsibilities.

Access depends on the authority delegated by the COE and university policy.

## 6.3 Examination Cell Officer

### Responsibilities

- Process examination registrations.
- Maintain examination records.
- Coordinate student examination information.
- Manage examination documentation.
- Support timetable administration.
- Process authorized examination requests.
- Maintain operational records.

Must not independently publish results or override examination policies.

## 6.4 Examination Superintendent

### Responsibilities

- Coordinate examination administration.
- Manage examination centre operations.
- Monitor examination arrangements.
- Coordinate examination personnel.
- Report operational incidents.
- Maintain examination centre records.

## 6.5 Chief Superintendent

### Responsibilities

- Supervise examination conduct at the assigned examination centre.
- Coordinate examination personnel.
- Monitor examination discipline.
- Handle centre-level operational issues.
- Report examination incidents.
- Submit examination completion reports.

## 6.6 Department Examination Representative

**Scope:** Assigned department.

### Responsibilities

- Coordinate examination requirements.
- Submit student examination information.
- Coordinate with HOD.
- Communicate examination notifications.
- Support examination registration verification.
- Coordinate examination-related documentation.
- Communicate department requirements to the COE.

Must not independently control university-wide examination operations.

## 6.7 Internal Examiner

### Responsibilities

- Evaluate assigned examination work.
- Enter authorized marks.
- Submit evaluation records.
- Maintain evaluation confidentiality.
- Report discrepancies.

## 6.8 External Examiner

### Responsibilities

- Evaluate assigned examination work.
- Submit evaluation records.
- Follow examination regulations.
- Maintain confidentiality.

External access must be temporary and limited to assigned evaluation activities.

## 6.9 Invigilator

### Responsibilities

- Conduct assigned examination duties.
- Verify examination attendance.
- Monitor examination discipline.
- Report malpractice or incidents.
- Submit examination duty reports.

Access is restricted to assigned examination sessions and centres.

## 6.10 Evaluation Personnel

### Responsibilities

- Process assigned answer scripts.
- Enter evaluation information.
- Maintain evaluation records.
- Report discrepancies.
- Follow confidentiality requirements.

# 7. Finance Administration Roles

## 7.1 Finance Officer

**Scope:** University-wide financial operations.

### Responsibilities

1. Manage financial administration.
2. Coordinate fee structures.
3. Monitor student fee collection.
4. Review outstanding dues.
5. Coordinate payment verification.
6. Monitor refunds.
7. Manage scholarship-related financial processing.
8. Monitor institutional expenses.
9. Maintain financial documentation.
10. Generate financial reports.
11. Coordinate with university administration.
12. Support financial audit activities.

### ERP capabilities

- Finance dashboard.
- Fee structures.
- Payment tracking.
- Outstanding dues.
- Refund workflows.
- Scholarship management.
- Expense tracking.
- Financial reporting.

### Authority boundaries

- Financial approval limits must be configurable.
- Payment creation and verification should be separated where required.
- Financial records must have audit trails.
- Finance access does not grant unrestricted academic access.

## 7.2 Accountant

### Responsibilities

- Maintain accounting records.
- Record authorized financial transactions.
- Process financial documentation.
- Reconcile payment records.
- Generate accounting reports.
- Support financial audits.

## 7.3 Fee Management Officer

### Responsibilities

- Maintain fee records.
- Process fee-related requests.
- Monitor payment status.
- Coordinate outstanding fee information.
- Maintain fee documentation.

## 7.4 Payment Verification Officer

### Responsibilities

- Verify payment information.
- Validate transaction references.
- Identify payment discrepancies.
- Confirm authorized payment status.
- Maintain verification records.

## 7.5 Scholarship Officer

### Responsibilities

- Manage scholarship applications.
- Verify scholarship documentation.
- Coordinate eligibility checks.
- Track scholarship approvals.
- Maintain scholarship records.

Scholarship eligibility and financial approval must follow the university's approved policies.

# 8. Placement Administration Roles

## 8.1 Placement Officer

**Scope:** University-wide placement operations.

### Responsibilities

1. Manage placement activities.
2. Coordinate company relationships.
3. Register employers.
4. Publish job opportunities.
5. Coordinate placement drives.
6. Manage eligibility criteria.
7. Monitor student applications.
8. Coordinate interviews.
9. Manage placement training.
10. Track internships.
11. Maintain offer records.
12. Generate placement reports.
13. Coordinate with Deans and HODs.
14. Monitor placement outcomes.

### ERP capabilities

- Placement dashboard.
- Company management.
- Job postings.
- Student eligibility.
- Application tracking.
- Interview schedules.
- Offer management.
- Training management.
- Placement analytics.

### Authority boundaries

- Operates across all schools.
- Cannot independently modify academic records.
- Cannot alter student examination results.
- Cannot override university academic eligibility policies.

## 8.2 Placement Coordinator

### Responsibilities

- Coordinate assigned placement activities.
- Manage placement communications.
- Track student participation.
- Support placement drives.
- Maintain placement records.

## 8.3 Department Placement Coordinator

**Scope:** Assigned department.

### Responsibilities

- Coordinate placement information.
- Communicate student eligibility requirements.
- Monitor departmental placement participation.
- Coordinate with the Placement Cell.
- Submit department-level placement information.

## 8.4 Training Coordinator

### Responsibilities

- Manage placement training schedules.
- Coordinate trainers.
- Monitor student attendance.
- Track training progress.
- Generate training reports.

# 9. Quality Assurance and Research Roles

## 9.1 IQAC Coordinator

**Scope:** University-wide quality assurance.

### Responsibilities

1. Coordinate institutional quality initiatives.
2. Collect academic information.
3. Coordinate academic audits.
4. Maintain quality documentation.
5. Coordinate accreditation evidence.
6. Monitor quality indicators.
7. Manage institutional feedback.
8. Coordinate Action Taken Reports.
9. Monitor improvement initiatives.
10. Generate quality reports.
11. Coordinate with Deans and HODs.
12. Report through approved institutional governance arrangements.

### ERP capabilities

- IQAC dashboard.
- Quality indicators.
- Department documentation.
- Accreditation evidence.
- Academic audits.
- Feedback analytics.
- Action Taken Reports.
- Quality reports.

### Authority boundaries

- Requires cross-school visibility into authorized institutional evidence.
- Does not automatically gain authority to modify academic or financial source records.
- Must preserve confidentiality.
- Must maintain documentation integrity.

## 9.2 IQAC Member

### Responsibilities

- Participate in quality initiatives.
- Review assigned documentation.
- Collect authorized institutional information.
- Support audits.
- Submit quality observations.

## 9.3 Research Coordinator

### Responsibilities

- Coordinate research projects.
- Maintain research records.
- Monitor research activities.
- Coordinate funding documentation.
- Track publications.
- Support research reporting.

## 9.4 Research Committee Member

### Responsibilities

- Review assigned research proposals.
- Participate in research evaluation.
- Submit recommendations.
- Maintain confidentiality.
- Record committee decisions.

## 9.5 IIC Coordinator

### Responsibilities

- Coordinate innovation activities.
- Manage innovation events.
- Support startup initiatives.
- Coordinate student innovation projects.
- Maintain institutional innovation records.
- Generate innovation activity reports.

## 9.6 Student Development Coordinator

### Responsibilities

- Coordinate student development programs.
- Manage training initiatives.
- Track student participation.
- Coordinate skill development.
- Maintain activity records.

# 10. Student Affairs and Support Roles

## 10.1 Student Affairs Officer

### Responsibilities

- Coordinate student welfare.
- Manage student engagement initiatives.
- Coordinate student grievances.
- Monitor student-support activities.
- Coordinate student events.
- Maintain student-affairs documentation.

## 10.2 Mentor

**Scope:** Assigned mentees.

### Responsibilities

1. Monitor assigned students.
2. Schedule mentorship meetings.
3. Record appropriate mentorship notes.
4. Monitor academic progress.
5. Identify student support requirements.
6. Guide students.
7. Follow up on assigned concerns.
8. Refer students to authorized support services when necessary.

### ERP capabilities

- Mentor dashboard.
- Assigned mentees.
- Meeting scheduling.
- Mentorship notes.
- Progress tracking.
- Follow-up records.
- Notifications.

### Authority boundaries

- Cannot access unrelated student records.
- Cannot access confidential counselling records unless separately authorized.
- Cannot modify official examination results.
- Must maintain mentorship confidentiality.

## 10.3 Counsellor

### Responsibilities

- Manage assigned counselling appointments.
- Provide authorized counselling services.
- Maintain confidential records.
- Manage appointment schedules.
- Record appropriate case information.
- Coordinate referrals when necessary.

### Security restrictions

Counselling information must be separated from ordinary student and academic records.

Only specifically authorized personnel may access confidential counselling records.

## 10.4 Grievance Officer

### Responsibilities

- Receive assigned grievances.
- Categorize complaints.
- Investigate assigned matters.
- Coordinate with relevant authorities.
- Record actions taken.
- Escalate unresolved matters.
- Maintain grievance closure documentation.

## 10.5 Student Support Officer

### Responsibilities

- Coordinate student support services.
- Process assigned requests.
- Maintain student-support records.
- Coordinate service referrals.
- Monitor support requests.

# 11. Admissions Administration Roles

## 11.1 Admission Officer

**Scope:** University admissions.

### Responsibilities

- Manage admission applications.
- Maintain applicant records.
- Verify submitted documents.
- Coordinate eligibility checks.
- Track application status.
- Coordinate admission decisions.
- Manage admission communications.
- Coordinate enrollment.
- Generate admission reports.

### Authority boundaries

Admission decisions must follow approved university policies.

Admission staff must not independently modify financial or academic regulations.

# 12. Operational Administration Roles

## 12.1 Librarian

### Responsibilities

- Manage library operations.
- Maintain book catalogues.
- Manage book issue and return.
- Monitor inventory.
- Manage library memberships.
- Coordinate digital library resources.
- Generate library reports.

## 12.2 Library Staff

### Responsibilities

- Process book transactions.
- Maintain library records.
- Assist library users.
- Update inventory.
- Handle assigned library operations.

## 12.3 Hostel Warden

### Responsibilities

- Manage hostel administration.
- Coordinate room allocation.
- Monitor hostel occupancy.
- Manage hostel-related requests.
- Coordinate maintenance.
- Monitor hostel operational records.
- Generate hostel reports.

## 12.4 Hostel Staff

### Responsibilities

- Support hostel administration.
- Maintain assigned records.
- Process operational requests.
- Coordinate hostel services.

## 12.5 Transport Manager

### Responsibilities

- Manage university transport operations.
- Maintain vehicle records.
- Manage routes.
- Coordinate transport schedules.
- Monitor vehicle maintenance.
- Coordinate drivers.
- Manage student transport allocation.
- Generate transport reports.

## 12.6 Transport Staff

### Responsibilities

- Maintain assigned transport records.
- Update operational information.
- Coordinate assigned transport activities.

## 12.7 Food In-charge

### Responsibilities

- Coordinate food and canteen operations.
- Manage vendor information.
- Monitor food service operations.
- Coordinate complaints.
- Maintain operational records.
- Generate service reports.

## 12.8 IT Administrator

### Responsibilities

- Manage university IT infrastructure.
- Maintain network services.
- Coordinate server operations.
- Manage technical support.
- Monitor system availability.
- Coordinate security maintenance.
- Support ERP infrastructure.

The IT Administrator and ERP Super Admin may be assigned to the same individual only when approved and with appropriate separation-of-duty safeguards.

## 12.9 Infrastructure Manager

### Responsibilities

- Manage institutional infrastructure.
- Coordinate maintenance.
- Track facility requirements.
- Manage assigned operational requests.
- Monitor infrastructure records.

## 12.10 Maintenance Staff

### Responsibilities

- Receive assigned maintenance requests.
- Update work status.
- Record completed activities.
- Escalate unresolved issues.

## 12.11 Legal and Compliance Officer

### Responsibilities

- Maintain legal documentation.
- Coordinate compliance records.
- Support legal review.
- Track compliance requirements.
- Maintain assigned regulatory documentation.
- Coordinate authorized audits.

Access must be limited to assigned legal and compliance responsibilities.

# 13. Student Role

**Scope:** Individual student account.

### Responsibilities

- Maintain permitted profile information.
- Access academic information.
- View attendance.
- View timetable.
- Access learning materials.
- Submit assignments.
- View internal assessment information.
- Access examination information.
- View published results.
- Make fee payments.
- Access placement opportunities.
- Apply for placements.
- Access mentorship services.
- Book authorized counselling appointments.
- Submit grievances.
- Receive university notifications.
- Access applicable library and hostel services.

### ERP capabilities

- Student dashboard.
- Personal profile.
- Academic records.
- Attendance.
- Timetable.
- Assignments.
- Results.
- Fee records.
- Placement.
- Mentorship.
- Student support.
- Notifications.

### Authority boundaries

Students must not:

- Access another student's confidential information.
- Modify official academic records.
- Modify attendance records.
- Modify examination results.
- Access restricted institutional documents.
- Access internal administrative workflows.

# 14. Committee Member Role

**Scope:** Assigned committee and tenure.

### Responsibilities

- Access assigned committee information.
- Participate in meetings.
- Review assigned documents.
- Submit recommendations.
- Record assigned decisions.
- Track assigned action items.

Committee membership must not automatically grant access to unrelated institutional records.

# 15. External User Roles

External users may include:

- External examiners.
- External evaluators.
- Industry representatives.
- Employers.
- Research collaborators.
- Authorized external auditors.

External access must be:

- Assignment-based.
- Time-limited.
- Permission-restricted.
- Auditable.
- Revocable.

External accounts must not receive unrestricted university access.

# 16. Consolidated Role and Scope Matrix

| Role | Scope | Primary responsibility |
|---|---|---|
| Administrator | University | Institutional administration |
| ERP Super Admin | ERP platform | Technical administration |
| Dean | Assigned school | School administration |
| HOD | Assigned department | Department administration |
| Academic Coordinator | Assigned academic unit | Academic coordination |
| Program Coordinator | Assigned program | Program administration |
| Faculty | Assigned courses | Teaching and assessment |
| Class Advisor | Assigned section | Class monitoring |
| Course Coordinator | Assigned course | Course coordination |
| COE | University | Examination governance |
| Deputy COE | Delegated examination scope | Examination operations |
| Examination Cell Officer | Examination Cell | Examination processing |
| Examination Superintendent | Assigned centre | Examination supervision |
| Chief Superintendent | Assigned centre | Examination conduct |
| Department Exam Representative | Department | Examination coordination |
| Internal Examiner | Assigned evaluation | Internal evaluation |
| External Examiner | Assigned evaluation | External evaluation |
| Invigilator | Assigned session | Examination supervision |
| Evaluation Personnel | Assigned evaluation | Marks processing |
| Finance Officer | University finance | Financial administration |
| Accountant | Assigned finance scope | Accounting |
| Fee Management Officer | Finance | Fee operations |
| Payment Verification Officer | Finance | Payment verification |
| Scholarship Officer | Finance | Scholarship processing |
| Placement Officer | University | Placement operations |
| Placement Coordinator | Assigned scope | Placement coordination |
| Department Placement Coordinator | Department | Department placement |
| Training Coordinator | Assigned training | Training operations |
| IQAC Coordinator | University | Quality assurance |
| IQAC Member | Assigned quality scope | Quality activities |
| Research Coordinator | Research unit | Research administration |
| Research Committee Member | Assigned committee | Research review |
| IIC Coordinator | University | Innovation coordination |
| Student Development Coordinator | Assigned scope | Student development |
| Student Affairs Officer | University | Student welfare |
| Mentor | Assigned mentees | Mentorship |
| Counsellor | Assigned cases | Counselling |
| Grievance Officer | Assigned grievances | Grievance resolution |
| Student Support Officer | Assigned services | Student support |
| Admission Officer | University | Admissions |
| Librarian | Library | Library administration |
| Library Staff | Assigned library operations | Library services |
| Hostel Warden | Assigned hostel | Hostel administration |
| Hostel Staff | Assigned hostel operations | Hostel services |
| Transport Manager | Transport | Transport administration |
| Transport Staff | Assigned transport operations | Transport services |
| Food In-charge | Food operations | Canteen administration |
| IT Administrator | IT infrastructure | Technical operations |
| Infrastructure Manager | Infrastructure | Facility administration |
| Maintenance Staff | Assigned tasks | Maintenance |
| Legal and Compliance Officer | Assigned compliance scope | Legal and compliance |
| Student | Individual | Academic participation |
| Committee Member | Assigned committee | Committee responsibilities |
| External User | Assigned activity | External collaboration |

# 17. Responsibility, Accountability and Approval Matrix

The following matrix identifies the primary operational owner and the authority that may be involved.

It is not a universal approval chain. Final approval rules must be defined separately for each operation.

| Operation | Responsible party | Functional authority / review |
|---|---|---|
| Student profile update | Student / authorized staff | Assigned administrative authority |
| Student admission | Admission Officer | Authorized admission authority |
| Department timetable | Academic Coordinator / HOD | Dean where delegated |
| Attendance entry | Faculty | HOD for monitoring |
| Attendance correction | Authorized academic staff | Designated approver |
| Internal marks entry | Faculty | HOD / authorized academic authority |
| Final result processing | Examination Cell | COE |
| Result publication | Examination Cell | COE / delegated authority |
| Examination registration | Examination Cell | COE |
| Examination hall allocation | Examination Cell | Authorized examination authority |
| Invigilator allocation | Examination authority | COE / delegated authority |
| Fee structure | Finance | Authorized university authority |
| Payment recording | Finance staff / gateway | Finance verification |
| Refund | Finance | Authorized financial approver |
| Placement drive | Placement Officer | Delegated university authority |
| Placement eligibility | Placement Cell | Approved academic criteria |
| Accreditation documentation | IQAC | Institutional review |
| Research proposal | Researcher | Authorized research committee |
| Mentorship assignment | Mentorship coordinator | Authorized academic authority |
| Counselling appointment | Student / Counsellor | Authorized counselling personnel |
| Grievance resolution | Grievance Officer | Designated escalation authority |
| Hostel allocation | Hostel Administration | Authorized authority |
| Transport allocation | Transport Manager | Authorized operational authority |
| User account creation | Authorized administrator | Approved provisioning policy |
| Role assignment | Authorized access administrator | Institutional authorization |
| Workflow configuration | ERP Super Admin | Approved business policy owner |

# 18. Role Assignment and User Lifecycle

## 18.1 User Creation

Every user account must be associated with:

- Unique user identifier.
- Institutional identity.
- Institutional designation.
- ERP role assignment.
- Organizational assignment.
- Account status.
- Effective date.
- Expiry date, where applicable.

## 18.2 Multiple Role Assignments

The system must support multiple authorized roles for one person.

Example:

An employee may be:

- Faculty.
- Department Placement Coordinator.
- Examination Representative.

Each assignment must have its own scope and permissions.

The system must not merge these assignments into unrestricted access.

## 18.3 Temporary Assignments

Temporary assignments must support:

- Start date.
- End date.
- Assigned responsibilities.
- Assigned scope.
- Delegating authority.
- Automatic expiry.

## 18.4 Role Revocation

When an employee changes designation or leaves the institution:

- Previous assignments must be closed.
- Active permissions must be reviewed.
- Pending approvals must be reassigned.
- Access tokens and sessions must be revoked where appropriate.
- Historical actions must remain auditable.

# 19. Delegation and Approval Authority

The ERP must support delegated authority.

Examples:

- A Dean delegates a defined school-level responsibility.
- The COE delegates a specific examination operation.
- The Finance authority delegates payment verification.
- An authorized university administrator delegates an institutional task.

Delegation must include:

1. Delegating authority.
2. Assigned individual.
3. Operation or permission.
4. Organizational scope.
5. Effective date.
6. Expiry date.
7. Delegation reason.
8. Approval reference.
9. Audit record.

Delegation must not automatically transfer all permissions of the original authority.

# 20. Separation of Duties

The following separation principles must be enforced.

| Function A | Function B | Governance requirement |
|---|---|---|
| User provisioning | Role approval | Separate where required |
| Role configuration | Institutional authorization | Separate |
| Payment creation | Payment verification | Separate where required |
| Marks entry | Final result publication | Controlled separation |
| Question paper creation | Unauthorized paper access | Restricted |
| Grievance investigation | Final review | Separate where policy requires |
| Counselling | Academic disciplinary access | Confidentiality boundary |
| System administration | Business approval | Separate |

These controls should be configurable according to institutional policies and risk.

# 21. Data Access Boundaries

| Data category | Authorized functional access |
|---|---|
| Institutional records | Authorized administration |
| School records | Assigned school authorities |
| Department records | Assigned department authorities |
| Academic records | Authorized academic personnel |
| Student personal records | Student and authorized staff |
| Examination records | COE and assigned examination personnel |
| Question papers | Specifically authorized examination personnel |
| Financial records | Authorized finance personnel |
| Placement records | Placement personnel and relevant students |
| IQAC documentation | Authorized IQAC personnel |
| Research records | Authorized research personnel |
| Mentorship records | Assigned mentors and authorized coordinators |
| Counselling records | Authorized counselling personnel |
| Grievance records | Assigned grievance personnel |
| Legal records | Authorized legal and compliance personnel |

Access must be enforced at the API and data-access layers.

# 22. Dashboard Responsibilities

Each role should receive an interface that reflects its responsibilities.

| Role | Dashboard focus |
|---|---|
| Administrator | University-wide institutional overview |
| ERP Super Admin | System health, users, permissions and configuration |
| Dean | School performance |
| HOD | Department operations |
| Faculty | Classes, attendance and assessments |
| COE | Examination operations |
| Examination Staff | Assigned examination tasks |
| Finance Officer | Financial operations |
| Accountant | Accounting tasks |
| Placement Officer | Placement activities |
| Placement Coordinator | Assigned placement activities |
| IQAC Coordinator | Quality indicators and evidence |
| Research Coordinator | Research activities |
| Student Affairs Officer | Student support operations |
| Mentor | Assigned mentees |
| Counsellor | Confidential appointments |
| Admission Officer | Admissions |
| Librarian | Library operations |
| Hostel Warden | Hostel operations |
| Transport Manager | Transport operations |
| Student | Personal academic and university services |

The same underlying dataset must be presented differently according to user responsibilities.

# 23. Role and Permission Governance

The ERP must maintain a controlled permission catalogue.

Every permission should have:

- Permission identifier.
- Permission name.
- Description.
- Functional module.
- Supported actions.
- Applicable scope.
- Sensitivity classification.
- Approval requirement, if applicable.
- Status.

Example permission identifiers:

```text
student.view
student.create
student.update
student.archive

attendance.view
attendance.mark
attendance.correct
attendance.approve

examination.registration.view
examination.schedule.manage
examination.marks.enter
examination.results.process
examination.results.publish

finance.fees.view
finance.payments.verify
finance.refunds.process

placement.companies.manage
placement.drives.manage
placement.offers.manage

workflow.view
workflow.submit
workflow.approve
workflow.reject

organization.manage
rbac.roles.manage
rbac.permissions.manage
audit.logs.view
```

These identifiers are illustrative and must be finalized during RBAC implementation.

# 24. Audit and Accountability

The ERP must record:

- User identity.
- Institutional designation.
- Assigned ERP role.
- Organizational scope.
- Action performed.
- Target record.
- Timestamp.
- Previous and new values where applicable.
- Approval reference.
- Delegation reference.
- Reason for sensitive operations.

The audit system must preserve historical accountability even after a person's role or organizational assignment changes.

# 25. Open Governance Decisions

The following decisions require official institutional confirmation:

1. Whether all five university leadership designations share identical operational permissions within the Administrator role.
2. Who formally authorizes Administrator role assignments.
3. Who appoints and governs the ERP Super Admin.
4. The official approval authority for financial transactions.
5. The exact hierarchy within the Examination Cell.
6. The authority responsible for final result publication.
7. The approval authority for admissions.
8. The formal authority of Deans over school-level expenditures.
9. The IQAC reporting and escalation arrangement.
10. The official authority for research project approvals.
11. The official grievance escalation hierarchy.
12. The appointment and delegation policies for department representatives.
13. Whether additional role separation is required for specific high-risk operations.
14. The formal authority for modifying organizational structures.

These must not be silently assumed during implementation.

# 26. Final Governance Principles

1. Every user must have an identifiable institutional assignment.
2. Every ERP role must have a defined responsibility.
3. Every permission must have a clear purpose.
4. Every permission must have an applicable scope.
5. Every approval must have an authorized authority.
6. Every delegation must have an expiry and audit record.
7. Every sensitive operation must be auditable.
8. Every role must have defined access boundaries.
9. Technical administration must remain distinct from institutional administration.
10. Organizational authority must remain distinct from workflow authority.
11. Multiple roles must be supported without privilege accumulation beyond approved assignments.
12. Confidential student information must receive additional protection.
13. Historical actions must remain traceable.
14. Institutional governance decisions must be configurable rather than hardcoded.

---

**Document Owner:** University ERP Project Team  
**Document:** ROLES_AND_RESPONSIBILITIES.md  
**Version:** 1.0  
**Status:** Governance Baseline — Pending Institutional Approval