"""Unit tests for SQLAlchemy ORM CRUD operations (Task Advanced 2)."""

import unittest

try:
    import sqlalchemy  # noqa: F401
    from db.orm_crud import ORMService
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


@unittest.skipUnless(HAS_SQLALCHEMY, "SQLAlchemy is not installed in the environment")
class TestORMService(unittest.TestCase):
    """Test suite verifying CRUD operations with SQLAlchemy ORM."""

    def setUp(self) -> None:
        """Initialize in-memory SQLite ORM service for isolated testing."""
        self.service = ORMService("sqlite:///:memory:")

    def test_create_and_read_department(self) -> None:
        """Verify department creation and reading (C and R)."""
        dep = self.service.create_department("Backend Development", "Saint Petersburg")
        self.assertIsNotNone(dep.id)
        self.assertEqual(dep.name, "Backend Development")
        self.assertEqual(dep.location, "Saint Petersburg")

        fetched = self.service.get_department(dep.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Backend Development")

    def test_create_and_read_employee(self) -> None:
        """Verify employee creation linked to department and fetching by email."""
        dep = self.service.create_department("AI Lab", "Moscow")
        emp = self.service.create_employee(
            department_id=dep.id,
            full_name="Евсюткин Максим Сергеевич",
            email="maksim@deepmind.com",
            salary=250000.0,
            hire_date="2026-09-17",
        )
        self.assertIsNotNone(emp.id)
        self.assertEqual(emp.full_name, "Евсюткин Максим Сергеевич")
        self.assertEqual(emp.salary, 250000.0)

        by_email = self.service.get_employee_by_email("maksim@deepmind.com")
        self.assertIsNotNone(by_email)
        self.assertEqual(by_email.id, emp.id)

    def test_update_employee(self) -> None:
        """Verify updating employee fields (U)."""
        dep = self.service.create_department("DevOps", "Remote")
        emp = self.service.create_employee(
            department_id=dep.id,
            full_name="Смирнов Алексей",
            email="alex@example.com",
            salary=120000.0,
            hire_date="2026-01-10",
        )

        updated = self.service.update_employee(
            employee_id=emp.id,
            full_name="Смирнов Алексей Игоревич",
            salary=160000.0,
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.full_name, "Смирнов Алексей Игоревич")
        self.assertEqual(updated.salary, 160000.0)

    def test_delete_employee(self) -> None:
        """Verify deleting an employee (D)."""
        dep = self.service.create_department("QA", "Novosibirsk")
        emp = self.service.create_employee(
            department_id=dep.id,
            full_name="Тестов Тест",
            email="test@qa.com",
            salary=80000.0,
            hire_date="2026-05-01",
        )
        emp_id = emp.id
        self.assertTrue(self.service.delete_employee(emp_id))
        self.assertIsNone(self.service.get_employee(emp_id))
        self.assertFalse(self.service.delete_employee(emp_id))

    def test_many_to_many_project_assignment(self) -> None:
        """Verify many-to-many relationship between Employee and Project."""
        dep = self.service.create_department("R&D", "Skolkovo")
        emp = self.service.create_employee(
            department_id=dep.id,
            full_name="Максим",
            email="maksim@rd.com",
            salary=200000.0,
            hire_date="2026-03-01",
        )
        proj = self.service.create_project("Autonomous AI", 10000000.0)

        self.service.assign_employee_to_project(emp.id, proj.id)

        fetched_emp = self.service.get_employee(emp.id)
        self.assertEqual(len(fetched_emp.projects), 1)
        self.assertEqual(fetched_emp.projects[0].title, "Autonomous AI")

    def test_cascade_delete_department(self) -> None:
        """Verify cascade delete of employees when department is deleted."""
        dep = self.service.create_department("Temporary", "Online")
        emp = self.service.create_employee(
            department_id=dep.id,
            full_name="Temp User",
            email="temp@user.com",
            salary=50000.0,
            hire_date="2026-01-01",
        )
        emp_id = emp.id

        self.service.delete_department(dep.id)
        self.assertIsNone(self.service.get_department(dep.id))
        self.assertIsNone(self.service.get_employee(emp_id))


if __name__ == "__main__":
    unittest.main()
