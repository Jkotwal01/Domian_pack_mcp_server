# Domain Pack Generator — Frontend

> **React + Vite** SPA for conversational domain pack management.

---

## 📋 Table of Contents

- [Developer Setup Guide](#developer-setup-guide)
- [Environment Variables](#environment-variables)
- [Common Commands](#common-commands)
- [Project Structure](#project-structure)

---

## Developer Setup Guide

### Prerequisites

| Requirement | Version |
|---|---|
| Node.js | 18 or higher |
| npm | 9 or higher |
| Backend server | Running at `http://localhost:8000` |

---

### Step 1 — Navigate to Frontend Directory

```bash
cd domain-pack-mcp/frontend
```

---

### Step 2 — Install Dependencies

```bash
npm install
```

---

### Step 3 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

> **Note**: All Vite environment variables must be prefixed with `VITE_` to be accessible in the browser.

---

### Step 4 — Start the Dev Server

```bash
npm run dev
```

The app will be available at [http://localhost:5173](http://localhost:5173) with Hot Module Replacement (HMR) enabled.

---

### Step 5 — Verify Setup

1. Open [http://localhost:5173](http://localhost:5173).
2. Register a new account via the Signup page.
3. Log in and verify the Dashboard loads your domains.
4. Create a domain and open `ConfigView`.
5. Send a chat message like: *"Add an entity called Customer with a name attribute."*
6. Confirm the patch to verify the full flow works.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

---

## Common Commands

| Task | Command |
|---|---|
| Start dev server | `npm run dev` |
| Build for production | `npm run build` |
| Preview production build | `npm run preview` |
| Lint code | `npm run lint` |
| Install new package | `npm install <package>` |

---

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── pages/                  # Top-level route pages
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   ├── Dashboard.jsx
│   │   ├── ConfigView.jsx
│   │   └── Monitoring.jsx
│   ├── components/
│   │   ├── ChatArea.jsx
│   │   ├── InputArea.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── IntentConfirmation.jsx
│   │   ├── ToolCallDisplay.jsx
│   │   ├── YAMLViewer.jsx
│   │   ├── Sidebar.jsx
│   │   ├── FileAttachment.jsx
│   │   ├── FileUploadButton.jsx
│   │   ├── FileUploadLoader.jsx
│   │   ├── TypingIndicator.jsx
│   │   ├── Onboarding.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── GuestRoute.jsx
│   │   ├── common/
│   │   ├── domain/
│   │   ├── modals/
│   │   └── sections/
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── hooks/
│   ├── services/
│   │   └── api.js
│   ├── utils/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```