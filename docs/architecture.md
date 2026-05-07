# LineLink Architecture

LineLink is organized as a modular API-first platform.

- Backend: FastAPI routers, SQLAlchemy models, Alembic migrations, JWT auth, role-based access control, landlord ownership filtering.
- Frontend: React/Vite workspace prepared for admin, landlord, caretaker, tenant, and public pages.
- Mobile: React Native/Expo workspace reserved for tenant, landlord, and caretaker apps.

The backend keeps routing out of `main.py`; each business area owns its router under `backend/app/routers`.
