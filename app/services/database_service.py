from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import flash

from app.extensions import db


class DatabaseService:

    @staticmethod
    def commit(
        success_message=None,
        error_message="Ocurrió un error al guardar la información."
    ):
        """
        Ejecuta commit de forma segura.
        """

        try:

            db.session.commit()

            if success_message:
                flash(success_message, "success")

            return True

        except IntegrityError as e:

            db.session.rollback()

            mensaje = str(e.orig)

            if "duplicate key" in mensaje.lower():
                flash(
                    "Ya existe un registro con esos datos.",
                    "warning"
                )

            elif "foreign key" in mensaje.lower():
                flash(
                    "El registro está relacionado con otra información y no puede eliminarse.",
                    "danger"
                )

            elif "not-null" in mensaje.lower():
                flash(
                    "Faltan datos obligatorios.",
                    "warning"
                )

            else:

                flash(error_message, "danger")

            return False

        except SQLAlchemyError:

            db.session.rollback()

            flash(
                error_message,
                "danger"
            )

            return False
        

    @staticmethod
    def save(objeto,
                success=None,
                error=None):

            try:

                db.session.add(objeto)

                db.session.commit()

                if success:
                    flash(success,"success")

                return True

            except IntegrityError:

                db.session.rollback()

                flash(error,"warning")

                return False
    
    @staticmethod
    def delete(objeto,
               success=None,
               error=None):

        try:

            db.session.delete(objeto)

            db.session.commit()

            if success:

                flash(success,"success")

            return True

        except IntegrityError:

            db.session.rollback()

            flash(error,"danger")

            return False