# AI Intent Radar — Handoff TODO

You are taking over development of this project. Read this entire file before touching any code.
Execute every incomplete task in order. Do not skip anything. Do not ask the user — just do it.

---

## Project Overview

AI Intent Radar is a commercial intelligence platform that ingests signals from the web (Hacker News, Google News, SEC EDGAR), scores them with AI, surfaces business opportunities, matches providers to those opportunities, and lets users send shareable briefing links to providers who can respond with interest.

---

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, React Query (`@tanstack/react-query`) — deployed on Vercel at https://ai-intent-radar.vercel.app
- **Backend**: FastAPI (Python 3.9), SQLAlchemy async, Pydantic v2 — deployed on Render at https://ai-intent-radar.onrender.com
- **DB**: Neon PostgreSQL — `ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb`
- **Cache**: Upstash Redis
- **Repo**: https://github.com/DesloWeb/ai-intent-radar
- **Local path**: `/Users/ravnit/Desktop/AI-SIR`
- **Python venv**: `/Users/ravnit/Desktop/AI-SIR/backend/venv/bin/python3.9`
- **OS**: macOS (darwin), shell: bash

---

## Deployment

- **Push to `main`** → Render auto-deploys backend, Vercel auto-deploys frontend. No manual steps needed.
- Backend health: `curl -s https://ai-intent-radar.onrender.com/health` → `{"status":"ok","version":"1.0.0"}`
- Frontend: https://ai-intent-radar.vercel.app
- OpenAPI docs: https://ai-intent-radar.onrender.com/docs

---

## Bash Commands Reference

### Navigation
```bash
# Project root
cd /Users/ravnit/Desktop/AI-SIR

# Frontend
cd /Users/ravnit/Desktop/AI-SIR/frontend

# Backend
cd /Users/ravnit/Desktop/AI-SIR/backend
```

### Git
```bash
# Check what's changed
git -C /Users/ravnit/Desktop/AI-SIR status
git -C /Users/ravnit/Desktop/AI-SIR log --oneline -10
git -C /Users/ravnit/Desktop/AI-SIR diff HEAD

# Commit and push (run from project root)
cd /Users/ravnit/Desktop/AI-SIR && git add . && git commit -m "your message" && git push
```

### Frontend
```bash
# Install dependencies
cd /Users/ravnit/Desktop/AI-SIR/frontend && npm install

# Type-check only (fast, no build output)
cd /Users/ravnit/Desktop/AI-SIR/frontend && npx tsc --noEmit

# Full production build (catches all errors — run this before committing)
cd /Users/ravnit/Desktop/AI-SIR/frontend && npm run build

# Run dev server locally on port 3000
cd /Users/ravnit/Desktop/AI-SIR/frontend && npm run dev
```

### Backend
```bash
# Run tests
cd /Users/ravnit/Desktop/AI-SIR/backend && /Users/ravnit/Desktop/AI-SIR/backend/venv/bin/python3.9 -m pytest tests/ -v

# Run a single test file
cd /Users/ravnit/Desktop/AI-SIR/backend && /Users/ravnit/Desktop/AI-SIR/backend/venv/bin/python3.9 -m pytest tests/test_auth.py -v

# Run dev server locally on port 8080
cd /Users/ravnit/Desktop/AI-SIR/backend && /Users/ravnit/Desktop/AI-SIR/backend/venv/bin/python3.9 -m uvicorn app.main:app --reload --port 8080

# Install a new Python package
/Users/ravnit/Desktop/AI-SIR/backend/venv/bin/pip install <package>
```

### Database (replace PASSWORD with Neon password)
```bash
# Interactive session
psql 'postgresql://neondb_owner:PASSWORD@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'

# One-liner query
psql 'postgresql://neondb_owner:PASSWORD@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require' -c "SELECT COUNT(*) FROM opportunities;"

# List all tables
psql 'postgresql://neondb_owner:PASSWORD@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require' -c "\dt"

# Check columns on a table
psql 'postgresql://neondb_owner:PASSWORD@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require' -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'provider_briefs' ORDER BY column_name;"
```

### Live API testing
```bash
# Login and store token
RESPONSE=$(curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com","password":"testpass123"}')
TOKEN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Health check
curl -s https://ai-intent-radar.onrender.com/health

# Trigger ingest
curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/signals/ingest/all" -H "Authorization: Bearer $TOKEN"

# List opportunities
curl -s "https://ai-intent-radar.onrender.com/api/v1/opportunities?per_page=5" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# List briefs
curl -s "https://ai-intent-radar.onrender.com/api/v1/briefs" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test change-password endpoint (once built)
curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/auth/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"testpass123","new_password":"newpass456"}' | python3 -m json.tool
```

---

## Key File Locations

```
/Users/ravnit/Desktop/AI-SIR/
├── frontend/src/
│   ├── app/
│   │   ├── dashboard/page.tsx          ← dashboard (Refresh Data button already added)
│   │   ├── opportunities/
│   │   │   ├── page.tsx                ← opportunities list
│   │   │   └── [id]/page.tsx           ← opportunity detail (brief status already added)
│   │   ├── providers/page.tsx          ← providers list + add form
│   │   ├── briefs/page.tsx             ← briefs page (ALREADY WRITTEN, needs verification)
│   │   ├── brief/[token]/page.tsx      ← public brief page (no auth, for providers)
│   │   ├── settings/page.tsx           ← DOES NOT EXIST YET — needs to be created
│   │   ├── market-intelligence/page.tsx
│   │   └── auth/login/page.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx             ← nav links (needs Briefs + Settings links added)
│   │   │   ├── AppShell.tsx            ← wraps all pages, includes Sidebar
│   │   │   └── Header.tsx
│   │   └── ui/
│   │       ├── Card.tsx
│   │       ├── ScoreBar.tsx
│   │       ├── UrgencyBadge.tsx
│   │       └── EmptyState.tsx
│   ├── hooks/useAuth.ts                ← exposes: user, isAuthenticated, isLoading, logout
│   ├── lib/api.ts                      ← ALL API calls go here (already has changePassword + updateProfile)
│   └── types/index.ts                  ← shared TypeScript types
├── backend/app/
│   ├── api/v1/
│   │   ├── auth.py                     ← needs PATCH /me and POST /change-password added
│   │   ├── briefs.py                   ← fully implemented (list_briefs updated to return opportunity_title)
│   │   ├── opportunities.py
│   │   ├── providers.py
│   │   └── signals.py
│   ├── models/models.py                ← SQLAlchemy models
│   ├── services/
│   │   └── feedback_service.py         ← org ownership check already fixed
│   └── core/
│       ├── security.py                 ← has verify_password, get_password_hash, get_current_user
│       └── database.py
└── TODO_HANDOFF.md                     ← this file
```

---

## What Is Already Done (do NOT redo)

- Signal ingestion (HN, Google News, SEC EDGAR) + AI pipeline
- Opportunities list + detail pages
- Contact modal (4 channels), provider matching, feedback buttons
- Provider brief system (generate links, public page, respond Interested/Not Interested)
- Providers page with email + phone fields
- Auth (JWT, RBAC, refresh tokens, brute-force protection, logout)
- Security (org scoping, audit logs, security headers, honeypot)
- Auto-ingest GitHub Actions (every 6 hours)
- About / Contact / Privacy pages
- ✅ **Refresh Data button** on dashboard — calls `api.ingestAll()` → `POST /signals/ingest/all`
- ✅ **Brief status inline** on opportunity detail — shows Interested/Not Interested/Awaiting Response badge per match
- ✅ **Feedback org check** — `backend/app/services/feedback_service.py` verifies org ownership
- ✅ **briefs/page.tsx** — fully written (see Task 3 below for verification steps)
- ✅ **api.ts updated** — `getBriefs()` returns full fields, `changePassword()` and `updateProfile()` methods exist
- ✅ **briefs.py backend updated** — `list_briefs` JOINs Opportunity table, returns `opportunity_title`, `provider_name`, `provider_email`, `provider_message`, `responded_at`

---

## Tasks To Complete (in order)

---

### TASK 3 — Verify /briefs page works [ WRITTEN, NEEDS VERIFICATION ]

The page at `frontend/src/app/briefs/page.tsx` is already fully written. You need to:

1. **Type-check it compiles:**
```bash
cd /Users/ravnit/Desktop/AI-SIR/frontend && npx tsc --noEmit 2>&1 | head -40
```

2. **Fix any TypeScript errors** — the `Brief` interface in `briefs/page.tsx` must match the return type of `api.getBriefs()` in `api.ts`. Both should have these fields:
   ```ts
   id, token, public_url, expires_at, status, view_count, created_at,
   opportunity_id, opportunity_title?, provider_match_id,
   provider_name?, provider_email?, provider_message?, responded_at?
   ```

3. If there are errors, read the actual file content and fix the type mismatch.

4. Once it compiles, move on to Task 4.

---

### TASK 4 — Add Briefs + Settings links to Sidebar [ NOT STARTED ]

**File**: `frontend/src/components/layout/Sidebar.tsx`

Read the file first, then make these two changes:

**Change 1 — Add `FileText` to lucide-react imports:**
The current import line is:
```ts
import { LayoutDashboard, Target, Radio, Globe, Users, Settings, LogOut, Radar } from 'lucide-react';
```
Add `FileText` to that import.

**Change 2 — Update navItems array:**
Replace the current `navItems` with:
```ts
const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/opportunities', label: 'Opportunities', icon: Target },
  { href: '/market-intelligence', label: 'Market Intelligence', icon: Globe },
  { href: '/providers', label: 'Providers', icon: Users },
  { href: '/briefs', label: 'Provider Briefs', icon: FileText },
  { href: '/settings', label: 'Settings', icon: Settings },
];
```

**Optional — pending badge on Briefs link:**
Inside the `Sidebar` component, add a query for pending briefs count and show a badge:
```tsx
const { isAuthenticated } = useAuth();
const { data: briefs = [] } = useQuery({
  queryKey: ['briefs'],
  queryFn: () => api.getBriefs(),
  enabled: isAuthenticated,
  staleTime: 30000,
});
const pendingCount = briefs.filter((b: any) => b.status === 'pending').length;
```
Then in the nav item render, when `href === '/briefs'` and `pendingCount > 0`, render a badge:
```tsx
{href === '/briefs' && pendingCount > 0 && (
  <span className="ml-auto text-[10px] font-bold bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded-full">
    {pendingCount}
  </span>
)}
```
You'll need to add `import { useQuery } from '@tanstack/react-query'` and `import { api } from '@/lib/api'` at the top of Sidebar.tsx.

---

### TASK 5 — Build Settings page [ NOT STARTED ]

**File to create**: `frontend/src/app/settings/page.tsx`

The file does NOT exist. Create it from scratch. Use `AppShell` as the wrapper (same as every other page). Match the style of `frontend/src/app/providers/page.tsx`.

The page needs two sections inside `Card` components:

**Section 1 — Account Details**
- Pre-fill Full Name and Email from `useAuth().user`
- Save button calls `api.updateProfile({ full_name, email })`
- Show an inline success message ("Profile updated") or error on response

**Section 2 — Change Password**
- Three fields: Current Password, New Password, Confirm New Password
- Validate `newPassword === confirmPassword` before calling API, show inline error if not
- Save button calls `api.changePassword(currentPassword, newPassword)`
- Show success ("Password changed") or error message inline
- Clear all fields on success

Both `api.changePassword` and `api.updateProfile` are already in `frontend/src/lib/api.ts`.

**BUT** — the backend endpoints don't exist yet. You also need to add them to `backend/app/api/v1/auth.py`.

**Step 1 — Read `backend/app/api/v1/auth.py`** to understand the existing patterns (schemas, router, imports).

**Step 2 — Add these Pydantic schemas** near the top of `auth.py` with the other schemas:
```python
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
```

**Step 3 — Add these two endpoints** to `auth.py` (after the existing `/me` GET endpoint):
```python
@router.patch("/me")
async def update_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update current user's profile."""
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        # Check email not already taken by another user
        existing = await db.execute(
            select(User).where(User.email == payload.email, User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = payload.email
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Change current user's password."""
    from app.core.security import verify_password, get_password_hash
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}
```

**Step 4 — Create `frontend/src/app/settings/page.tsx`** using `useMutation` for both forms. Here is a complete working implementation to use as reference:

```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';
import { User, Lock, CheckCircle, AlertCircle } from 'lucide-react';

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.replace('/auth/login');
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const profileMutation = useMutation({
    mutationFn: () => api.updateProfile({ full_name: fullName, email }),
    onSuccess: () => setProfileMsg({ type: 'success', text: 'Profile updated successfully.' }),
    onError: (e: any) => setProfileMsg({ type: 'error', text: e.message || 'Failed to update profile.' }),
  });

  const passwordMutation = useMutation({
    mutationFn: () => api.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      setPasswordMsg({ type: 'success', text: 'Password changed successfully.' });
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
    },
    onError: (e: any) => setPasswordMsg({ type: 'error', text: e.message || 'Failed to change password.' }),
  });

  const handlePasswordSubmit = () => {
    setPasswordMsg(null);
    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }
    if (newPassword.length < 8) {
      setPasswordMsg({ type: 'error', text: 'Password must be at least 8 characters.' });
      return;
    }
    passwordMutation.mutate();
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your account details and password.</p>
      </div>

      <div className="max-w-xl space-y-6">
        {/* Account Details */}
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <User className="w-4 h-4" /> Account Details
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
              />
            </div>
            {profileMsg && (
              <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${profileMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                {profileMsg.type === 'success' ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {profileMsg.text}
              </div>
            )}
            <button
              onClick={() => { setProfileMsg(null); profileMutation.mutate(); }}
              disabled={profileMutation.isPending}
              className="px-4 py-2 bg-radar-600 hover:bg-radar-700 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
            >
              {profileMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </Card>

        {/* Change Password */}
        <Card>
          <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Lock className="w-4 h-4" /> Change Password
          </h2>
          <div className="space-y-4">
            {(['Current Password', 'New Password', 'Confirm New Password'] as const).map((label, i) => {
              const val = [currentPassword, newPassword, confirmPassword][i];
              const setter = [setCurrentPassword, setNewPassword, setConfirmPassword][i];
              return (
                <div key={label}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                  <input
                    type="password"
                    value={val}
                    onChange={e => setter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-radar-400"
                  />
                </div>
              );
            })}
            {passwordMsg && (
              <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${passwordMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
                {passwordMsg.type === 'success' ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {passwordMsg.text}
              </div>
            )}
            <button
              onClick={handlePasswordSubmit}
              disabled={passwordMutation.isPending}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
            >
              {passwordMutation.isPending ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
```

---

### TASK 6 — Type-check, build, commit and push [ NOT STARTED ]

After Tasks 3, 4, and 5 are done:

**Step 1 — Type-check frontend:**
```bash
cd /Users/ravnit/Desktop/AI-SIR/frontend && npx tsc --noEmit 2>&1
```
Fix any errors before proceeding.

**Step 2 — Run backend tests:**
```bash
cd /Users/ravnit/Desktop/AI-SIR/backend && /Users/ravnit/Desktop/AI-SIR/backend/venv/bin/python3.9 -m pytest tests/ -v 2>&1
```
Fix any failures before proceeding.

**Step 3 — Commit and push:**
```bash
cd /Users/ravnit/Desktop/AI-SIR && git add . && git commit -m "Add briefs page, settings page, sidebar nav links, brief status inline" && git push
```

**Step 4 — Verify deployment:**
Wait ~2 minutes for Render to deploy, then:
```bash
curl -s https://ai-intent-radar.onrender.com/health
```
Should return `{"status":"ok","version":"1.0.0"}`.

Then log in via the live API and test the new endpoints:
```bash
RESPONSE=$(curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com","password":"testpass123"}')
TOKEN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Test PATCH /me
curl -s -X PATCH "https://ai-intent-radar.onrender.com/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User"}' | python3 -m json.tool

# Test briefs list
curl -s "https://ai-intent-radar.onrender.com/api/v1/briefs" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Code Patterns to Follow

**Frontend page template:**
```tsx
'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AppShell } from '@/components/layout/AppShell';
import { Card } from '@/components/ui/Card';

export default function SomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.replace('/auth/login');
  }, [isAuthenticated, authLoading, router]);

  if (authLoading || !isAuthenticated) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin w-8 h-8 border-4 border-radar-500 border-t-transparent rounded-full" />
    </div>;
  }

  return <AppShell>{/* content */}</AppShell>;
}
```

**API call pattern (mutation):**
```tsx
import { useMutation } from '@tanstack/react-query';
const mutation = useMutation({
  mutationFn: () => api.someMethod(data),
  onSuccess: (result) => { /* handle */ },
  onError: (e: any) => { /* handle e.message */ },
});
```

**Backend endpoint pattern:**
```python
@router.post("/some-endpoint")
async def some_endpoint(
    payload: SomeSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),  # remove if public endpoint
):
    # always scope queries to user.organization_id
    result = await db.execute(select(Model).where(Model.organization_id == user.organization_id))
    ...
    await db.commit()
    return response
```

---

## Notes

- `Settings` icon is already imported in `Sidebar.tsx` — just add it to `navItems`
- `useAuth()` returns `{ user, isAuthenticated, isLoading, logout }` — `user` has `full_name` and `email`
- The `User` type is in `frontend/src/types/index.ts`
- `radar-500`, `radar-600`, `radar-700` etc. are custom Tailwind colors already configured
- All API methods go in `frontend/src/lib/api.ts` — never use raw `fetch` in components
- Org scoping: every backend query that touches user data MUST filter by `user.organization_id`
- Render free tier spins down after inactivity — first request may take 30-60 seconds
