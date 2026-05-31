# Rentalink

Rentalink is a national rental governance and smart property operations platform designed for Lesotho rental ecosystems, student accommodations, line-houses, apartments, and property management operations.

The platform helps:
- National housing administrators oversee rental ecosystems
- District administrators manage landlord onboarding and compliance
- Landlords manage approved rental operations
- Caretakers assist operational management
- Tenants securely occupy assigned rooms
- Public users discover verified vacant rooms online

Rentalink transforms fragmented manual rental operations into a secure, scalable, and intelligent digital infrastructure.

---

# Vision

Rentalink aims to become the national digital rental infrastructure for Lesotho and beyond by modernizing:

- rental governance
- property operations
- tenant onboarding
- room allocation
- rent management
- listing verification
- maintenance coordination
- payment integration
- occupancy intelligence

---

# Core Problems Solved

Traditional rental operations often rely on:

- walking around villages searching for rooms
- paper records
- WhatsApp messages
- informal verbal agreements
- poor occupancy tracking
- weak landlord verification
- no centralized governance
- manual rent collection

Rentalink digitizes and secures these workflows into one controlled platform.

---

# Platform Architecture

Rentalink uses a hierarchical governance architecture.

```text
National Admin
    ↓
District Admin
    ↓
Landlord
    ↓
Caretaker (optional)
    ↓
Tenant
```

---

# Roles and Responsibilities

## National Admin

Highest authority in the platform.

Responsibilities:
- create district admins
- oversee national rental operations
- monitor system-wide risks
- verify district governance
- oversee payment infrastructure
- manage platform subscriptions
- manage listing verification systems
- monitor fraud and abuse
- manage AI risk intelligence

---

## District Admin

District-level rental authority.

Responsibilities:
- onboard and approve landlords
- create approved property records
- allocate room capacity
- monitor district rental operations
- oversee district compliance
- handle landlord verification
- manage district rental disputes
- review suspicious activities

District admins operate only within assigned districts.

---

## Landlord

Approved property owner/operator.

Responsibilities:
- manage approved properties
- manage approved room inventory
- onboard tenants
- assign tenants to rooms
- manage payments
- manage maintenance
- manage caretakers
- manage occupancy operations

Landlords cannot create unlimited tenant accounts.

Tenant capacity is restricted by room availability.

```text
active_tenants <= total_rooms
```

---

## Caretaker (Optional)

Operational assistant assigned by landlord.

Responsibilities:
- assist tenant operations
- assist maintenance coordination
- manage room status updates
- assist occupancy workflows
- monitor operational issues

Caretakers operate only within assigned landlord/property scope.

---

## Tenant

Assigned occupant of a verified room.

Tenants can:
- access tenant portal
- view rent obligations
- submit payment confirmations
- receive notifications
- request support
- monitor occupancy information

Tenants can access only their own records.

---

## Public Visitor

Unauthenticated public user.

Public users can:
- search vacant rooms
- filter listings
- request viewings
- submit rental applications

Public users cannot access internal management operations.

---

# Public Room Finder

Rentalink includes a public room discovery system.

Users can:
- browse available rooms
- filter by district
- filter by location
- filter by room type
- filter by price
- filter by occupancy type
- view verified listings
- apply for rooms
- request room viewings

This removes the need to physically search villages for vacancies.

---

# Tenant Onboarding Workflow

## Step 1 — Public Discovery

A public user discovers a vacant verified listing.

---

## Step 2 — Application

The applicant submits:
- personal details
- contact information
- application request

Applications are tied to:
- listing_id
- room_id
- property_id
- landlord_id

---

## Step 3 — Review

Landlord or caretaker reviews the application.

Possible actions:
- approve
- reject
- request additional information

---

## Step 4 — Tenant Assignment

Once approved:
- tenant account is created
- occupancy is created
- room becomes occupied
- listing becomes hidden
- rent workflow begins

---

# Occupancy Enforcement

Rentalink enforces room occupancy limits.

Example:

```text
20 rooms = maximum 20 active tenants
```

The system prevents:
- over-allocation
- fake occupancy
- unlimited tenant creation
- ghost tenant records

---

# Security Architecture

Rentalink uses strict multi-tenant isolation.

## Isolation Rules

### National Admin
- full system visibility

### District Admin
- district-scoped access only

### Landlord
- landlord-scoped access only

### Caretaker
- delegated scoped access only

### Tenant
- self-data access only

### Public User
- public listings only

---

# AI Risk and Governance

Rentalink includes intelligent operational monitoring.

Capabilities include:
- suspicious activity monitoring
- occupancy anomaly detection
- payment risk detection
- fraudulent listing monitoring
- verification intelligence
- governance visibility
- operational audit logging

---

# Payment Infrastructure

Rentalink includes MoPay payment integration scaffolding.

Supported payment flows:
- M-Pesa
- EcoCash
- bank transfers
- card payments
- rent payments
- deposits
- landlord subscriptions

Rentalink never stores:
- card PINs
- M-Pesa PINs
- EcoCash secrets
- wallet credentials

Sensitive credentials remain only in secure environment variables.

---

# Progressive Web App (PWA)

Rentalink supports installable app behavior.

Features:
- installable on phones
- mobile-friendly
- responsive dashboards
- offline-ready architecture preparation
- app manifest support
- service worker support

---

# Technology Stack

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT Authentication

---

## Frontend

- React
- Vite
- TypeScript
- CSS modules/global styling

---

## Deployment

- Render (Backend)
- Vercel (Frontend)
- Neon PostgreSQL

---

# Deployment Overview

## Backend

Production backend runs on Render.

Start command:

```bash
alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Frontend

Frontend runs on Vercel.

Build command:

```bash
npm run build
```

Output directory:

```text
dist
```

---

# Required Backend Environment Variables

```env
APP_ENV=production
SEED_DEMO_DATA=false

DATABASE_URL=your-database-url

SECRET_KEY=your-secret-key

ADMIN_EMAIL=your-email
ADMIN_PASSWORD=your-password
ADMIN_FULL_NAME=Phomolo Matsoso

ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

PUBLIC_BASE_URL=https://your-backend-domain.onrender.com
```

---

# Production Setup

Rentalink production environments do not rely on demo users.

The seed system creates:
- initial national admin only

Demo data is skipped in production.

---

# Production User Identifiers

Example identifiers:

```text
RL-NAT-000001
RL-DADM-000001
RL-LND-000001
RL-CRT-000001
RL-TNT-000001
```

---

# Repository Security

Never:
- commit `.env`
- expose secrets
- expose internal deployment notes
- expose database credentials
- expose payment credentials

---

# Security Recommendations

## Production Requirements

- strong SECRET_KEY
- HTTPS only
- production database isolation
- secure environment variables
- no demo data in production
- restricted admin access
- two-factor authentication support

---

# Deployment Troubleshooting

## Python Version

Use Python 3.11.x in production.

Avoid unsupported production builds with newer unstable versions.

---

## Database Reset Warning

Never automatically drop schemas in production startup code.

If a database becomes corrupted during development:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

Use only for empty development databases.

---

# Current Production Infrastructure

## Frontend

```text
https://rentalink.app
```

---

## Backend

```text
https://rentalink.onrender.com
```

---

# Roadmap

## Planned Features

- React Native mobile application
- digital lease agreements
- AI operational intelligence
- smart rental analytics
- SMS notifications
- email notifications
- advanced payment automation
- document uploads
- maintenance workflows
- landlord subscription billing
- district intelligence dashboards
- national rental intelligence systems

---

# Rentalink Mission

Rentalink is building secure, intelligent, and scalable digital rental infrastructure for Africa.
