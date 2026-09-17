"""Raw SQLite manager implementing Variant 2 medium tasks.

Tasks:
- Medium 7: Создать несколько таблиц (departments, employees, projects, assignments).
- Medium 2: Вставить данные в таблицу (insert_department, insert_employee, etc. with parameterized SQL).
- Medium 4: Обновить запись (update_employee_salary, update_department, update_project_budget).
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteManager:
    """Manager for direct SQLite database operations using sqlite3 standard library."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        """Initialize SQLite manager with path or memory database."""
        self.db_path = str(db_path)
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Establish and return database connection with row factory and foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # ------------------------------------------------------------------------
    # Task Medium 7: Создать несколько таблиц
    # ------------------------------------------------------------------------
    def create_tables(self) -> None:
        """Create multiple related relational tables (Task Medium 7)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table 1: Departments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    location TEXT NOT NULL
                );
            """)

            # Table 2: Employees (Foreign Key -> departments)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department_id INTEGER NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    salary REAL NOT NULL CHECK (salary >= 0),
                    hire_date TEXT NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
                );
            """)

            # Table 3: Projects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    budget REAL NOT NULL CHECK (budget >= 0)
                );
            """)

            # Table 4: Project Assignments (Many-to-Many junction table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    employee_id INTEGER NOT NULL,
                    project_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    hours INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (employee_id, project_id),
                    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );
            """)

            conn.commit()

    # ------------------------------------------------------------------------
    # Task Medium 2: Вставить данные в таблицу
    # ------------------------------------------------------------------------
    def insert_department(self, name: str, location: str) -> int:
        """Insert a department using parameterized SQL (Task Medium 2)."""
        clean_name = name.strip()
        clean_loc = location.strip()
        if not clean_name:
            raise ValueError("Department name cannot be empty")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO departments (name, location) VALUES (?, ?);",
                (clean_name, clean_loc),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def insert_employee(
        self,
        department_id: int,
        full_name: str,
        email: str,
        salary: float,
        hire_date: str,
    ) -> int:
        """Insert an employee record linked to a department (Task Medium 2)."""
        if salary < 0:
            raise ValueError("Salary must be non-negative")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO employees (department_id, full_name, email, salary, hire_date)
                VALUES (?, ?, ?, ?, ?);
                """,
                (department_id, full_name.strip(), email.strip().lower(), float(salary), hire_date.strip()),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def insert_project(self, name: str, budget: float) -> int:
        """Insert a project record (Task Medium 2)."""
        if budget < 0:
            raise ValueError("Budget must be non-negative")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, budget) VALUES (?, ?);",
                (name.strip(), float(budget)),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def assign_employee(self, employee_id: int, project_id: int, role: str, hours: int = 0) -> None:
        """Assign an employee to a project with specified role and hours."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO assignments (employee_id, project_id, role, hours)
                VALUES (?, ?, ?, ?);
                """,
                (employee_id, project_id, role.strip(), max(0, hours)),
            )
            conn.commit()

    # ------------------------------------------------------------------------
    # Task Medium 4: Обновить запись
    # ------------------------------------------------------------------------
    def update_employee_salary(self, employee_id: int, new_salary: float) -> bool:
        """Update employee salary by ID (Task Medium 4)."""
        if new_salary < 0:
            raise ValueError("Salary cannot be negative")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE employees SET salary = ? WHERE id = ?;",
                (float(new_salary), employee_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_department(
        self,
        department_id: int,
        name: Optional[str] = None,
        location: Optional[str] = None,
    ) -> bool:
        """Update department information (Task Medium 4)."""
        updates: List[str] = []
        params: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name.strip())
        if location is not None:
            updates.append("location = ?")
            params.append(location.strip())

        if not updates:
            return False

        params.append(department_id)
        query = f"UPDATE departments SET {', '.join(updates)} WHERE id = ?;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0

    def update_project_budget(self, project_id: int, new_budget: float) -> bool:
        """Update project budget by ID (Task Medium 4)."""
        if new_budget < 0:
            raise ValueError("Budget cannot be negative")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE projects SET budget = ? WHERE id = ?;",
                (float(new_budget), project_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    # ------------------------------------------------------------------------
    # Read helper methods for verification
    # ------------------------------------------------------------------------
    def get_department(self, department_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single department by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location FROM departments WHERE id = ?;", (department_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_employee(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """Fetch an employee by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT e.id, e.department_id, d.name AS department_name,
                       e.full_name, e.email, e.salary, e.hire_date
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                WHERE e.id = ?;
                """,
                (employee_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_employees_by_department(self, department_id: int) -> List[Dict[str, Any]]:
        """List all employees belonging to a specific department."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, department_id, full_name, email, salary, hire_date FROM employees WHERE department_id = ?;",
                (department_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_project_assignments(self, project_id: int) -> List[Dict[str, Any]]:
        """Fetch all employee assignments for a given project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.employee_id, e.full_name, a.project_id, p.name AS project_name, a.role, a.hours
                FROM assignments a
                JOIN employees e ON a.employee_id = e.id
                JOIN projects p ON a.project_id = p.id
                WHERE a.project_id = ?;
                """,
                (project_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
