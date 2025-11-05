from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def create_tables() -> None:
    """
    Crea todas las tablas en la base de datos.
    Usa SQLAlchemy create_all() en lugar de Alembic.

    Warning:
        Este método solo crea tablas, no maneja migraciones.
        Para producción, considera usar Alembic para migraciones.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_tables() -> None:
    """
    Elimina todas las tablas de la base de datos.

    Warning:
        Esta operación es destructiva y eliminará todos los datos.
        Usar solo en desarrollo.
    """
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")


def init_db(db: Session) -> None:
    """
    Inicializa la base de datos con datos iniciales si es necesario.
    Puede crear usuarios de prueba, configuraciones, etc.

    Args:
        db: Sesión de base de datos

    Example:
        from app.db.session import SessionLocal
        from app.db.init_db import init_db

        db = SessionLocal()
        init_db(db)
        db.close()
    """
    # Verificar si ya existen usuarios
    user_count = db.query(User).count()

    if user_count == 0:
        print("No users found. Creating initial users...")

        # Crear usuario administrador de ejemplo (OPCIONAL - solo para desarrollo)
        # Comentar o eliminar en producción
        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            password=get_password_hash("Admin123!"),
            role=UserRole.ADMIN_PARQUEADERO,
            is_verified=True,
            is_active=True,
        )
        db.add(admin_user)

        # Crear usuario regular de ejemplo (OPCIONAL - solo para desarrollo)
        regular_user = User(
            name="Regular User",
            email="user@example.com",
            password=get_password_hash("User123!"),
            role=UserRole.USUARIO,
            is_verified=True,
            is_active=True,
        )
        db.add(regular_user)

        db.commit()
        print("Initial users created successfully!")
    else:
        print(f"Database already initialized with {user_count} users.")


def reset_db() -> None:
    """
    Resetea completamente la base de datos.
    Elimina todas las tablas y las vuelve a crear.

    Warning:
        Esta operación es destructiva y eliminará todos los datos.
        Usar solo en desarrollo.
    """
    print("Resetting database...")
    drop_tables()
    create_tables()
    print("Database reset complete!")


if __name__ == "__main__":
    """
    Script para inicializar la base de datos desde la línea de comandos.

    Usage:
        python -m app.db.init_db
    """
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create":
            create_tables()
        elif command == "drop":
            confirm = input("Are you sure you want to drop all tables? (yes/no): ")
            if confirm.lower() == "yes":
                drop_tables()
            else:
                print("Operation cancelled.")
        elif command == "reset":
            confirm = input("Are you sure you want to reset the database? (yes/no): ")
            if confirm.lower() == "yes":
                reset_db()
            else:
                print("Operation cancelled.")
        elif command == "seed":
            create_tables()
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                init_db(db)
            finally:
                db.close()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: create, drop, reset, seed")
    else:
        # Por defecto, crear tablas e inicializar
        create_tables()
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
