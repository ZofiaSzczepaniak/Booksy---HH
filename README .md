# AI-native Hardware Hub

The app for manage, rent and maintain equipment. 

---

## How to start

### 1. Backend (virtual environment) and setting the GROQ API key:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:GROQ_API_KEY = "your_api_key"
$env:SERPER_API_KEY= "your_api_key"
python -m uvicorn main:app --reload --port 8000
```

### 2. Seed the database (run once, in a second terminal)

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/seed -Method POST
```

### 3. Frontend

> Requires Node.js — download from [nodejs.org](https://nodejs.org) (LTS)

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

Default admin account created automatically on first startup:   

- **Username:** `admin`
- **Password:** `admin123`

---

## Fully Implemented Features


| Feature | Details |
|---|---|
| Login system | JWT-based auth, tokens stored in localStorage |
| Smart Dashboard | Full inventory with sort (all columns) and filter (status, brand, name) |
| My Rentals view | Each user sees only their own rented items; only they can return them |
| Rent / Return flow | Status guards — cannot rent broken/in-use gear; cannot return someone else's item |
| Admin: Hardware management | Add, edit, delete items; inline status toggle |
| Admin: User management | Create accounts (only way to gain access), delete users |
| AI Semantic Search | Natural language → AI anlyses the query, searches internet what type of hardware satisfies the query, matches with existing hardware after finding their specifications|
| AI Inventory Auditor | AI flags data issues: future dates, typos, unsafe notes, etc. |
---

## Running Tests

```powershell
cd backend
venv\Scripts\activate
pip install pytest
python -m pytest test_hardware.py -v
```

**24 tests across 3 groups — all passing:**

| Group | Count | What's covered |
|---|---|---|
| HardwareManager | 10 | add/retrieve, skip duplicate, reassign conflicting ID, normalize dates × 2, normalize status, normalize brand, delete, delete nonexistent, update |
| UserManager | 5 | register + login, wrong password, duplicate username, delete user, delete nonexistent |
| Rental logic (API) | 9 | rent available, cannot rent In Use, cannot rent Repair, return In Use, cannot return Available, unauthenticated blocked, user cannot add hardware, admin can add, full rent→return cycle|

---

## Shortcuts & "Hacks"

### 1. localStorage for sessions instead of HTTP-only cookies
- *Why acceptable for MVP:* Simple to implement, sufficient for an internal tool demo.
- *Production fix:* Use HTTP-only cookies with CSRF protection. JWTs in localStorage are vulnerable to XSS, never acceptable in a real app.


### 2. `assigned_to` text column instead of a proper rentals table
- *Why acceptable for MVP:* Enables the My Rentals feature and gives ownership enforcement with minimal schema change.
- *Production fix:* Add a `rentals` table: `(id, hardware_id, user_id, rented_at,due_to, returned_at)`. This gives a full audit trail, overdue detection, and usage statistics.

### 3. No pagination on the inventory list
- *Why acceptable for MVP:* 11 seed items. Works fine at this scale.
- *Production fix:* Add `?page=&limit=` query params to `GET /api/hardware` and a paginated table component on the frontend.

### 4. AI search suboptimality
- *Why acceptable for MVP:* The search for all item information at all search requesrts is simple to implement and fine for demo use with few items.
- *Production fix:* Run a single search of item specifics and keep the information for searches. Do it continuously when new item added.

---

## Partial / Missing

- **Rental history** — no record of past rentals (who had what, when, for how long);
- **Password change UI** — There is no possibility to change password for the user.
- **Rental deadlines** — No rental dates and deadlines, therefore limited planning control.
---

## Next Steps (24h Roadmap)

1. **Add a `rentals` history table** — `(id, hardware_id, user_id, rented_at, returned_at)` to replace the single `assigned_to` column. This unlocks audit trails, overdue tracking, and per-user rental history.

2. **HTTP-only cookie auth** — replace localStorage JWT with secure cookies and refresh token rotation. This is the single biggest security gap in the current implementation.

3. **Automatic specification and description generation** — The AI semantic search is at each time searching for information on all the hardware, in case of large database this would be suboptimal, instead keep track of descriptions of the products.

---




## Project Structure

```
Hardware_Manager/
├── backend/
│   ├── venv/                  # Python virtual environment
│   ├── main.py                # FastAPI app — routes, auth, AI endpoints
│   ├── items.py               # HardwareManager — CRUD + data normalisation
│   ├── users.py               # UserManager — registration, login, hashing
│   ├── test_hardware.py       # pytest test suite (24 tests)
│   ├── seed.json              # Initial inventory data (11 items)
│   ├── hardware.db            # SQLite database (auto-created on first run)
│   └── requirements.txt       # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── views/
    │   │   ├── LoginView.vue      # Login page
    │   │   ├── DashboardView.vue  # Inventory + My Rentals tabs
    │   │   └── AdminView.vue      # Hardware mgmt, user mgmt, AI Audit
    │   ├── stores/
    │   │   ├── auth.js            # Pinia store — JWT, login/logout
    │   │   └── toast.js           # Pinia store — toast notifications
    │   ├── router/
    │   │   └── index.js           # Vue Router — route guards
    │   ├── App.vue                # Root component — nav bar
    │   ├── main.js                # App entry point
    │   └── style.css              # Global styles
    ├── index.html
    ├── vite.config.js             # Vite config — /api proxy to :8000
    └── package.json
```

---

## Architecture

```
┌─────────────────────┐     HTTP/JSON      ┌──────────────────────┐
│   Vue 3 + Vite      │ ─────────────────▶│   FastAPI (Python)   │
│   Pinia (state)     │                    │   Uvicorn            │
│   Vue Router        │ ◀─────────────────│   JWT auth           │
└─────────────────────┘                    └──────────┬───────────┘
                                                      │
                                           ┌──────────▼───────────┐
                                           │  SQLite (hardware.db)│
                                           │  • hardware table    │
                                           │  • users table       │
                                           └──────────┬───────────┘
                                                      │
                                           ┌──────────▼───────────┐
                                           │   AI Services        │
                                           │   GROQ API           │
                                           │   llama-3.1-8b       │
                                           │   • Semantic Search  │
                                           │   • Inventory Audit  │
                                           │   Serper API         │
                                           │   • Web enrichment   │
                                           └──────────────────────┘
```

---


