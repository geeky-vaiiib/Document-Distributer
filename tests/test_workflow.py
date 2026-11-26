import io
import re
import unittest
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from app import app, connect, init_db


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        config = app.config.copy()
        self.addCleanup(app.config.update, config)
        data = Path(self.temp.name)
        app.config.update(TESTING=True, DATABASE=data / "app.db", UPLOAD_DIR=data / "uploads")
        init_db()
        self.client = app.test_client()

    def post(self, path, fields=None, form_path=None):
        page = self.client.get(form_path or path)
        token = re.search(rb'name="csrf_token" value="([^"]+)"', page.data)[1].decode()
        return self.client.post(path, data={**(fields or {}), "csrf_token": token})

    def register(self, email):
        return self.post("/register", {
            "student_name": "Sam Rivera", "email": email, "password": "Example-password42",
        })

    def test_registration_and_login(self):
        self.assertEqual(self.register("Student@example.test").location, "/dashboard")
        self.assertIn(b"Welcome back, Sam.", self.client.get("/dashboard").data)
        with connect() as con:
            row = con.execute("SELECT email, password FROM students").fetchone()
            self.assertEqual(row["email"], "student@example.test")
            self.assertTrue(row["password"].startswith("pbkdf2:sha256:"))
            self.assertEqual(con.execute("SELECT count(*) AS total FROM documents").fetchone()["total"], 0)
        self.assertEqual(self.post("/logout", form_path="/dashboard").location, "/")
        self.assertEqual(self.client.get("/dashboard").location, "/")
        self.assertEqual(self.register("student@example.test").status_code, 409)
        self.assertEqual(self.post("/", {"email": "student@example.test", "password": "wrong"}).status_code, 401)
        self.assertEqual(self.post("/", {
            "email": "STUDENT@example.test", "password": "Example-password42",
        }).location, "/dashboard")

    def test_sample_workspace_filters_and_sorting(self):
        self.assertEqual(self.post("/demo", form_path="/").location, "/dashboard")
        result = self.client.get("/documents", query_string={"status": "soon", "sort": "expiry"}).data
        self.assertIn(b"Student ID Card", result)
        self.assertIn(b"Scholarship Certificate", result)
        self.assertLess(result.index(b"Student ID Card"), result.index(b"Scholarship Certificate"))
        self.assertNotIn(b"Library Membership", result)
        result = self.client.get("/documents", query_string={
            "search": "academic", "category": "Academic Documents", "status": "none",
        }).data
        self.assertIn(b"Academic Transcript", result)
        self.assertNotIn(b"Enrollment Letter", result)
        self.assertIn(b"Library Membership", self.client.get("/reminders").data)
        self.assertEqual(self.post("/logout", form_path="/dashboard").status_code, 302)
        self.assertEqual(self.post("/demo", form_path="/").status_code, 302)
        with connect() as con:
            self.assertEqual(con.execute("SELECT count(*) AS total FROM documents").fetchone()["total"], 5)

    def test_upload_edit_download_calendar_delete_and_ownership(self):
        self.assertEqual(self.register("first@example.test").status_code, 302)
        expiry = (date.today() + timedelta(days=10)).isoformat()
        response = self.post("/add-document", {
            "document_name": "Enrollment Letter", "category": "Academic Documents",
            "expiry_date": expiry, "document": (io.BytesIO(b"%PDF-1.4\n"), "proof.pdf"),
        })
        self.assertEqual(response.location, "/documents")
        with connect() as con:
            record = con.execute("SELECT id, file_name FROM documents").fetchone()
        document_url = f"/documents/{record['id']}/edit"
        upload_url = f"/uploads/{record['file_name']}"
        calendar_url = f"/documents/{record['id']}/calendar.ics"
        with self.client.get(upload_url + "?download=1") as download:
            self.assertEqual(download.data, b"%PDF-1.4\n")
            self.assertIn("attachment", download.headers["Content-Disposition"])
        self.assertEqual(self.post(document_url, {
            "document_name": "Updated letter", "category": "Certificates", "expiry_date": expiry,
        }).location, "/documents")
        self.assertIn(b"Updated letter", self.client.get("/documents?category=Certificates").data)
        self.assertIn(b"BEGIN:VCALENDAR", self.client.get(calendar_url).data)
        owner = self.client
        self.client = app.test_client()
        self.assertEqual(self.register("second@example.test").status_code, 302)
        for private_url in (document_url, upload_url, calendar_url):
            self.assertEqual(self.client.get(private_url).status_code, 404)
        self.assertEqual(self.post(f"/delete/{record['id']}", form_path="/dashboard").status_code, 404)
        self.client = owner
        self.assertEqual(self.post(f"/delete/{record['id']}", form_path=document_url).location, "/documents")
        self.assertEqual(self.client.get(upload_url).status_code, 404)
        with connect() as con:
            self.assertIsNone(con.execute(
                "SELECT 1 FROM document_files WHERE file_name = ?", (record["file_name"],),
            ).fetchone())
        self.assertFalse((app.config["UPLOAD_DIR"] / record["file_name"]).exists())


if __name__ == "__main__":
    unittest.main()
