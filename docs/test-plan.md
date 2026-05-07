# Test Plan

Manual Swagger flow:

1. Create admin user through a seed script or temporary database insert.
2. Log in at `/auth/login`.
3. Create landlord user and landlord profile.
4. Create property, room, and public listing.
5. Submit public viewing request and application.
6. Approve and assign the application.
7. Confirm room becomes occupied and listing leaves public search.
8. Submit and approve payment proof.
9. Check dashboard summary and audit logs.
