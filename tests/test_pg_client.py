"""Unit and integration tests for PostgreSQL client (Task Advanced 6)."""

import unittest
from unittest.mock import MagicMock, patch

from db.pg_client import HAS_PSYCOPG2, PostgresClient


class TestPostgresClientUnit(unittest.TestCase):
    """Unit tests for PostgresClient using mocks (runs offline)."""

    def setUp(self) -> None:
        """Set up mocked client."""
        self.client = PostgresClient(
            host="127.0.0.1",
            port=5432,
            user="test_user",
            password="test_password",
            dbname="test_db",
        )

    def test_validation_negative_salary(self) -> None:
        """Verify negative salary raises ValueError."""
        with self.assertRaises(ValueError):
            self.client.insert_employee("Test", "Dep", "t@example.com", -100.0)
        with self.assertRaises(ValueError):
            self.client.update_salary(1, -50.0)

    @unittest.skipUnless(HAS_PSYCOPG2, "psycopg2 is not installed")
    @patch("db.pg_client.psycopg2.connect")
    def test_init_db_executes_ddl(self, mock_connect: MagicMock) -> None:
        """Verify table creation query execution."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        self.client.init_db()

        mock_connect.assert_called_once_with(
            host="127.0.0.1",
            port=5432,
            user="test_user",
            password="test_password",
            dbname="test_db",
        )
        self.assertTrue(mock_cursor.execute.called)
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("CREATE TABLE IF NOT EXISTS pg_employees", executed_query)
        self.assertTrue(mock_conn.commit.called)

    @unittest.skipUnless(HAS_PSYCOPG2, "psycopg2 is not installed")
    @patch("db.pg_client.psycopg2.connect")
    def test_insert_employee_success(self, mock_connect: MagicMock) -> None:
        """Verify parameterized insert and returning id."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        new_id = self.client.insert_employee("Иван Иванов", "ИТ", "ivan@company.com", 120000.0)
        self.assertEqual(new_id, 42)

        call_args = mock_cursor.execute.call_args
        self.assertIn("INSERT INTO pg_employees", call_args[0][0])
        self.assertEqual(
            call_args[0][1],
            ("Иван Иванов", "ИТ", "ivan@company.com", 120000.0),
        )

    @unittest.skipUnless(HAS_PSYCOPG2, "psycopg2 is not installed")
    @patch("db.pg_client.psycopg2.connect")
    def test_update_salary_success(self, mock_connect: MagicMock) -> None:
        """Verify update query and rowcount check."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        updated = self.client.update_salary(42, 140000.0)
        self.assertTrue(updated)

        call_args = mock_cursor.execute.call_args
        self.assertIn("UPDATE pg_employees SET salary", call_args[0][0])
        self.assertEqual(call_args[0][1], (140000.0, 42))

    @unittest.skipUnless(HAS_PSYCOPG2, "psycopg2 is not installed")
    @patch("db.pg_client.psycopg2.connect")
    def test_delete_employee_success(self, mock_connect: MagicMock) -> None:
        """Verify delete query and rowcount check."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        deleted = self.client.delete_employee(42)
        self.assertTrue(deleted)

        call_args = mock_cursor.execute.call_args
        self.assertIn("DELETE FROM pg_employees WHERE id", call_args[0][0])
        self.assertEqual(call_args[0][1], (42,))


class TestPostgresClientLive(unittest.TestCase):
    """Integration test suite executed when live PostgreSQL is running (e.g. in CI)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Check live connection."""
        cls.client = PostgresClient()
        cls.is_live = cls.client.ping()

    def setUp(self) -> None:
        """Skip if live PostgreSQL is not reachable."""
        if not self.is_live:
            self.skipTest("Live PostgreSQL database is not reachable")
        self.client.init_db()

    def test_live_lifecycle(self) -> None:
        """Full CRUD lifecycle on live PostgreSQL."""
        import uuid
        unique_email = f"live_{uuid.uuid4().hex[:8]}@example.com"

        emp_id = self.client.insert_employee("Живой Пользователь", "Разработка", unique_email, 180000.0)
        self.assertGreater(emp_id, 0)

        emp = self.client.get_employee(emp_id)
        self.assertIsNotNone(emp)
        self.assertEqual(emp["email"], unique_email)

        self.assertTrue(self.client.update_salary(emp_id, 200000.0))
        emp_updated = self.client.get_employee(emp_id)
        self.assertEqual(float(emp_updated["salary"]), 200000.0)

        self.assertTrue(self.client.delete_employee(emp_id))
        self.assertIsNone(self.client.get_employee(emp_id))


if __name__ == "__main__":
    unittest.main()
