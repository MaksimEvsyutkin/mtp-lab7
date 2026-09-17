"""SQLAlchemy ORM service implementing CRUD operations (Task Advanced 2)."""

from typing import List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base, Department, Employee, Project


class ORMService:
    """Service providing Create, Read, Update, Delete (CRUD) operations via SQLAlchemy ORM."""

    def __init__(self, db_url: str = "sqlite:///:memory:") -> None:
        """Initialize engine, sessionmaker and create all tables."""
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self) -> Session:
        """Create and return a new database session."""
        return self.SessionLocal()

    # ========================================================================
    # CREATE Operations
    # ========================================================================
    def create_department(self, name: str, location: str) -> Department:
        """Create a new department."""
        with self.get_session() as session:
            dep = Department(name=name.strip(), location=location.strip())
            session.add(dep)
            session.commit()
            session.refresh(dep)
            return dep

    def create_employee(
        self,
        department_id: int,
        full_name: str,
        email: str,
        salary: float,
        hire_date: str,
    ) -> Employee:
        """Create a new employee linked to a department."""
        if salary < 0:
            raise ValueError("Salary must be non-negative")

        with self.get_session() as session:
            dep = session.get(Department, department_id)
            if not dep:
                raise ValueError(f"Department with id={department_id} does not exist")

            emp = Employee(
                department_id=department_id,
                full_name=full_name.strip(),
                email=email.strip().lower(),
                salary=float(salary),
                hire_date=hire_date.strip(),
            )
            session.add(emp)
            session.commit()
            session.refresh(emp)
            return emp

    def create_project(self, title: str, budget: float, status: str = "active") -> Project:
        """Create a new project."""
        if budget < 0:
            raise ValueError("Budget must be non-negative")

        with self.get_session() as session:
            proj = Project(
                title=title.strip(),
                budget=float(budget),
                status=status.strip(),
            )
            session.add(proj)
            session.commit()
            session.refresh(proj)
            return proj

    def assign_employee_to_project(self, employee_id: int, project_id: int) -> None:
        """Link an employee to a project in the many-to-many relationship."""
        with self.get_session() as session:
            emp = session.get(Employee, employee_id)
            proj = session.get(Project, project_id)
            if not emp:
                raise ValueError(f"Employee {employee_id} not found")
            if not proj:
                raise ValueError(f"Project {project_id} not found")

            if proj not in emp.projects:
                emp.projects.append(proj)
                session.commit()

    # ========================================================================
    # READ Operations
    # ========================================================================
    def get_department(self, department_id: int) -> Optional[Department]:
        """Fetch department by ID."""
        with self.get_session() as session:
            return session.get(Department, department_id)

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Fetch employee by ID."""
        with self.get_session() as session:
            return session.get(Employee, employee_id)

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Fetch employee by unique email."""
        with self.get_session() as session:
            stmt = select(Employee).where(Employee.email == email.strip().lower())
            return session.execute(stmt).scalar_one_or_none()

    def list_employees(self, department_id: Optional[int] = None) -> List[Employee]:
        """List all employees or filter by department ID."""
        with self.get_session() as session:
            stmt = select(Employee)
            if department_id is not None:
                stmt = stmt.where(Employee.department_id == department_id)
            return list(session.execute(stmt).scalars().all())

    def list_departments(self) -> List[Department]:
        """List all registered departments."""
        with self.get_session() as session:
            stmt = select(Department).order_by(Department.id)
            return list(session.execute(stmt).scalars().all())

    def get_project(self, project_id: int) -> Optional[Project]:
        """Fetch project by ID."""
        with self.get_session() as session:
            return session.get(Project, project_id)

    # ========================================================================
    # UPDATE Operations
    # ========================================================================
    def update_employee(
        self,
        employee_id: int,
        full_name: Optional[str] = None,
        salary: Optional[float] = None,
        department_id: Optional[int] = None,
    ) -> Optional[Employee]:
        """Update fields of an employee."""
        if salary is not None and salary < 0:
            raise ValueError("Salary must be non-negative")

        with self.get_session() as session:
            emp = session.get(Employee, employee_id)
            if not emp:
                return None

            if full_name is not None:
                emp.full_name = full_name.strip()
            if salary is not None:
                emp.salary = float(salary)
            if department_id is not None:
                dep = session.get(Department, department_id)
                if not dep:
                    raise ValueError(f"Department {department_id} not found")
                emp.department_id = department_id

            session.commit()
            session.refresh(emp)
            return emp

    def update_department(
        self,
        department_id: int,
        name: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Optional[Department]:
        """Update department name or location."""
        with self.get_session() as session:
            dep = session.get(Department, department_id)
            if not dep:
                return None

            if name is not None:
                dep.name = name.strip()
            if location is not None:
                dep.location = location.strip()

            session.commit()
            session.refresh(dep)
            return dep

    def update_project(
        self,
        project_id: int,
        title: Optional[str] = None,
        budget: Optional[float] = None,
        status: Optional[str] = None,
    ) -> Optional[Project]:
        """Update project title, budget or status."""
        if budget is not None and budget < 0:
            raise ValueError("Budget must be non-negative")

        with self.get_session() as session:
            proj = session.get(Project, project_id)
            if not proj:
                return None

            if title is not None:
                proj.title = title.strip()
            if budget is not None:
                proj.budget = float(budget)
            if status is not None:
                proj.status = status.strip()

            session.commit()
            session.refresh(proj)
            return proj

    # ========================================================================
    # DELETE Operations
    # ========================================================================
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee by ID."""
        with self.get_session() as session:
            emp = session.get(Employee, employee_id)
            if not emp:
                return False
            session.delete(emp)
            session.commit()
            return True

    def delete_department(self, department_id: int) -> bool:
        """Delete department by ID (cascade deletes orphan employees)."""
        with self.get_session() as session:
            dep = session.get(Department, department_id)
            if not dep:
                return False
            session.delete(dep)
            session.commit()
            return True

    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID."""
        with self.get_session() as session:
            proj = session.get(Project, project_id)
            if not proj:
                return False
            session.delete(proj)
            session.commit()
            return True
