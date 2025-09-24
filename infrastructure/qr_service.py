import qrcode
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

class QRService:
    def __init__(self):
        self.qr_codes_dir = "qr_codes"
        # Asegurar que el directorio existe
        os.makedirs(self.qr_codes_dir, exist_ok=True)
    
    def generar_qr_transferencia(self, id_accion: int, monto: float, concepto: str) -> Dict[str, Any]:
        """
        Genera QR con datos de transferencia bancaria
        """
        datos_transferencia = {
            "banco": "Banco Nacional de Bolivia",
            "cuenta": "1234567890",
            "titular": "Club CEAS",
            "monto": monto,
            "concepto": f"Compra de acción {id_accion} - {concepto}",
            "referencia": f"ACC{id_accion:06d}",
            "fecha_limite": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "telefono_contacto": "12345678",
            "email_contacto": "contacto@clubceas.com"
        }
        
        try:
            # Generar QR
            qr_code = qrcode.make(json.dumps(datos_transferencia, ensure_ascii=False))
            qr_path = os.path.join(self.qr_codes_dir, f"transferencia_{id_accion}.png")
            qr_code.save(qr_path)
            
            logging.info(f"QR generado exitosamente para acción {id_accion}")
            
            return {
                "tipo": "transferencia_bancaria",
                "qr_image": qr_path,
                "datos_transferencia": datos_transferencia,
                "instrucciones": [
                    "1. Escanea el código QR con tu app bancaria",
                    "2. Verifica los datos de la transferencia",
                    "3. Realiza la transferencia bancaria",
                    "4. Envía el comprobante por WhatsApp al 12345678",
                    "5. Espera la confirmación del pago"
                ]
            }
        except Exception as e:
            logging.error(f"Error generando QR para acción {id_accion}: {str(e)}")
            raise Exception(f"Error generando código QR: {str(e)}")
    
    def generar_qr_pago_movil(self, id_accion: int, monto: float) -> Dict[str, Any]:
        """
        Genera QR con datos de pago móvil (si está disponible)
        """
        datos_pago = {
            "tipo": "pago_movil",
            "numero": "12345678",
            "monto": monto,
            "concepto": f"Acción {id_accion}",
            "referencia": f"ACC{id_accion:06d}",
            "fecha_limite": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        }
        
        try:
            # Generar QR
            qr_code = qrcode.make(json.dumps(datos_pago, ensure_ascii=False))
            qr_path = os.path.join(self.qr_codes_dir, f"pago_movil_{id_accion}.png")
            qr_code.save(qr_path)
            
            logging.info(f"QR de pago móvil generado para acción {id_accion}")
            
            return {
                "tipo": "pago_movil",
                "qr_image": qr_path,
                "datos_pago": datos_pago,
                "instrucciones": [
                    "1. Escanea el código QR",
                    "2. Realiza el pago móvil",
                    "3. Guarda el comprobante",
                    "4. El pago se confirmará automáticamente"
                ]
            }
        except Exception as e:
            logging.error(f"Error generando QR de pago móvil para acción {id_accion}: {str(e)}")
            raise Exception(f"Error generando código QR de pago móvil: {str(e)}")
    
    def generar_qr_efectivo(self, id_accion: int, monto: float) -> Dict[str, Any]:
        """
        Genera instrucciones para pago en efectivo
        """
        return {
            "tipo": "efectivo",
            "monto": monto,
            "instrucciones": [
                "1. Acércate a las oficinas del club",
                "2. Realiza el pago en efectivo",
                "3. Recibe tu comprobante",
                "4. Tu acción será activada inmediatamente"
            ],
            "direccion_oficinas": "Av. Principal 123, La Paz, Bolivia",
            "horario_atencion": "Lunes a Viernes: 8:00 AM - 6:00 PM",
            "telefono_contacto": "12345678"
        }
    
    def generar_qr_pago(self, id_accion: int, monto: float, metodo_pago: str, concepto: str = "compra") -> Dict[str, Any]:
        """
        Genera QR según el método de pago seleccionado
        """
        if metodo_pago == "qr_transferencia":
            return self.generar_qr_transferencia(id_accion, monto, concepto)
        elif metodo_pago == "qr_pago_movil":
            return self.generar_qr_pago_movil(id_accion, monto)
        elif metodo_pago == "efectivo":
            return self.generar_qr_efectivo(id_accion, monto)
        else:
            raise ValueError(f"Método de pago no soportado: {metodo_pago}")
    
    def generar_qr_transferencia_bolivia(self, referencia_temporal: str, monto: float, cantidad_acciones: int, concepto: str) -> Dict[str, Any]:
        """
        Genera QR específico para transferencias bancarias en Bolivia
        """
        datos_transferencia = {
            "banco": "Banco Nacional de Bolivia",
            "cuenta": "1234567890",
            "titular": "Club CEAS",
            "monto": monto,
            "concepto": f"Compra de {cantidad_acciones} acciones - {concepto}",
            "referencia": referencia_temporal,
            "fecha_limite": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "telefono_contacto": "12345678",
            "email_contacto": "contacto@clubceas.com"
        }
        
        try:
            # Generar QR
            qr_code = qrcode.make(json.dumps(datos_transferencia, ensure_ascii=False))
            qr_path = os.path.join(self.qr_codes_dir, f"temp_{referencia_temporal}.png")
            qr_code.save(qr_path)
            
            logging.info(f"QR generado exitosamente para referencia {referencia_temporal}")
            
            return {
                "tipo": "transferencia_bancaria_bolivia",
                "qr_data": datos_transferencia,
                "instrucciones": [
                    "1. Realiza la transferencia bancaria con los datos mostrados",
                    "2. Envía el comprobante por WhatsApp al 12345678",
                    "3. El pago se confirmará automáticamente",
                    "4. Tu acción será activada inmediatamente"
                ]
            }
        except Exception as e:
            logging.error(f"Error generando QR para referencia {referencia_temporal}: {str(e)}")
            raise Exception(f"Error generando código QR: {str(e)}")
    
    def limpiar_qr_antiguos(self, dias_antiguedad: int = 7):
        """
        Limpia códigos QR antiguos para liberar espacio
        """
        try:
            import glob
            import time
            
            # Buscar archivos QR antiguos
            patron = os.path.join(self.qr_codes_dir, "*.png")
            archivos = glob.glob(patron)
            
            tiempo_limite = time.time() - (dias_antiguedad * 24 * 60 * 60)
            archivos_eliminados = 0
            
            for archivo in archivos:
                if os.path.getmtime(archivo) < tiempo_limite:
                    os.remove(archivo)
                    archivos_eliminados += 1
            
            logging.info(f"Se eliminaron {archivos_eliminados} códigos QR antiguos")
            return archivos_eliminados
            
        except Exception as e:
            logging.error(f"Error limpiando códigos QR antiguos: {str(e)}")
            return 0
