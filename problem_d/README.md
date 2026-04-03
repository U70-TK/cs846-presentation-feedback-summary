# Problem D - SaaS Website
This problem contains a demo SaaS website with a NestJS backend, a React frontend, and a SQLite database folder.

## Layout
- `problem_d_backend/` NestJS API service (port `4000`, base path `api/`).
- `problem_d_frontend/` Vite frontend app (port `5173`).
- `problem_d_database/` SQLite database location.

## Notes

- Backend uses `problem_d_database/northwind_signal.sqlite` by default.
- Frontend expects backend on `http://localhost:4000`.
- The backend uses in-memory demo data for now.
- The database folder is a placeholder for the experiment's SQLite file.