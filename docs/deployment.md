# Deployment

Backend deployment expects:

- PostgreSQL database
- `DATABASE_URL`
- strong `SECRET_KEY`
- persistent upload storage path or object storage replacement
- allowed frontend origins in `ALLOWED_ORIGINS`

Run migrations before serving traffic.
