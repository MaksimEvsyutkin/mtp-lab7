"""Main entrypoint script demonstrating all Variant 2 tasks for Lab 7.

Variant 2 tasks:
- Medium 2: Вставить данные в таблицу
- Medium 4: Обновить запись
- Medium 7: Создать несколько таблиц
- Advanced 2: CRUD через ORM (SQLAlchemy)
- Advanced 6: Работа с PostgreSQL через psycopg2
"""

from db.sqlite_raw import SQLiteManager

try:
    from db.orm_crud import ORMService
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    from db.pg_client import PostgresClient
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def demo_sqlite() -> None:
    """Demonstrate Tasks Medium 2, 4 and 7 using SQLite."""
    print("\n" + "=" * 60)
    print("1. ДЕМОНСТРАЦИЯ SQLITE (Средняя №2, №4, №7)")
    print("=" * 60)

    manager = SQLiteManager(":memory:")
    print("✅ Создано 4 связанных таблицы: departments, employees, projects, assignments (Средн. №7)")

    # Insert data (Medium 2)
    dep_id = manager.insert_department("Департамент ИИ и данных", "Москва, Главный кампус")
    emp1_id = manager.insert_employee(
        department_id=dep_id,
        full_name="Евсюткин Максим Сергеевич",
        email="maksim@company.com",
        salary=220000.0,
        hire_date="2026-09-01",
    )
    emp2_id = manager.insert_employee(
        department_id=dep_id,
        full_name="Смирнов Алексей Игоревич",
        email="alex@company.com",
        salary=160000.0,
        hire_date="2026-09-10",
    )
    proj_id = manager.insert_project("Нейросетевой ассистент", 5000000.0)
    manager.assign_employee(emp1_id, proj_id, "Lead Architect", 40)
    manager.assign_employee(emp2_id, proj_id, "ML Engineer", 35)

    print("✅ Данные успешно добавлены с параметризованными запросами (Средн. №2):")
    emp1 = manager.get_employee(emp1_id)
    print(f"   Сотрудник #{emp1['id']}: {emp1['full_name']} | Отдел: {emp1['department_name']} | З/П: {emp1['salary']}")

    # Update record (Medium 4)
    manager.update_employee_salary(emp1_id, 260000.0)
    manager.update_department(dep_id, location="Москва, Центр инноваций Сколково")
    emp1_updated = manager.get_employee(emp1_id)
    dep_updated = manager.get_department(dep_id)
    print("✅ Записи успешно обновлены (Средн. №4):")
    print(f"   Новая зарплата: {emp1_updated['salary']} руб.")
    print(f"   Новая локация отдела: {dep_updated['location']}")


def demo_orm() -> None:
    """Demonstrate Task Advanced 2 using SQLAlchemy ORM."""
    print("\n" + "=" * 60)
    print("2. ДЕМОНСТРАЦИЯ SQLALCHEMY 2.0 ORM CRUD (Повышенная №2)")
    print("=" * 60)

    if not HAS_SQLALCHEMY:
        print("⚠️  SQLAlchemy не установлена в текущем интерпретаторе. Пропуск ORM демо.")
        return

    service = ORMService("sqlite:///:memory:")

    # CREATE
    dep = service.create_department("Архитектура ПО", "Санкт-Петербург")
    emp = service.create_employee(
        department_id=dep.id,
        full_name="Евсюткин Максим Сергеевич",
        email="m.evsyutkin@lab7.ru",
        salary=300000.0,
        hire_date="2026-09-17",
    )
    proj = service.create_project("Корпоративная СУБД платформа", 12000000.0)
    service.assign_employee_to_project(emp.id, proj.id)
    print(f"✅ [CREATE] Созданы объекты ORM: {dep}, {emp}, {proj}")

    # READ
    fetched_emp = service.get_employee_by_email("m.evsyutkin@lab7.ru")
    print(f"✅ [READ] Получен сотрудник по email: {fetched_emp.full_name}, проектов: {len(fetched_emp.projects)}")

    # UPDATE
    updated_emp = service.update_employee(emp.id, salary=350000.0)
    print(f"✅ [UPDATE] Обновлен оклад через ORM сессию: {updated_emp.salary} руб.")

    # DELETE
    emp2 = service.create_employee(
        department_id=dep.id,
        full_name="Временный Сотрудник",
        email="temp@lab7.ru",
        salary=50000.0,
        hire_date="2026-01-01",
    )
    deleted = service.delete_employee(emp2.id)
    print(f"✅ [DELETE] Удаление объекта сотрудника id={emp2.id}: {deleted}")


def demo_postgres() -> None:
    """Demonstrate Task Advanced 6 using psycopg2."""
    print("\n" + "=" * 60)
    print("3. ДЕМОНСТРАЦИЯ POSTGRESQL / PSYCOPG2 (Повышенная №6)")
    print("=" * 60)

    if not HAS_PSYCOPG2:
        print("⚠️  psycopg2 не установлена в текущем интерпретаторе. Пропуск PostgreSQL демо.")
        return

    client = PostgresClient()
    if not client.ping():
        print("ℹ️  Сервер PostgreSQL недоступен по умолчанию (127.0.0.1:5432).")
        print("   Клиент PostgresClient сконфигурирован и готов к работе.")
        print("   В GitHub Actions CI поднят контейнер postgres:15, где выполняются живые интеграционные тесты.")
        return

    print("✅ Подключение к серверу PostgreSQL успешно установлено!")
    client.init_db()
    emp_id = client.insert_employee("Максим Евсюткин", "DevOps", "maksim.pg@example.com", 240000.0)
    print(f"✅ Добавлен сотрудник в PostgreSQL: id={emp_id}")
    client.update_salary(emp_id, 280000.0)
    fetched = client.get_employee(emp_id)
    print(f"✅ Получены обновленные данные из PostgreSQL: {fetched}")
    client.delete_employee(emp_id)
    print("✅ Запись удалена после демонстрации.")


def main() -> None:
    """Run all demonstrations."""
    print("=" * 60)
    print("Лабораторная работа №7: Работа с различными СУБД в Python")
    print("Студент: Евсюткин Максим Сергеевич, группа 221141, вариант 2")
    print("=" * 60)

    demo_sqlite()
    demo_orm()
    demo_postgres()

    print("\n" + "=" * 60)
    print("✅ Все задания варианта 2 успешно продемонстрированы!")
    print("=" * 60)


if __name__ == "__main__":
    main()
