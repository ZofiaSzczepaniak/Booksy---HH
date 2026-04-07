## AI Development Log

### Tooling
- **Claude Code** — primary coding assistant throughout the session (architecture, code generation, debugging, test fixes)
- **VS Code** — IDE

### Data Strategy

The seed JSON contained several data quality challenges. To identify them all manual audit was needed, because AI-generated code didn't provide enough safeguards for quality of loaded data, as it didn't account for typos in brands, wrong date format etc. It had to be further ensured through building rules.

The following normalizing rules were implemented:

1. **Brand Name Standardization**
   - Capitalize brand names properly (e.g., "apple" → "Apple", "SAMSUNG" → "Samsung")
   - Correct common typos and variations (e.g., "Aple" → "Apple", "Samsng" → "Samsung", "Delll" → "Dell")
   - Handle matching for known brands

2. **Date Format Normalization**
   - Convert all purchase dates to ISO format (YYYY-MM-DD)
   - Set default to unknown for invalid or missing dates

3. **Status Field Validation**
   - Ensure status is one of the valid values: "Available", "In Use", "Repair"
   - Default to "Available" for new items
   - "Unkown" assigned to invalid dates

4. **ID Duplication Handling**
   - Detect and resolve duplicate IDs during import
   - First available ID is assigned if new data is not a clone of existing, else disregard


### Prompt Trail

#### Prompt 1
You are a senior full-stack developer. Help me build a hardware rental management app.
Use:

Backend: Python (FastAPI)

Frontend: Vue.js

Database: SQLite

Requirements:

Admin and Users:

Admin can add/edit/delete hardware and create users (no public signup)

Simple login system (JWT)

Dashboard showing hardware (name, brand, purchase date, status)

Add sorting and filtering

Rental Logic:

Users can rent and return devices

Enforce rules:

Only rent if Available

Cannot rent if In Use or Repair

Only return if currently In Use by the given user

Track who is using the device

AI Features:

semantic search (e.g. “phone for testing” → relevant devices)

AI audit flags potential issues in the current
inventory based on all available information.

Data:

Start from a JSON dataset (I’ll provide it)

Clean issues like duplicate IDs, bad dates, wrong brands, invalid statuses

Testing:

Write at least 3 tests:

Cannot rent unavailable device

Cannot rent device in repair

Returning updates status correctly

Output:

Give me:

Project structure

Backend code

Frontend code

How to run it

Keep code clean and production-like, not a quick prototype.

#### Prompt 2.

The admin account should be predefined automatically. Implement automatic creation of a default admin account when the application starts (e.g. during app initialization).

Make sure:

The admin has role = "admin".
Credentials are:
username - "admin",
password - "admin123".

Update your solution accordingly.

#### Prompt 3. 

The dataset isn't seeded automatically to the database, how it should be seeded?

#### Prompt 4. 

The dataset contains intentionally faulty entries (invalid dates, brand typos, duplicate IDs). Implement data normalization and validation during import.

Requirements:

Normalize brand names (e.g. fix typos like "Appel" → "Apple")

Standardize date formats to a consistent format (e.g. ISO YYYY-MM-DD)

Handle duplicate IDs:

If a new item has a duplicate ID but different data → assign it the next available free ID

If all fields (name, brand, date, status, etc.) are identical to an existing record → ignore the new item (do not insert)

Ensure the process is deterministic and idempotent

#### Prompt 5. 

User search queries may be ambiguous. Improve the AI search by implementing a multi-step pipeline:

LLM Interpretation
Parse the natural language query into structured requirements (e.g. device type, use case, key features)

External Knowledge Enrichment
Use internet search (or a knowledge source) to better understand the use case and typical requirements

Specification Matching
Map the inferred requirements to available hardware specifications in the database

LLM Ranking & Selection
Return the best matching items based on relevance

Justification
For each suggested item, provide a short explanation of why it matches the user’s needs

#### Prompt 6.

Adjust the frontend to match the layout and styling from the provided reference images.

Additional requirement:

The login username field must enforce the company domain @booksy.com

Important:

Do NOT change any existing functionality

Do NOT modify application structure

Do NOT alter communication with the backend

This refinement should affect only the UI and input validation layer.

#### Prompt 7.

Authentication Fix:
Refine the user authentication so that:

Users must log in using username only, not email.
Enforce that usernames belong to the domain @booksy.com.
Keep all other login functionality unchanged.

#### Prompt 8.

Button Placement:
Correct the placement of all buttons in the frontend:

Ensure that all buttons are positioned consistently as per the design reference and unify their size.
No other functionality or layout should be altered.

#### Prompt 9.

User Creation and Admin Panel:
Update the user creation pane and admin panel:

Replace the username input with email input in the user creation form.
Remove any unnecessary captions from the admin panel.
Keep all other functionality intact.

#### Prompt 10.

Analyze the following test failures and errors. Explain the root cause clearly and propose fixes.

Focus on:

Error Explanation
Identify why the TypeError: <lambda>() takes 0 positional arguments but 1 was given occurs

Explain how the mocking/patching setup is breaking the expected constructor behavior

Fix the Issue

Provide a correct implementation for the patching logic so that injected classes still accept required arguments (e.g. database path)

Ensure compatibility with dependency injection in tests

Test Stability

Verify that the fix resolves all failing tests across:

HardwareManager

UserManager

RentalLogic

Ensure no regressions

Code Improvements

Suggest a cleaner pattern for dependency injection (e.g. factory functions or FastAPI dependency overrides instead of lambda patching)

exemplary error log:
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001F118587E30>

    @pytest.fixture
    def client(tmp_path, monkeypatch):
        """FastAPI test client with fresh DB."""
        db = str(tmp_path / "api.db")
        import main as main_module
        import importlib

        # Patch HardwareManager and UserManager to use temp DB
        original_hm = main_module.HardwareManager
        original_um = main_module.UserManager

        monkeypatch.setattr(main_module, "HardwareManager", lambda: original_hm(db))
        monkeypatch.setattr(main_module, "UserManager", lambda: original_um(db))

        # Seed: admin user + one available item + one "In Use" item + one "Repair" item
>       hm = original_hm(db)
             ^^^^^^^^^^^^^^^
E       TypeError: patch_db.<locals>.<lambda>() takes 0 positional arguments but 1 was given

### The Correction

Multiple critical bugs were identified and resolved throughout development. The initial AI-generated code had inconsistencies that required extensive fixes:

| Bug Category | Root Cause | Fix |
|---|---|---|
| **Authentication Logic** | Domain enforcement (@booksy.com) and form field inconsistencies | Updated frontend validation and changed admin user creation to use email input |
| **Data Management** | No data seeding and incomplete data loading safeguards | Implemented `/api/seed` endpoint and data cleaning (brands, dates, duplicate IDs)|
| **AI Search Pipeline** | Single-step search couldn't handle ambiguous queries | Built multi-step LLM pipeline with interpretation, web enrichment, and ranking |
| **Admin Account Creation** | No automatic default admin setup | Added FastAPI lifespan handler to create admin user on startup |
