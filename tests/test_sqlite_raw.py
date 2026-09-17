"""Unit tests for direct SQLite operations (Medium tasks 2, 4, 7)."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from db.sqlite_raw import SQLiteManager


class TestSQLiteRaw(unittest.TestCase):
    """Test suite for SQLite direct queries, multi-table schema, inserts and updates."""

    def setUp(self) -> None:
        """Create a temporary SQLite database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.manager = SQLiteManager(self.db_path)

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_medium_7_multi_table_creation(self) -> None:
        """Verify that all 4 tables exist and foreign keys are enforced (Medium 7)."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}
            self.assertIn("departments", tables)
            self.assertIn("employees", tables)
            self.assertIn("projects", tables)
            self.assertIn("assignments", tables)

    def test_medium_2_insert_data(self) -> None:
        """Verify inserting records into multiple tables using parameterized SQL (Medium 2)."""
        dep_id = self.manager.insert_department("Инженерия", "Москва, Главный офис")
        self.assertGreater(dep_id, 0)

        emp_id = self.manager.insert_employee(
            department_id=dep_id,
            full_name="Евсюткин Максим Сергеевич",
            email="maksim@example.com",
            salary=150000.0,
            hire_date="2026-09-01",
        )
        self.assertGreater(emp_id, 0)

        proj_id = self.manager.insert_project("Система биллинга", 2500000.0)
        self.assertGreater(proj_id, 0)

        self.manager.assign_employee(emp_id, proj_id, "Tech Lead", 40)

        # Verify insertion via query
        emp = self.manager.get_employee(emp_id)
        self.assertIsNotNone(emp)
        self.assertEqual(emp["full_name"], "Евсюткин Максим Сергеевич")
        self.assertEqual(emp["department_name"], "Инженерия")
        self.assertEqual(emp["salary"], 150000.0)

        # Verify foreign key constraint rejection
        with self.assertRaises(sqlite3.IntegrityError):
            self.manager.insert_employee(
                department_id=99999,  # Non-existent department
                full_name="Невалидный Сотрудник",
                email="invalid@example.com",
                salary=50000.0,
                hire_date="2026-09-01",
            )

    def test_medium_4_update_record(self) -> None:
        """Verify updating existing records in database (Medium 4)."""
        dep_id = self.manager.insert_department("Аналитика", "Казань")
        emp_id = self.manager.insert_employee(
            department_id=dep_id,
            full_name="Иванов Иван Иванович",
            email="ivanov@example.com",
            salary=90000.0,
            hire_date="2026-01-15",
        )

        # Update salary
        updated = self.manager.update_employee_salary(emp_id, 120000.0)
        self.assertTrue(updated)
        emp = self.manager.get_employee(emp_id)
        self.assertEqual(emp["salary"], 120000.0)

        # Update department
        dep_updated = self.manager.update_department(dep_id, name="Data Science", location="Иннополис")
        self.assertTrue(dep_updated)
        dep = self.manager.get_department(dep_id)
        self.assertEqual(dep["name"], "Data Science")
        self.assertEqual(dep["location"], "Иннополис")

        # Update non-existent record returns False
        self.assertFalse(self.manager.update_employee_salary(99999, 100000.0))

    def test_validation_errors(self) -> None:
        """Verify input validations."""
        with self.assertRaises(ValueError):
            self.manager.insert_department("   ", "Москва")
        with self.assertRaises(ValueError):
            self.manager.insert_employee(1, "Name", "e@mail.com", -500.0, "2026-01-01")
        with self.assertRaises(ValueError):
            self.manager.update_employee_salary(1, -100.0)


if __name__ == "__main__":
    unittest.main()
