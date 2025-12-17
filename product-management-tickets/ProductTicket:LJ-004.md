## 🎟️ Product Ticket: LJ-004 — Child Profile Model & CRUD (MVP Data Foundation)

---

### 📌 Ticket ID

LJ-004

### 🧑‍💼 Ownership & Roles

* **Primary Owner (Full Stack Engineer):** Backend / Full Stack Engineer
* **Product Manager:** PM (scope control, acceptance)
* **Test Owner:** Test Engineer (functional & validation testing)
* **Design Owner:** ❌ Not required for this ticket

---

### 🎯 Objective

Create a **robust Child Profile data model** and **basic CRUD capability** that forms the **data foundation** for diagnostics, AI test generation, rankings, and rewards.

This ticket intentionally focuses on **data correctness and ownership**, not UI polish.

---

### 🧩 In Scope (MVP ONLY)

* Child Profile database model
* Parent → Child ownership relationship
* CRUD operations for Child Profile
* Validation of age, year group, and school metadata
* Secure access control (parents can only manage their own children)

---

### 🚫 Out of Scope (Explicitly Excluded)

* Child-facing dashboards or UI
* Avatars, rankings, or streaks
* AI logic or question generation
* Notifications or rewards logic (already handled in LJ-003)
* Styling, animations, or gamification

---

### 🧠 Functional Requirements

#### 1. Child Profile Model

The system must support a **Child Profile** entity with the following fields:

* `id` (UUID or auto ID)
* `parent` (ForeignKey → Parent/User)
* `first_name` (string)
* `age` (integer, validated range 5–11)
* `school_name` (string)
* `year_group` (integer or enum, aligned with UK years)
* `created_at` (datetime)
* `updated_at` (datetime)

---

#### 2. Ownership & Access Control

* Only authenticated parents can create Child Profiles
* Parents can **only view, edit, or delete their own children**
* Any cross-parent access must be rejected

---

#### 3. CRUD Operations

The system must support:

* Create Child Profile
* Read Child Profile (single + list by parent)
* Update Child Profile
* Delete Child Profile

Implementation may be via:

* Django views
* Django REST Framework
* Django Admin (acceptable for MVP)

---

#### 4. Validation Rules

* Age must be between **5 and 11 inclusive**
* Year group must align with age (basic validation only)
* School name must not be empty

---

### 🧪 Acceptance Criteria

| Scenario                            | Expected Result     |
| ----------------------------------- | ------------------- |
| Parent creates child                | Child profile saved |
| Invalid age (e.g. 3 or 15)          | Validation error    |
| Parent views own children           | Allowed             |
| Parent views another parent’s child | Access denied       |
| Parent updates child profile        | Changes persisted   |
| Parent deletes child profile        | Record removed      |

All criteria must pass for acceptance.

---

### 🔐 Non-Functional Requirements

* Must use existing authentication (LJ-002)
* Must integrate cleanly with Treasure Chest (LJ-003)
* Code must be testable and deterministic
* No breaking changes to existing features

---

### 🏗️ Technical Notes

* Child Profile should be reusable by future AI features
* Avoid hardcoding curriculum logic in this ticket
* Keep business logic out of views where possible
* Prepare model to be referenced by diagnostics, tests, and rewards

---

### 🧭 Dependencies

* LJ-002 — Parent Authentication ✅
* LJ-003 — Treasure Chest Core Logic ✅

---

### 🏁 Definition of Done

* Feature branch created: `feature/LJ-004-child-profile`
* All acceptance criteria met
* Tests written for model + access control
* Pull Request opened, reviewed, and merged
* No scope creep introduced

---

### 🚦 Priority

P0 — Foundational MVP feature
