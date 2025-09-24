import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

class TempPaymentService:
    def __init__(self):
        self.temp_payments_dir = "temp_payments"
        os.makedirs(self.temp_payments_dir, exist_ok=True)
    
    def create_temp_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        Crea un pago temporal y retorna una referencia única
        """
        try:
            # Generar referencia única
            temp_ref = f"TEMP_{uuid.uuid4().hex[:8].upper()}"
            
            # Preparar datos del pago temporal
            temp_payment = {
                "referencia_temporal": temp_ref,
                "datos_pago": payment_data,
                "fecha_creacion": datetime.now().isoformat(),
                "fecha_limite": (datetime.now() + timedelta(hours=24)).isoformat(),
                "estado": "pendiente",
                "intentos": 0
            }
            
            # Guardar en archivo JSON
            file_path = os.path.join(self.temp_payments_dir, f"{temp_ref}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(temp_payment, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Pago temporal creado: {temp_ref}")
            return temp_ref
            
        except Exception as e:
            logging.error(f"Error creando pago temporal: {str(e)}")
            raise Exception(f"Error creando pago temporal: {str(e)}")
    
    def get_temp_payment(self, temp_ref: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un pago temporal por su referencia
        """
        try:
            file_path = os.path.join(self.temp_payments_dir, f"{temp_ref}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                temp_payment = json.load(f)
            
            # Verificar si no ha expirado
            fecha_limite = datetime.fromisoformat(temp_payment["fecha_limite"])
            if datetime.now() > fecha_limite:
                logging.warning(f"Pago temporal expirado: {temp_ref}")
                return None
            
            return temp_payment
            
        except Exception as e:
            logging.error(f"Error obteniendo pago temporal {temp_ref}: {str(e)}")
            return None
    
    def confirm_temp_payment(self, temp_ref: str, comprobante_path: str) -> Dict[str, Any]:
        """
        Confirma un pago temporal
        """
        try:
            temp_payment = self.get_temp_payment(temp_ref)
            
            if not temp_payment:
                raise Exception(f"Pago temporal no encontrado o expirado: {temp_ref}")
            
            # Actualizar estado
            temp_payment["estado"] = "confirmado"
            temp_payment["fecha_confirmacion"] = datetime.now().isoformat()
            temp_payment["comprobante_path"] = comprobante_path
            
            # Guardar cambios
            file_path = os.path.join(self.temp_payments_dir, f"{temp_ref}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(temp_payment, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Pago temporal confirmado: {temp_ref}")
            return temp_payment
            
        except Exception as e:
            logging.error(f"Error confirmando pago temporal {temp_ref}: {str(e)}")
            raise Exception(f"Error confirmando pago temporal: {str(e)}")
    
    def delete_temp_payment(self, temp_ref: str):
        """
        Elimina un pago temporal
        """
        try:
            file_path = os.path.join(self.temp_payments_dir, f"{temp_ref}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Pago temporal eliminado: {temp_ref}")
        except Exception as e:
            logging.error(f"Error eliminando pago temporal {temp_ref}: {str(e)}")
    
    def cleanup_expired_payments(self, hours_expired: int = 24):
        """
        Limpia pagos temporales expirados
        """
        try:
            import glob
            
            archivos_eliminados = 0
            tiempo_limite = datetime.now() - timedelta(hours=hours_expired)
            
            # Buscar todos los archivos de pagos temporales
            patron = os.path.join(self.temp_payments_dir, "TEMP_*.json")
            for archivo in glob.glob(patron):
                try:
                    # Leer fecha de creación
                    with open(archivo, "r", encoding="utf-8") as f:
                        temp_payment = json.load(f)
                    
                    fecha_creacion = datetime.fromisoformat(temp_payment["fecha_creacion"])
                    
                    if fecha_creacion < tiempo_limite:
                        os.remove(archivo)
                        archivos_eliminados += 1
                        logging.info(f"Pago temporal expirado eliminado: {archivo}")
                        
                except Exception as e:
                    logging.error(f"Error procesando archivo {archivo}: {str(e)}")
            
            logging.info(f"Se eliminaron {archivos_eliminados} pagos temporales expirados")
            return archivos_eliminados
            
        except Exception as e:
            logging.error(f"Error limpiando pagos temporales: {str(e)}")
            return 0
    
    def get_payment_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de pagos temporales
        """
        try:
            import glob
            
            patron = os.path.join(self.temp_payments_dir, "TEMP_*.json")
            archivos = glob.glob(patron)
            
            stats = {
                "total_pagos_temporales": len(archivos),
                "pendientes": 0,
                "confirmados": 0,
                "expirados": 0
            }
            
            for archivo in archivos:
                try:
                    with open(archivo, "r", encoding="utf-8") as f:
                        temp_payment = json.load(f)
                    
                    estado = temp_payment.get("estado", "pendiente")
                    fecha_limite = datetime.fromisoformat(temp_payment["fecha_limite"])
                    
                    if estado == "confirmado":
                        stats["confirmados"] += 1
                    elif datetime.now() > fecha_limite:
                        stats["expirados"] += 1
                    else:
                        stats["pendientes"] += 1
                        
                except Exception as e:
                    logging.error(f"Error procesando estadísticas para {archivo}: {str(e)}")
            
            return stats
            
        except Exception as e:
            logging.error(f"Error obteniendo estadísticas: {str(e)}")
            return {"error": str(e)}
