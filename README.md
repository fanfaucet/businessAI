# AnnabanAI Business Suite

AnnabanAI Business Suite is a full-stack starter platform for business-focused AI automation. It includes an Express + Prisma backend, PostgreSQL schema, JWT-based authentication, modular plugin management, OpenAI-powered insight generation, and a React dashboard for business users, analysts, and administrators.

## Architecture overview

### Backend
- Express REST API with the following routes:
  - `POST /auth/signup`
  - `POST /auth/login`
  - `POST /data/submit`
  - `GET /insights/ai`
  - `GET /plugins`
  - `POST /plugins/load`
- JWT authentication and role-based authorization middleware.
- Prisma schema for PostgreSQL with `User`, `BusinessData`, `Insight`, and `Plugin` models.
- OpenAI integration with fallback insight generation when no API key is configured.
- Plugin registry that allows modular intelligence utilities to transform business payloads.

### Frontend
- React + Vite single-page application.
- Login and signup experience.
- Dashboard containing:
  - business data submission form,
  - AI insight panel,
  - plugin manager.

## Project structure

```text
.
├── backend/
│   ├── src/
│   └── .env.example
├── frontend/
│   ├── src/
│   └── .env.example
├── prisma/
│   └── schema.prisma
└── package.json
```

## Environment setup

### 1. Install dependencies

```bash
npm install
npm run install:all
```

### 2. Configure environment variables

Backend:

```bash
cp backend/.env.example backend/.env
```

Frontend:

```bash
cp frontend/.env.example frontend/.env
```

Update these values before running locally:

- `DATABASE_URL`: PostgreSQL connection string.
- `JWT_SECRET`: strong random string for signing tokens.
- `OPENAI_API_KEY`: optional, enables live LLM analysis.
- `OPENAI_MODEL`: optional, defaults to `gpt-4o-mini`.
- `CORS_ORIGIN`: frontend origin.
- `VITE_API_BASE_URL`: backend base URL.

### 3. Prepare the database

Generate Prisma client and create the schema in PostgreSQL:

```bash
npm run prisma:generate
npm run prisma:migrate
```

### 4. Run the application

Run backend and frontend together:

```bash
npm run dev
```

Or run each service separately:

```bash
npm run dev --workspace backend
npm run dev --workspace frontend
```

- Backend: `http://localhost:4000`
- Frontend: `http://localhost:5173`

## API usage notes

### Authentication
- Create a user with `POST /auth/signup` using `{ "name", "email", "password", "role" }`.
- Login with `POST /auth/login` using `{ "email", "password" }`.
- Pass the JWT as `Authorization: Bearer <token>` for protected routes.

### Business data submission
Send JSON payloads with business metrics to `POST /data/submit`:

```json
{
  "jsonPayload": {
    "revenue": 120000,
    "expenses": 83000,
    "activeClients": 145,
    "churnRate": 4.2,
    "satisfactionScore": 8.9
  }
}
```

### AI insights
Call `GET /insights/ai` after submitting data. The platform will:
- fetch the latest business payload for the authenticated user,
- apply active plugins,
- call OpenAI when `OPENAI_API_KEY` is configured,
- persist the generated insight.

### Plugin management
- `GET /plugins` lists available and active plugins.
- `POST /plugins/load` enables a plugin by registry key, for example:

```json
{
  "key": "revenuePulse",
  "config": {
    "activatedFromUi": true
  }
}
```

## Security and implementation notes

- Passwords are hashed with `bcryptjs`.
- JWT tokens expire after 8 hours.
- Role checks protect data submission, insight generation, and plugin loading.
- Sensitive configuration is kept in environment variables.
- API responses return JSON with appropriate HTTP status codes.

## Suggested next steps

- Add automated tests for route, service, and component behavior.
- Add refresh tokens and stronger session lifecycle management.
- Expand the plugin registry to dynamically load packages or tenant-specific modules.
- Add charts, audit logs, and analytics exports to the dashboard.
