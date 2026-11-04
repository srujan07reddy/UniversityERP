# University ERP — Student Portal Architecture & Design Specification



Final documentation draft

Version 1.0



This document consolidates the institutional branding, role-based visual identity, school and department differentiation, programme and specialization-level student portals, frontend architecture, configuration engine, backend integration and governance requirements.

# UNIVERSITY ERP

## Student Portal Architecture & Design Specification

**Document Version:** 1.1\
**Status:** Proposed Architecture Baseline\
**Frontend (Web & Mobile APK):** React + TypeScript (Vite + Capacitor 7)\
**Backend:** FastAPI\
**Database:** PostgreSQL\
**UI Framework:** Tailwind CSS + shadcn/ui\
**Mobile Platform:** Native Android APK via Capacitor (`in.ac.jeppiaaruniversity.erp`)\
**Animation:** Motion for React

---

# 1. Executive Summary

The University ERP will provide a unified institutional platform with customized user experiences for different academic schools, departments, programmes and specializations.

The student portal will not follow a single generic dashboard design. Instead, it will use a hierarchical, configuration-driven architecture that provides specialized interfaces based on each student's verified academic enrollment.

The system will support:

- University-wide institutional branding.
- School-specific academic identity.
- Department-specific functionality.
- Programme-specific dashboards.
- Specialization-specific widgets and navigation.
- Role-specific workspaces.
- Shared academic and administrative services.
- Centralized configuration and governance.

The primary objective is to create one integrated ERP platform that delivers different academic experiences without developing and maintaining independent applications for every department or specialization.

# 2. Design Objectives

The frontend architecture must satisfy the following objectives:

1. Establish a consistent university-wide visual identity.
2. Provide different dashboards for different categories of users.
3. Support distinct student experiences for individual academic programmes.
4. Support specialization-level customization.
5. Reuse common academic components across programmes.
6. Provide rich animations and interactive interfaces.
7. Maintain responsive layouts across desktop, tablet and mobile.
8. Support future academic programmes without restructuring the entire application.
9. Separate visual customization from authentication and authorization.
10. Allow authorized administrators to manage and publish portal configurations.

# 3. Institutional Design System

## 3.1 University Branding

The university's preferred institutional colours are Green and Gold.

These colours will remain the foundation of every ERP workspace.

| Colour          | Hex Code | Usage                        |
| --------------- | -------- | ---------------------------- |
| Deep Emerald    | #064E3B  | Primary institutional colour |
| Royal Gold      | #C5A04B  | Premium highlights           |
| Dark Emerald    | #043D2F  | Navigation and emphasis      |
| Gold Dark       | #80621F  | Accessible gold text         |
| Ivory Canvas    | #F7F8F5  | Main background              |
| Pure White      | #FFFFFF  | Cards and surfaces           |
| Forest Charcoal | #17251F  | Primary typography           |
| Sage Mist       | #E8EDE7  | Secondary surfaces           |

Gold will be used for institutional highlights, borders, selected navigation indicators, important icons and premium visual details.

Accessibility and colour contrast must be maintained, particularly for text placed over gold backgrounds.

## 3.2 Typography

Recommended typography:

- Primary font: Inter.
- Headings: Inter Semibold.
- Body: Inter Regular.
- Tables: Inter Regular.
- Numeric information: Tabular numerals.

## 3.3 Design Principles

The design should follow a hybrid enterprise and modern SaaS approach.

Required characteristics:

- Clean and structured layouts.
- Professional typography.
- Consistent spacing.
- Restrained shadows.
- Clear visual hierarchy.
- Functional animations.
- Consistent component behaviour.
- Minimal decorative gradients.
- Accessible contrast.

The application must not resemble a generic AI-generated dashboard.

# 4. Theme Architecture

The theme system will operate independently from the authorization system.

Three primary dimensions will determine the visual experience.

### 4.1 Institutional Identity

Common across the entire university:

- University logo.
- Institutional colours.
- Typography.
- Global components.
- Common design tokens.

### 4.2 Role Identity

Different workspaces will be provided for:

- Vice Chancellor.
- Registrar.
- Dean.
- HOD.
- Faculty.
- Student.
- Controller of Examinations.
- Examination stakeholders.
- Finance.
- Placement.
- Other authorized administrative personnel.

Each role will have a different workspace layout and relevant navigation.

### 4.3 Department Identity

Each department will have its own accent colour and specialized visual elements.

Proposed department accents:

| Department         | Accent              | Hex Code |
| ------------------ | ------------------- | -------- |
| CSE                | Technology Blue     | #2563EB  |
| AIML               | Intelligence Violet | #7C3AED  |
| Quantum Computing  | Quantum Cyan        | #0891B2  |
| AI & DS            | Data Amber          | #D97706  |
| ECE                | Circuit Teal        | #0F766E  |
| MBA                | Executive Gold      | #80621F  |
| BBA                | Business Blue       | #2563A6  |
| B.Com              | Commerce Green      | #28734B  |
| B.Sc               | Science Blue        | #2563A6  |
| BCA                | Digital Purple      | #7C3AED  |
| Aviation           | Aviation Navy       | #1E3A5F  |
| Biotechnology      | Bio Green           | #16804A  |
| Physical Education | Athletic Green      | #16803C  |

These are proposed interface colours and require institutional approval.

# 5. Academic Structure and Customization Hierarchy

The ERP will implement a hierarchical academic configuration system.

University → School → Department → Programme → Specialization → Student Academic Context.

## 5.1 University Level

Controls:

- Institutional branding.
- Academic calendar.
- Common policies.
- Global design tokens.
- Common ERP modules.
- Institutional notifications.

## 5.2 School Level

Controls:

- School identity.
- Academic administration.
- School-level announcements.
- School-specific resources.
- Academic reporting.

The university's school structure includes:

1. School of Engineering and Technology.
2. School of Sciences & Allied Health Sciences.
3. School of Arts, Humanities & Management.
4. School of Aviation.
5. School of Physical Education and Sports Science.

## 5.3 Department Level

Controls:

- Department-specific features.
- Department dashboards.
- Faculty and student resources.
- Laboratory configurations.
- Department projects.
- Department-level notifications.

## 5.4 Programme Level

Controls:

- Programme structure.
- Curriculum.
- Programme-specific dashboard configuration.
- Academic requirements.
- Common programme resources.

Examples include B.Tech, MBA, BBA, B.Com, B.Sc and BCA.

## 5.5 Specialization Level

Controls:

- Specialized widgets.
- Specialized navigation.
- Learning resources.
- Research activities.
- Technical or practical resources.
- Specialization-specific projects.

## 5.6 Student Academic Context

Contains:

- Student identification.
- Enrollment.
- Batch.
- Academic year.
- Semester.
- Registered subjects.
- Academic status.

Batch and semester primarily determine the academic data and available activities rather than creating separate dashboard templates.

# 6. Student Portal Architecture

The student portal will consist of one shared application shell and multiple specialized templates.

## 6.1 Engineering and Technology

### CSE — Computer Science and Engineering

Specialized functionality:

- Programming laboratories.
- Coding assessments.
- Software development projects.
- Project team management.
- Technical events.
- Internship tracking.
- Technical learning resources.

Potential specializations:

- General Computer Science.
- Cyber Security.
- Artificial Intelligence.
- Software Engineering.

### AIML — Artificial Intelligence and Machine Learning

Specialized functionality:

- Machine learning projects.
- Dataset management.
- Model experiment tracking.
- GPU resource booking.
- AI competitions.
- Research projects.
- Model development resources.

Potential specializations:

- Machine Learning.
- Deep Learning.
- Intelligent Systems.

### Quantum Computing

Specialized functionality:

- Quantum circuit simulation.
- Quantum laboratory schedules.
- Research projects.
- Quantum algorithm resources.
- Research publication tracking.
- Specialized learning resources.

Potential specializations:

- Quantum Algorithms.
- Quantum Information.
- Quantum Simulation.

### AI & DS — Artificial Intelligence and Data Science

Specialized functionality:

- Data analytics projects.
- Dataset repository.
- Statistical computing.
- Data visualization.
- Data pipeline projects.
- Analytics competitions.

Potential specializations:

- Data Science.
- Business Analytics.
- Big Data Analytics.

### ECE — Electronics and Communication Engineering

Specialized functionality:

- Electronics laboratory schedules.
- Hardware equipment booking.
- Embedded systems projects.
- Circuit design resources.
- Practical assessments.
- Hardware competitions.

Potential specializations:

- VLSI Design.
- Communication Systems.
- Embedded Systems.
- Signal Processing.

## 6.2 Arts, Humanities and Management

### MBA

Specialized functionality:

- Business case studies.
- Business simulations.
- Industry projects.
- Internship tracking.
- Leadership development.
- Group presentations.
- Placement preparation.

Potential specializations:

- Finance.
- Human Resource Management.
- Marketing.
- Operations.
- Business Analytics.

### BBA

Specialized functionality:

- Business projects.
- Entrepreneurship activities.
- Marketing simulations.
- Industrial visits.
- Business communication.
- Internship management.

Potential specializations:

- General Management.
- Finance.
- Marketing.
- Entrepreneurship.

### B.Com

Specialized functionality:

- Accounting practicals.
- Financial analysis.
- Taxation assignments.
- Banking and finance projects.
- Commerce internships.
- Financial literacy resources.

Potential specializations:

- General Commerce.
- Accounting and Finance.
- Corporate Secretaryship.
- Banking and Finance.

## 6.3 Sciences and Allied Health Sciences

### B.Sc

Specialized functionality:

- Laboratory schedules.
- Practical assessments.
- Research projects.
- Scientific learning resources.
- Laboratory equipment booking.
- Research supervision.

Potential specializations:

- Physics.
- Chemistry.
- Mathematics.
- Computer Science.

### Biotechnology

Specialized functionality:

- Biotechnology laboratory schedules.
- Research experiment tracking.
- Equipment management.
- Practical records.
- Research projects.
- Laboratory safety resources.

Potential specializations:

- Molecular Biology.
- Genetic Engineering.
- Industrial Biotechnology.
- Bioinformatics.

## 6.4 Computing Programme

### BCA

Specialized functionality:

- Programming assignments.
- Application development projects.
- Software laboratory schedules.
- Technical certifications.
- Coding competitions.
- IT placement preparation.

Potential specializations:

- General Computer Applications.
- Software Development.
- Application Development.

## 6.5 Aviation

Specialized functionality:

- Flight training schedules.
- Simulator reservations.
- Practical training records.
- Aviation safety resources.
- Training hours tracking.
- Aviation certification records.

Potential specializations:

- Flight Operations.
- Aviation Management.
- Aircraft Maintenance, where applicable.

## 6.6 Physical Education and Sports Science

Specialized functionality:

- Sports participation records.
- Fitness assessments.
- Training schedules.
- Tournament management.
- Sports equipment booking.
- Performance tracking.

Potential specializations:

- Sports Science.
- Sports Management.
- Fitness and Performance.
- Coaching and Training.

All programme and specialization lists must be validated against the university's approved academic catalogue before production.

# 7. Shared and Specialized Component Architecture

The ERP will use three component categories.

## 7.1 University-Wide Components

Shared by all eligible students:

- Student profile.
- Attendance.
- Timetable.
- Examination schedules.
- Examination results.
- Fee management.
- Notifications.
- Mentorship.
- Leave requests.
- Academic calendar.
- Placement portal.

## 7.2 Specialized Components

Examples:

- CSE: Coding assessment interface.
- AIML: Model experiment tracker.
- Quantum: Circuit simulation interface.
- AI & DS: Data visualization workspace.
- ECE: Hardware inventory interface.
- MBA: Business simulation interface.
- B.Com: Financial analysis workspace.
- B.Sc: Scientific laboratory interface.
- Biotechnology: Experiment tracking.
- Aviation: Training records.
- Physical Education: Sports performance tracker.

## 7.3 Configurable Components

Reusable components with programme-specific configurations:

- Project management.
- Laboratory booking.
- Resource scheduling.
- Research tracking.
- Academic performance charts.
- Assessment calendars.
- Faculty interaction.
- Department announcements.

The objective is to reuse business logic without forcing identical user interfaces.

# 8. Frontend Technology Stack

| Layer        | Technology       | Responsibility           |
| ------------ | ---------------- | ------------------------ |
| Framework    | React            | Application interface    |
| Language     | TypeScript       | Type safety              |
| Build tool   | Vite             | Development and bundling |
| Styling      | Tailwind CSS     | Design system            |
| Components   | shadcn/ui        | Reusable UI              |
| Animation    | Motion for React | Transitions              |
| Routing      | React Router     | Navigation               |
| Server state | TanStack Query   | API state                |
| Tables       | TanStack Table   | Data management          |
| Forms        | React Hook Form  | Form handling            |
| Validation   | Zod              | Schema validation        |
| Charts       | Recharts         | Analytics                |
| Icons        | Lucide React     | Icon system              |
| Mobile Bridge| Capacitor 7      | Native Android APK runtime |

Recommended starting template: Shadcn Admin.

The template will be customized to meet the university's design and architecture requirements.

## 8.1 Dual-Target Distribution (Web & Native Android APK)

The frontend is engineered as a unified single codebase serving two deployment targets:
1. **Responsive Web Portal**: Served via standard modern browsers across desktops, tablets, and mobile devices.
2. **Native Android Application (APK)**: Packaged via **Capacitor 7** into a native Android Gradle project located at `frontend/android/` with application ID `in.ac.jeppiaaruniversity.erp`.

Key native mobile architectural guidelines:
- **Zero Duplication**: Shared business logic, routing, domain queries, and design tokens across Web and APK.
- **Hardware Integration**: Capacitor bridges for native camera verification, biometric logins, push notifications, and local offline caching.
- **Safe Area Adaptations**: CSS environment bindings (`safe-area-inset-top`, `safe-area-inset-bottom`) and mobile viewport cover handling for notches and gesture navigation.
- **One-Command Compilation**:
  - `pnpm run build`: Generates production web bundle in `dist/`.
  - `pnpm cap:sync`: Synchronizes web assets to Android platform assets.
  - `pnpm build:apk`: Triggers Gradle to assemble `app-debug.apk` directly.
  - `pnpm cap:open:android`: Launches Android Studio for hardware emulation and signing release APKs.

# 9. Frontend Folder Architecture

```
src/
├── app/
│   ├── router/
│   ├── providers/
│   ├── layouts/
│   └── guards/
│
├── design-system/
│   ├── tokens/
│   ├── brand/
│   ├── themes/
│   ├── components/
│   └── animations/
│
├── student-portal/
│   ├── core/
│   ├── engine/
│   ├── registries/
│   ├── layouts/
│   ├── shared/
│   ├── widgets/
│   └── specializations/
│
├── workspaces/
│   ├── executive/
│   ├── hod/
│   ├── faculty/
│   ├── coe/
│   ├── finance/
│   ├── placement/
│   └── student/
│
├── features/
│   ├── authentication/
│   ├── academics/
│   ├── attendance/
│   ├── examinations/
│   ├── finance/
│   ├── mentorship/
│   ├── placements/
│   └── notifications/
│
├── services/
│   ├── api/
│   ├── authentication/
│   └── student-context/
│
└── types/
```

# 10. Template Configuration Engine

Five independent registries will be maintained:

1. School Registry.
2. Department Registry.
3. Programme Registry.
4. Specialization Registry.
5. Template Registry.

The Student Context Resolver will combine the configurations using the verified enrollment information.

## 10.1 Configuration Inheritance

The configuration resolution sequence will be:

University defaults → School configuration → Department configuration → Programme configuration → Specialization configuration → Student context.

More specific configurations may extend or override permitted presentation and feature settings.

The following cannot be overridden by a lower-level configuration:

- Institutional identity.
- Academic policies.
- Authorization rules.
- Official enrollment records.
- Examination governance.
- Approval authority.

## 10.2 Widget Registry

The dashboard renderer will load reusable widgets based on approved template configuration.

Each widget must define:

- Component identifier.
- Data contract.
- Permission requirements.
- Responsive behaviour.
- Loading state.
- Error state.
- Accessibility requirements.

Unknown or unauthorized widgets must not be rendered.

# 11. Backend Architecture

The backend will use FastAPI with PostgreSQL.

Recommended domains:

```
backend/
├── modules/
│   ├── academic_structure/
│   │   ├── schools/
│   │   ├── departments/
│   │   ├── programmes/
│   │   ├── specializations/
│   │   └── batches/
│   │
│   ├── student_enrollment/
│   ├── portal_configuration/
│   ├── authorization/
│   ├── academics/
│   ├── attendance/
│   ├── examinations/
│   ├── finance/
│   ├── mentorship/
│   └── placements/
│
└── api/
    └── v1/
```

## 11.1 Database Entities

| Entity             | Responsibility               |
| ------------------ | ---------------------------- |
| School             | University schools           |
| Department         | Academic departments         |
| Programme          | Academic programmes          |
| Specialization     | Programme specializations    |
| ProgrammeVersion   | Approved curriculum versions |
| StudentEnrollment  | Official enrollment          |
| PortalTemplate     | Template definitions         |
| TemplateVersion    | Template version history     |
| TemplateAssignment | Academic template mapping    |
| FeatureDefinition  | Available system features    |
| FeatureAssignment  | Feature configuration        |
| UserRole           | Assigned roles               |
| Permission         | Authorized operations        |

All academic entities should use stable identifiers and appropriate relational constraints.

# 12. Student Context Resolution

The backend will determine the student's portal using verified enrollment records.

Example endpoint:

GET /api/v1/students/me/portal-context

Illustrative response:

```
{
  "student": {
    "id": "student-id",
    "batch": "2023",
    "semester": 7
  },
  "academic_context": {
    "school": "SET",
    "department": "CSE",
    "programme": "BTECH",
    "specialization": "CYBER_SECURITY"
  },
  "portal": {
    "template_id": "cse-cyber-security",
    "template_version": 1,
    "layout": "technical"
  }
}
```

The backend will resolve the context from official enrollment records.

Students cannot manually select an unauthorized specialization or template.

# 13. Security and Authorization

Visual customization and authorization must remain independent.

The following principles are mandatory:

1. Frontend visibility does not establish authorization.
2. Every protected operation must be validated by FastAPI.
3. Role switching must use server-validated workspace context.
4. Students must only access their permitted academic records.
5. Department-specific resources must enforce department-level access policies.
6. Approval authority must be governed by backend workflows.
7. Template configuration cannot grant additional privileges.
8. API responses must be scoped to the authenticated user and permitted academic context.

# 14. Administrative Configuration and Governance

A dedicated Academic Programme and Portal Configuration module will allow authorized administrators to manage the academic hierarchy and portal templates.

Required capabilities:

- Create and manage schools.
- Create departments.
- Define programmes.
- Add specializations.
- Assign dashboard templates.
- Configure navigation.
- Enable or disable approved features.
- Preview templates.
- Publish template versions.
- Roll back published configurations.
- Maintain audit logs.

## 14.1 Proposed Approval Workflow

1. Department submits a proposal.
2. HOD reviews the academic requirement.
3. Dean or designated academic authority approves the academic configuration.
4. ERP administrator implements the portal configuration.
5. Authorized reviewers test the implementation.
6. Approved configuration is published.
7. Changes are recorded in the audit log.

The final approval hierarchy must follow university policy.

# 15. Animation and Interaction Standards

The interface will use Motion for React.

| Interaction        | Proposed duration |
| ------------------ | ----------------- |
| Page transition    | 200–300 ms        |
| Modal transition   | 180–240 ms        |
| Sidebar transition | 220–280 ms        |
| Dropdown           | 120–180 ms        |
| Card interaction   | 150–200 ms        |
| Dashboard entrance | 300–450 ms        |

Required interactions:

- Animated navigation indicators.
- Smooth sidebar expansion.
- Dashboard widget entrance.
- Interactive cards.
- Modal and drawer transitions.
- Animated progress indicators.
- Toast notifications.
- Skeleton loading.
- Responsive mobile navigation.

All animation must support reduced-motion preferences and must not interfere with operational performance.

# 16. Implementation Roadmap

### Phase 1 — Academic Structure

- Define schools.
- Define departments.
- Define programmes.
- Define specializations.
- Establish academic relationships.

### Phase 2 — Design System

- Institutional design tokens.
- Typography.
- Component library.
- Role themes.
- Department and programme accents.
- Animation standards.

### Phase 3 — Template Engine

- Configuration registries.
- Student context resolver.
- Template inheritance.
- Feature resolution.
- Widget registry.

### Phase 4 — Student Portal Foundation

- Student application shell.
- Header and navigation.
- Responsive layouts.
- Authentication integration.
- Enrollment-based template loading.

### Phase 5 — Prototype Development

Develop three representative student portal prototypes:

1. CSE Cyber Security.
2. MBA Finance.
3. B.Sc Physics.

These represent technical, management and scientific academic experiences.

### Phase 6 — Shared Academic Modules

- Attendance.
- Timetable.
- Examinations.
- Results.
- Fees.
- Mentorship.
- Notifications.
- Placements.

### Phase 7 — Specialized Modules

Develop programme-specific and specialization-specific widgets.

### Phase 8 — Administrative Configuration

Implement academic catalogue management, template configuration, approvals and version publishing.

### Phase 9 — Testing and Deployment

- Functional testing.
- Role and permission testing.
- Enrollment resolution testing.
- Responsive testing.
- Accessibility testing.
- Performance testing.
- Security testing.

# 17. Non-Negotiable Architectural Principles

1. One university ERP, not independent applications for every programme.
2. Shared academic functionality must not be duplicated.
3. Specializations may customize dashboards without changing the common application shell unnecessarily.
4. Academic enrollment determines the student's context.
5. The backend controls permissions.
6. Template configuration cannot override institutional governance.
7. Every published template must have a version.
8. Changes must be auditable and reversible.
9. New programmes must be addable without restructuring the entire frontend.
10. All workspaces must preserve institutional branding.

# 18. Final Architecture Summary

| Area                       | Final Decision                           |
| -------------------------- | ---------------------------------------- |
| Institutional identity     | Premium Green + Gold                     |
| Theme                      | Light                                    |
| Role differentiation       | Role-specific workspaces                 |
| Department differentiation | Department-specific accents and features |
| Student customization      | Programme and specialization level       |
| Template architecture      | Hierarchical and configuration-driven    |
| Dashboard rendering        | Widget registry                          |
| Academic context           | Enrollment-driven                        |
| Frontend                   | React + TypeScript                       |
| Styling                    | Tailwind CSS + shadcn/ui                 |
| Animation                  | Motion for React                         |
| Backend                    | FastAPI                                  |
| Database                   | PostgreSQL                               |
| Authorization              | Backend-controlled                       |
| Configuration governance   | Versioned approval and publishing        |

# 19. Conclusion

The University ERP will implement a unified but highly adaptable student portal architecture.

Every student will access the same institutional platform while receiving a dashboard designed around their academic programme and specialization.

The architecture will support different academic workflows, specialized resources, practical activities, research environments and learning experiences without duplicating common university services.

The system will remain extensible as new departments, programmes and specializations are introduced.

**Core architectural principle: One institution, one ERP, multiple academic experiences, centrally governed.**

---

**Document Status:** Final architecture proposal\
**Implementation Status:** Pending architecture approval and academic catalogue validation

## Recommended next action

Before coding, I recommend treating this document as the baseline architecture and moving to the Academic Structure Database Design: defining the actual School, Department, Programme, Specialization, Curriculum and Enrollment relationships in PostgreSQL.

That is the foundation on which the entire template engine will depend.