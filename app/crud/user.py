from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """
    CRUD operations for User model.
    Implements Create, Read, Update, Delete operations.
    """

    def get(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Obtiene un usuario por su ID.

        Args:
            db: Sesión de base de datos
            user_id: UUID del usuario

        Returns:
            User o None si no existe
        """
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Returns:
            User o None si no existe
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_verification_token(self, db: Session, token: str) -> Optional[User]:
        """
        Obtiene un usuario por su token de verificación.

        Args:
            db: Sesión de base de datos
            token: Token de verificación

        Returns:
            User o None si no existe o el token expiró
        """
        user = db.query(User).filter(User.verification_token == token).first()

        if user and user.verification_token_expires:
            # Verificar si el token no ha expirado
            if user.verification_token_expires < datetime.utcnow():
                return None

        return user

    def get_by_reset_token(self, db: Session, token: str) -> Optional[User]:
        """
        Obtiene un usuario por su token de reset de contraseña.

        Args:
            db: Sesión de base de datos
            token: Token de reset

        Returns:
            User o None si no existe o el token expiró
        """
        user = db.query(User).filter(User.reset_token == token).first()

        if user and user.reset_token_expires:
            # Verificar si el token no ha expirado
            if user.reset_token_expires < datetime.utcnow():
                return None

        return user

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_verified: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> list[User]:
        """
        Obtiene múltiples usuarios con filtros opcionales.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            role: Filtrar por rol (opcional)
            is_verified: Filtrar por verificación (opcional)
            is_active: Filtrar por estado activo (opcional)

        Returns:
            Lista de usuarios
        """
        query = db.query(User)

        if role is not None:
            query = query.filter(User.role == role)
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Crea un nuevo usuario.

        Args:
            db: Sesión de base de datos
            obj_in: Datos del usuario a crear

        Returns:
            Usuario creado
        """
        db_obj = User(
            email=obj_in.email,
            name=obj_in.name,
            password=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_verified=False,  # Por defecto no verificado
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate
    ) -> User:
        """
        Actualiza un usuario existente.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario a actualizar
            obj_in: Datos a actualizar

        Returns:
            Usuario actualizado
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(
        self,
        db: Session,
        *,
        db_obj: User,
        new_password: str
    ) -> User:
        """
        Actualiza la contraseña de un usuario.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario a actualizar
            new_password: Nueva contraseña (sin hashear)

        Returns:
            Usuario actualizado
        """
        db_obj.password = get_password_hash(new_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_verification_token(
        self,
        db: Session,
        *,
        db_obj: User,
        token: str,
        expires_hours: int = 24
    ) -> User:
        """
        Establece el token de verificación de email.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario
            token: Token de verificación
            expires_hours: Horas hasta la expiración (default: 24)

        Returns:
            Usuario actualizado
        """
        db_obj.verification_token = token
        db_obj.verification_token_expires = datetime.utcnow() + timedelta(hours=expires_hours)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def verify_email(self, db: Session, *, db_obj: User) -> User:
        """
        Marca el email del usuario como verificado.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario a verificar

        Returns:
            Usuario actualizado
        """
        db_obj.is_verified = True
        db_obj.verification_token = None
        db_obj.verification_token_expires = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_reset_token(
        self,
        db: Session,
        *,
        db_obj: User,
        token: str,
        expires_hours: int = 1
    ) -> User:
        """
        Establece el token de reset de contraseña.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario
            token: Token de reset
            expires_hours: Horas hasta la expiración (default: 1)

        Returns:
            Usuario actualizado
        """
        db_obj.reset_token = token
        db_obj.reset_token_expires = datetime.utcnow() + timedelta(hours=expires_hours)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def clear_reset_token(self, db: Session, *, db_obj: User) -> User:
        """
        Limpia el token de reset de contraseña.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario

        Returns:
            Usuario actualizado
        """
        db_obj.reset_token = None
        db_obj.reset_token_expires = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica un usuario por email y contraseña.

        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña sin hashear

        Returns:
            User si las credenciales son válidas, None en caso contrario
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        Verifica si un usuario está activo.

        Args:
            user: Usuario a verificar

        Returns:
            True si está activo, False en caso contrario
        """
        return user.is_active

    def is_verified(self, user: User) -> bool:
        """
        Verifica si un usuario ha verificado su email.

        Args:
            user: Usuario a verificar

        Returns:
            True si está verificado, False en caso contrario
        """
        return user.is_verified

    def deactivate(self, db: Session, *, db_obj: User) -> User:
        """
        Desactiva un usuario.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario a desactivar

        Returns:
            Usuario actualizado
        """
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, db_obj: User) -> User:
        """
        Activa un usuario.

        Args:
            db: Sesión de base de datos
            db_obj: Usuario a activar

        Returns:
            Usuario actualizado
        """
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, user_id: UUID) -> Optional[User]:
        """
        Elimina un usuario (hard delete).

        Args:
            db: Sesión de base de datos
            user_id: UUID del usuario a eliminar

        Returns:
            Usuario eliminado o None si no existe
        """
        obj = db.query(User).get(user_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# Instancia única de CRUD para importar en otros módulos
user = CRUDUser()
