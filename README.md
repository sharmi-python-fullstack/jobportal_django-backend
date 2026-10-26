# CareerLane Job Portal

CareerLane is a React and Django REST Framework job portal. Visitors can search
and filter job listings; registered users can sign in, upload a resume, apply
for jobs, and review their applications.

## Run locally on Windows

Open two PowerShell terminals from the project root (the folder containing
`manage.py`).

### Django API

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`. The health check is
`http://127.0.0.1:8000/`.

### React frontend

```powershell
cd .\job-portal-frontend
npm install
npm start
```

Open `http://localhost:3000`. The frontend uses
`REACT_APP_API_URL` to find the API; without it, it defaults to
`http://localhost:8000/api`.

## Deploy a free demo on Render

The root `render.yaml` Blueprint describes the Django API, React static site,
and a free PostgreSQL database. It is intended for a project demo, not
production: free API instances sleep when idle, the free database expires
after 30 days, and local resume uploads are lost when the API restarts or
redeploys. Render may apply usage limits; check its current free-plan terms.
For durable user data and resume files, use paid persistent services and
configure private S3-compatible object storage.

### 1. Put the project root in a Git repository

Render must be able to access the repository containing `render.yaml`,
`manage.py`, and both application folders. Connect that repository to your
Render account. Do not commit `.env.local`, `.venv`, `node_modules`,
`db.sqlite3`, or credentials. If the React folder has its own nested Git
repository, make sure the root repository contains the React source files as
normal files rather than a Git submodule.

**Workspace setup note:** this project root is not currently a Git repository,
and the React folder has its own Git repository. Create or select a repository
for the whole project before connecting Render; do not connect Render to only
the React folder because that would omit the Django API and `render.yaml`.

### 2. Create the Blueprint

In Render, choose **New > Blueprint**, connect the repository, and select the
repository root. Review the resources and choose the free plans. The Blueprint
creates `careerlane-api`, `careerlane-frontend`, and `careerlane-db`. Render
will build and deploy them; migrations run when the API starts.

The frontend's `REACT_APP_API_URL` and API's `CORS_ALLOWED_ORIGINS` are
intentionally left as dashboard values because Render assigns the public
hostnames. After the first deploy:

1. Copy the API service URL from Render, such as
   `https://careerlane-api.onrender.com`.
2. In the **careerLane-frontend** Static Site environment settings, set
   `REACT_APP_API_URL` to `https://<API-hostname>/api` (include `/api`).
   Save the change and trigger a new frontend deploy; Create React App embeds
   this value at build time.
3. In the **careerlane-api** Web Service environment settings, set
   `CORS_ALLOWED_ORIGINS` to the exact frontend origin, such as
   `https://careerlane-frontend.onrender.com` (no `/` or path). Save the
   change and let the API redeploy.
4. Visit the frontend URL. The API health check is at the API URL `/`, and the
   job-list endpoint is `/api/jobs/`.

Render generates `DJANGO_SECRET_KEY` and connects the database automatically.
The API also recognizes Render's `RENDER_EXTERNAL_HOSTNAME` setting for
`ALLOWED_HOSTS`. Do not place secrets in the frontend environment or commit
them to Git.

### 3. Create the first account and jobs

Register through the deployed frontend. The project has no sample job records;
create jobs through the authenticated `POST /api/jobs/` endpoint before
testing applications.

## Important deployment notes

- Render account access, repository connection, domains, and environment
  variables must be configured in your own Render account. Do not share account
  tokens or database credentials.
- Local development uses SQLite. The Render Blueprint uses PostgreSQL; the
  free database expires after 30 days, so do not use it for irreplaceable data.
- The demo allows resume uploads to Render's temporary filesystem. They can be
  lost at any restart, sleep, or redeploy. Production needs persistent object
  storage; configure an S3-compatible private bucket and remove
  `ALLOW_EPHEMERAL_MEDIA`.
- The project contains no sample job records. Create jobs through the API as an
  authenticated recruiter or add them through Django admin after creating a
  superuser.
- The current Create React App toolchain (`react-scripts` 5) has upstream npm
  audit advisories. A non-breaking `npm audit fix` cannot resolve them; migrating
  to a maintained build tool would be a separate major change. The advisories
  affect the build/development dependency tree, not the generated static files.
- Production checklist: confirm the API health URL, frontend job list, account
  registration/login, resume upload, and job application flow using deployed
  URLs.

## Checks

```powershell
python manage.py check
python manage.py test
cd .\job-portal-frontend
npm test -- --watchAll=false --runInBand
npm run build
```
