from sqlalchemy import text
from config import SessionLocal

def check_socio_structure():
    db = SessionLocal()
    try:
        # Verificar estructura de la tabla socio
        print("=== ESTRUCTURA DE LA TABLA SOCIO ===")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'socio' 
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"Columna: {row[0]}, Tipo: {row[1]}, Nullable: {row[2]}")
        
        print("\n=== DATOS DE LA TABLA SOCIO ===")
        result = db.execute(text("SELECT * FROM socio LIMIT 3"))
        
        for row in result:
            print(f"Datos: {row}")
            
        print("\n=== ESTRUCTURA DE ESTADOSOCIO ===")
        result = db.execute(text("SELECT * FROM estadosocio"))
        
        for row in result:
            print(f"Estado: {row}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_socio_structure() 