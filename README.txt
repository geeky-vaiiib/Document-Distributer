DOCFOLIO · STUDENT DOCUMENT ORGANIZER

LOCAL SETUP

  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -r requirements.txt
  python app.py

On Windows, activate with .venv\Scripts\activate.
Open http://127.0.0.1:5002. Set PORT to choose a different port.
Run the workflow tests with python -m unittest discover -s tests.

WORKFLOW

Choose Try sample workspace for five example documents in a browser-specific
workspace. You can test search, category and status filters, sorting, downloads,
and expiry reminders there. Create an account to start with a private empty
workspace. Sign in from another browser with the same email and password to
access that account. Passwords are stored as salted PBKDF2 hashes.

Upload PDF, JPEG, or PNG files up to 10 MB. Enter optional issue and expiry dates.
You can edit details, replace files, download, and delete your documents.
Reminders shows overdue documents and dates due within 30 days. Import a
downloaded calendar event to receive the 30-day and 7-day alerts in your calendar.

Local data lives in SQLite under instance/mock/. ORGANIZER_DATABASE overrides
its path. Older local uploads are read from instance/mock/uploads/ or
ORGANIZER_UPLOAD_DIR. Never commit the database, uploads, or secrets.

RENDER AND VERCEL

1. Create a Neon Free PostgreSQL project and copy its TLS connection string.
   Push the source to a Git repository connected to Render. Create a Render
   Blueprint from render.yaml and enter the connection string as DATABASE_URL.
   The Free web service runs Flask with Gunicorn and generates a session secret.
   PostgreSQL stores accounts, documents, and uploads. The app limits total
   hosted file contents to 250 MiB to leave space under the database quota.
2. Wait for Render to deploy. Confirm that its /health endpoint returns
   {"status":"ok"}. Copy the HTTPS onrender.com origin.
3. Import the same repository in Vercel Hobby with vercel/ as its Root Directory.
   If deploying to a different Render service, update the origin in
   vercel/vercel.json before deploying.
   The rewrite keeps pages, forms, static files, and downloads on one origin
   and forwards them to Render. Private responses bypass Vercel caching.
4. Open the Vercel URL and smoke-test registration, sign-in, filters, and a sample
   upload and download. Confirm the same account and upload survive a Render
   restart before sharing the deployment.

The Render Free service can take about a minute to wake after inactivity.
Register with an address you control when using a real account. This version
does not send email verification or password reset messages.
