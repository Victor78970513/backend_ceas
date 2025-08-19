from domain.personal import Personal
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class PersonalRepository:
    def list_personal(self):
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener el nombre del cargo
            result = db.execute(text("""
                SELECT 
                    p.id_personal, 
                    p.id_club, 
                    p.nombres, 
                    p.apellidos, 
                    p.cargo, 
                    p.fecha_ingreso, 
                    p.salario,
                    p.correo,
                    p.departamento, 
                    p.estado,
                    c.nombre_cargo
                FROM personal p
                LEFT JOIN cargos c ON p.cargo = c.id_cargo
                ORDER BY p.nombres, p.apellidos
            """)).fetchall()
            
            personal_list = []
            for row in result:
                # Convertir fecha de datetime a string si existe
                fecha_ingreso = str(row[5]) if row[5] else None
                personal = Personal(
                    id_personal=row[0],
                    id_club=row[1],
                    nombres=row[2],
                    apellidos=row[3],
                    cargo=row[4],
                    fecha_ingreso=fecha_ingreso,
                    salario=float(row[6]) if row[6] else 0.0,
                    correo=row[7] if row[7] else None,
                    departamento=row[8] if row[8] else None,
                    estado=bool(row[9]) if row[9] is not None else True,
                    nombre_cargo=row[10] if row[10] else None
                )
                personal_list.append(personal)
            return personal_list
        finally:
            db.close()

    def get_personal(self, personal_id: int) -> Optional[Personal]:
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener el nombre del cargo
            result = db.execute(text("""
                SELECT 
                    p.id_personal, 
                    p.id_club, 
                    p.nombres, 
                    p.apellidos, 
                    p.cargo, 
                    p.fecha_ingreso, 
                    p.salario,
                    p.correo,
                    p.departamento, 
                    p.estado,
                    c.nombre_cargo
                FROM personal p
                LEFT JOIN cargos c ON p.cargo = c.id_cargo
                WHERE p.id_personal = :id_personal
            """), {"id_personal": personal_id}).fetchone()
            
            if result:
                # Convertir fecha de datetime a string si existe
                fecha_ingreso = str(result[5]) if result[5] else None
                return Personal(
                    id_personal=result[0],
                    id_club=result[1],
                    nombres=result[2],
                    apellidos=result[3],
                    cargo=result[4],
                    fecha_ingreso=fecha_ingreso,
                    salario=float(result[6]) if result[6] else 0.0,
                    correo=result[7] if result[7] else None,
                    departamento=result[8] if result[8] else None,
                    estado=bool(result[9]) if result[9] is not None else True,
                    nombre_cargo=result[10] if result[10] else None
                )
            return None
        finally:
            db.close()

    def create_personal(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO personal (id_club, nombres, apellidos, cargo, salario, correo, departamento, estado)
                VALUES (:id_club, :nombres, :apellidos, :cargo, :salario, :correo, :departamento, :estado)
                RETURNING id_personal, id_club, nombres, apellidos, cargo, fecha_ingreso, salario, correo, departamento, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            
            # Obtener el nombre del cargo
            nombre_cargo = self._get_nombre_cargo(db, row[4])
            
            # Convertir fecha de datetime a string si existe
            fecha_ingreso = str(row[5]) if row[5] else None
            return Personal(
                id_personal=row[0],
                id_club=row[1],
                nombres=row[2],
                apellidos=row[3],
                cargo=row[4],
                fecha_ingreso=fecha_ingreso,
                salario=float(row[6]) if row[6] else 0.0,
                correo=row[7] if row[7] else None,
                departamento=row[8] if row[8] else None,
                estado=bool(row[9]) if row[9] is not None else True,
                nombre_cargo=nombre_cargo
            )
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
    
    def _get_nombre_cargo(self, db: Session, id_cargo: int) -> Optional[str]:
        """Obtiene el nombre del cargo basado en el ID"""
        try:
            result = db.execute(text("""
                SELECT nombre_cargo FROM cargos WHERE id_cargo = :id_cargo
            """), {"id_cargo": id_cargo}).fetchone()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            logging.error(f"Error al obtener nombre del cargo: {str(e)}")
            return None 