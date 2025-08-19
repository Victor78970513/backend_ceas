from sqlalchemy import text
from config import SessionLocal

def check_tables():
    db = SessionLocal()
    try:
        # Lista de tablas que necesitamos verificar
        tables = [
            "usuario",
            "socio", 
            "club",
            "roles",
            "estadosocio",  # Cambiado de estado_socio a estadosocio
            "estado_accion",
            "modalidad_pago",
            "estado_pago",
            "tipo_pago",
            "cargos",
            "accion",
            "pago_accion",
            "personal",
            "asistencia",
            "movimiento_financiero",
            "logs_sistema",
            "inventario",
            "eventos",
            "reservas",
            "proveedores",
            "compras",
            "facturacion"
        ]
        
        print("Verificando tablas en la base de datos...")
        print("=" * 50)
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"✅ {table}: {count} registros")
            except Exception as e:
                print(f"❌ {table}: NO EXISTE - {str(e)}")
        
        print("=" * 50)
        print("Verificación completada.")
        
    except Exception as e:
        print(f"Error general: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tables() 