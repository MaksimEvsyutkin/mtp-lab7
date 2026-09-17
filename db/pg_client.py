"""PostgreSQL client implementation using psycopg2 (Task Advanced 6)."""

import os
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    from psycopg2 import extras
    HAS_PSYCOPG2 = True
except ImportError:
    psycopg2 = None
    extras = None
    HAS_PSYCOPG2 = False


class PostgresClient:
    """Manager for PostgreSQL database operations using psycopg2."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
    ) -> None:
        """Initialize connection parameters with defaults from environment."""
        self.host = host or os.getenv("PG_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("PG_PORT", "5432"))
        self.user = user or os.getenv("PG_USER", "postgres")
        self.password = password or os.getenv("PG_PASSWORD", "postgres")
        self.dbname = dbname or os.getenv("PG_DB", "postgres")

    def get_connection(self) -> Any:
        """Establish connection to PostgreSQL server."""
        if not HAS_PSYCOPG2:
            raise RuntimeError("psycopg2 is not installed in the environment")

        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )

    def ping(self) -> bool:
        """Check if PostgreSQL server is accessible."""
        if not HAS_PSYCOPG2:
            return False
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    return bool(cur.fetchone())
        except Exception:
            return False

    def init_db(self) -> None:
        """Create employees table in PostgreSQL."""
        query = """
            CREATE TABLE IF NOT EXISTS pg_employees (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                department VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                salary NUMERIC(12, 2) NOT NULL CHECK (salary >= 0),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()

    def insert_employee(
        self,
        full_name: str,
        department: str,
        email: str,
        salary: float,
    ) -> int:
        """Insert employee into PostgreSQL using parameterized query (Task Advanced 6)."""
        if salary < 0:
            raise ValueError("Salary must be non-negative")

        query = """
            INSERT INTO pg_employees (full_name, department, email, salary)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (full_name.strip(), department.strip(), email.strip().lower(), float(salary)))
                emp_id = cur.fetchone()[0]
            conn.commit()
            return int(emp_id)

    def get_employee(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """Fetch employee by ID from PostgreSQL."""
        query = "SELECT id, full_name, department, email, salary, created_at FROM pg_employees WHERE id = %s;"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, (employee_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def list_employees(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """List employees, optionally filtered by department."""
        if department:
            query = """
                SELECT id, full_name, department, email, salary, created_at
                FROM pg_employees
                WHERE department = %s
                ORDER BY id;
            """
            params: Tuple[Any, ...] = (department.strip(),)
        else:
            query = """
                SELECT id, full_name, department, email, salary, created_at
                FROM pg_employees
                ORDER BY id;
            """
            params = ()

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return [dict(r) for r in cur.fetchall()]

    def update_salary(self, employee_id: int, new_salary: float) -> bool:
        """Update employee salary in PostgreSQL (Task Advanced 6)."""
        if new_salary < 0:
            raise ValueError("Salary must be non-negative")

        query = "UPDATE pg_employees SET salary = %s WHERE id = %s;"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (float(new_salary), employee_id))
                updated = cur.rowcount > 0
            conn.commit()
            return updated

    def delete_employee(self, employee_id: int) -> bool:
        """Delete employee by ID from PostgreSQL."""
        query = "DELETE FROM pg_employees WHERE id = %s;"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (employee_id,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
