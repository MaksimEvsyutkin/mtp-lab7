"""SQLAlchemy 2.0 ORM models for relational schema (Task Advanced 2)."""

from typing import List

from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for ORM entities."""

    pass


# Junction table for Employee <-> Project (Many-to-Many)
employee_projects = Table(
    "employee_projects",
    Base.metadata,
    Column("employee_id", Integer, ForeignKey("orm_employees.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("orm_projects.id", ondelete="CASCADE"), primary_key=True),
)


class Department(Base):
    """Department entity."""

    __tablename__ = "orm_departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)

    employees: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return readable string representation."""
        return f"<Department(id={self.id}, name='{self.name}', location='{self.location}')>"


class Employee(Base):
    """Employee entity."""

    __tablename__ = "orm_employees"
    __table_args__ = (CheckConstraint("salary >= 0", name="check_positive_salary"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("orm_departments.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    hire_date: Mapped[str] = mapped_column(String(20), nullable=False)

    department: Mapped["Department"] = relationship("Department", back_populates="employees", lazy="selectin")
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        secondary=employee_projects,
        back_populates="members",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return readable string representation."""
        return f"<Employee(id={self.id}, name='{self.full_name}', salary={self.salary})>"


class Project(Base):
    """Project entity."""

    __tablename__ = "orm_projects"
    __table_args__ = (CheckConstraint("budget >= 0", name="check_positive_budget"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    members: Mapped[List["Employee"]] = relationship(
        "Employee",
        secondary=employee_projects,
        back_populates="projects",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return readable string representation."""
        return f"<Project(id={self.id}, title='{self.title}', budget={self.budget}, status='{self.status}')>"
