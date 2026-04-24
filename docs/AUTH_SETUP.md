# Frontend Clerk Configuration

Create a `.env.local` file in the `frontend/` directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_CLERK_KEY
CLERK_SECRET_KEY=sk_test_YOUR_CLERK_SECRET
```

## Setup Steps

1. Create a Clerk account at https://dashboard.clerk.com
2. Create an application
3. Get your Publishable Key and Secret Key
4. Add them to `.env.local`

## API Integration

The backend validates Clerk tokens using:

```python
from clerk_backend_api import Clerk

clerk_client = Clerk(api_key=CLERK_SECRET_KEY)
```

## Role-Based Access Control

Users can have roles assigned in Clerk:
- **admin**: Full access (read, write, delete, train, manage users)
- **analyst**: Can train and modify (read, write, train)
- **viewer**: Read-only access

These are stored in Clerk's custom claims and validated on every request.

## Multi-Tenant Isolation

Each tenant's data is isolated at the database level:
- All queries filter by `tenant_id`
- API responses only show tenant's own data
- Audit logs track all access
