from domain.personal import Personal
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class PersonalRepository:
    def list_personal(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_personal, id_club, nombres, apellidos, cargo, fecha_ingreso, salario FROM personal")).fetchall()
            return [Personal(*row) for row in result]
        finally:
            db.close()

    def get_personal(self, personal_id: int) -> Optional[Personal]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_personal, id_club, nombres, apellidos, cargo, fecha_ingreso, salario FROM personal WHERE id_personal = :id_personal"), {"id_personal": personal_id}).fetchone()
            if result:
                return Personal(*result)
            return None
        finally:
            db.close()

    def create_personal(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO personal (id_club, nombres, apellidos, cargo, salario)
                VALUES (:id_club, :nombres, :apellidos, :cargo, :salario)
                RETURNING id_personal, id_club, nombres, apellidos, cargo, fecha_ingreso, salario
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Personal(*row)
        finally:
            db.close()

    def update_personal(self, personal_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_personal": personal_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_personal(personal_id)
            db.execute(text(f"UPDATE personal SET {', '.join(fields)} WHERE id_personal = :id_personal"), params)
            db.commit()
            return self.get_personal(personal_id)
        finally:
            db.close()

    def delete_personal(self, personal_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM personal WHERE id_personal = :id_personal RETURNING id_personal"), {"id_personal": personal_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 