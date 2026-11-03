UNIVERSITY ERP
Role-Based Access Control (RBAC)
Authorization Model & Permission Management Specification
Status: Design proposal for review | Version 1.0 | 13 October 2026
Purpose: define how the University ERP assigns, configures, evaluates, and audits permissions for roles and individual users. This document records the decisions established in discussion and identifies controls that require institutional validation before production implementation.
1. Executive Summary
The ERP will use a centralized, configurable Role-Based Access Control (RBAC) system. Permissions will not be scattered as hardcoded checks across individual modules. Authorized ERP Administrators will manage role permission bundles and individual permission exceptions through a centralized Permission Management interface. The backend will enforce the resulting permissions for every protected operation.
RBAC will be combined with data-scope checks and workflow rules. A permission answers “what action may this user perform?”; scope answers “on which records?”; workflow authority answers “may this user approve this particular operation at this stage?”
2. Objectives
•	Centralize role and permission configuration.
•	Allow authorized administrators to manage privileges without code changes for routine permission updates.
•	Support individual grants, restrictions, expiry, revocation, and review.
•	Apply authorization consistently across frontend, APIs, background jobs, exports, and integrations.
•	Maintain traceable records of permission changes and sensitive actions.
•	Support future modules through a shared permission model and documented module contracts.
3. Core Concepts
Concept	Meaning	Example
Identity / User	The authenticated individual account.	A staff member’s ERP account.
Designation	Official institutional position; not automatically a permission bundle.	HOD, Dean, Registrar.
Role	Reusable collection of permissions and responsibilities.	Faculty, HOD, Examination Officer.
Permission	A specific action on a resource.	examination.timetable.edit
Scope	The records or organizational boundary where an action is allowed.	Only the user’s department.
Individual override	A user-specific grant or restriction layered over role defaults.	Allow one HOD to export a report.
Workflow authority	Authority to perform an approval or transition in a workflow.	Approve a result publication.
Policy constraint	Mandatory rule that cannot be bypassed by ordinary permission configuration.	Separation of duties for result publication.
4. Established Design Decisions
•	Centralized management: The ERP Administrator manages role permissions and individual exceptions through one permission-management system.
•	Role defaults: Each role has a configurable set of default permissions. Users assigned that role inherit those permissions within the applicable scope.
•	Individual exceptions: An authorized Administrator can grant or restrict a specific permission for a specific individual without changing the role for other users.
•	Backend enforcement: The backend—not merely the user interface—must enforce permissions on every protected action.
•	Scope-aware access: Permissions do not automatically grant access to every record; school, department, assignment, ownership, and other relevant scope checks still apply.
•	Mandatory safeguards: Individual overrides cannot bypass mandatory security constraints, applicable institutional policies, or enforced separation-of-duties controls.
•	Auditability: Permission changes and sensitive operations must be attributable and reviewable.
5. Permission Structure
Permissions should use a consistent resource.action naming convention. Modules register permissions with the platform and use the same authorization service.
•	student.profile.view
•	student.profile.edit
•	attendance.record.create
•	attendance.record.edit
•	examination.timetable.view
•	examination.timetable.edit
•	examination.results.approve
•	examination.results.publish
•	finance.refund.approve
•	communication.announcement.publish
•	access_control.permission.manage
These names are examples, not a finalized permission catalogue. Each permission must define its resource, action, applicable scope, sensitivity, and any policy or workflow constraints.
6. Permission Evaluation Rules
The authorization service should evaluate each request using the following order:
1.	Authenticate the user and confirm that the account is active.
2.	Load the user’s active role assignments and applicable scopes.
3.	Apply mandatory platform and institutional policy constraints.
4.	Apply explicit individual restrictions; an ordinary role grant must not override an explicit restriction.
5.	Apply valid individual grants and role-derived permissions according to the documented precedence rules.
6.	Check record-level and organizational scope.
7.	Check workflow state, required approval authority, and separation-of-duties rules.
8.	Allow or deny the operation and record the decision when required by the audit policy.
Important implementation rule: “deny by default.” If the system cannot establish that an action is allowed, it must deny the operation. The exact precedence for multiple roles, multiple scopes, and conflicting grants must be implemented consistently and tested.
7. Individual Permission Overrides
Operation	Purpose	Required information / control
Grant	Add a permission for one user.	Permission, scope, reason, start date, expiry where applicable.
Restrict	Block a permission otherwise inherited.	Permission, scope, reason, duration/review date where applicable.
Expire	End a time-bound exception automatically.	Expiry timestamp and reliable scheduled enforcement.
Revoke	Remove an exception before expiry.	Actor, timestamp, reason and audit record.
Review	Reassess exceptional access.	Reviewer, decision, review date and outcome.
High-impact permissions—such as permission administration, result publication, sensitive-record access, or financial approvals—may require a second authorized approver. The institution must define which actions are subject to this requirement.
8. Role and Individual Example
Illustrative scenario: all HODs may view departmental records and edit attendance within their own department. By default, HODs may not export examination reports or publish results. The Administrator grants one HOD a time-limited export permission for an approved reporting task. Other HODs remain unchanged, and the selected HOD still cannot publish results unless separately authorized and permitted by policy.
Capability	Role default	Individual override	Effective result
View department records	Allow	None	Allow within scope
Edit attendance	Allow	None	Allow within scope
Export examination reports	Deny	Grant, time-limited	Allow within approved scope and period
Publish examination results	Deny	None	Deny
9. Scope and Separation of Duties
Permissions must be evaluated together with data scope. A permission to edit attendance does not authorize editing every student’s attendance. Scope may be based on school, department, program, batch, section, assigned course, ownership, or an explicitly approved cross-unit responsibility.
Workflow permissions must also be separate from general edit permissions. For example, entering marks, reviewing marks, approving results, and publishing results are distinct actions. The institution must identify workflows that require different people to perform these actions.
10. Administration Interface Requirements
•	Role catalogue with search, description, active status, and assigned-user count.
•	Permission matrix grouped by module, resource, and action.
•	Individual user access view showing inherited permissions and explicit overrides.
•	Clear distinction between role-derived, individually granted, individually restricted, and policy-blocked access.
•	Scope selector and start/expiry dates for applicable exceptions.
•	Reason field for privilege changes; mandatory for sensitive permissions.
•	Preview or simulation of effective permissions before saving.
•	Confirmation for high-impact changes and optional second-approver workflow.
•	Permission change history, exportable audit records, and periodic access-review queue.
•	Immediate or controlled cache invalidation so revoked access does not remain active unexpectedly.
11. Audit and Security Requirements
•	Record the actor, target user or role, permission, scope, old value, new value, reason, timestamp, and expiry.
•	Protect audit records from ordinary modification or deletion.
•	Re-check authorization on every API request and sensitive background operation.
•	Prevent users from granting permissions to themselves unless a separately approved, tightly controlled process explicitly permits it.
•	Protect permission-management endpoints against privilege escalation and mass assignment.
•	Test authorization failures, cross-department access, expired overrides, revoked permissions, and conflicting roles.
•	Define retention, monitoring, alerting, and incident-response procedures for access-control events.
12. Module Integration Contract
Every module must declare its permissions, protected resources, scopes, sensitive actions, workflow transitions, and audit requirements. Modules must call the shared authorization service rather than implementing independent permission logic. Adding a module should register new permissions through a controlled extension mechanism and must not grant them to roles automatically without an explicit configuration decision.
13. Decisions Still Requiring Confirmation
The following are open design or governance decisions. They should not be treated as approved university policy:
•	Which institutional roles may administer permissions, and whether some permission changes require dual approval.
•	Whether individual overrides can be created only by the ERP Administrator or by delegated access administrators.
•	The complete permission catalogue for every module.
•	The exact precedence and conflict rules for users with multiple roles and overlapping scopes.
•	Which permissions are time-limited by default and how often privileged access is reviewed.
•	Which workflows require separation of duties or institutional approval.
•	The university-approved policies for privacy, records retention, examination governance, finance, and confidential counselling data.
14. Acceptance Criteria
•	An authorized Administrator can configure role permissions without a code deployment.
•	An authorized Administrator can grant, restrict, expire, and revoke an individual exception.
•	Changing a role does not unintentionally alter unrelated roles or users’ individual exceptions.
•	Effective permissions are evaluated consistently across UI, API, exports, background jobs, and integrations.
•	Unauthorized cross-scope access is denied by the backend.
•	Mandatory policy constraints cannot be bypassed by ordinary overrides.
•	Permission changes and sensitive actions produce audit evidence.
•	Automated tests cover role inheritance, individual overrides, expiry, revocation, multiple roles, and scope boundaries.
15. Recommended Implementation Principle
Use configurable roles for standard access, individual overrides for justified exceptions, scope-aware checks for record access, and workflow policies for approvals. Keep the authorization engine centralized, deny by default, and audit privileged changes.
