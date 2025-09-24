import paypalrestsdk
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE

class PayPalService:
    def __init__(self):
        paypalrestsdk.configure({
            "mode": PAYPAL_MODE,  # "sandbox" o "live"
            "client_id": PAYPAL_CLIENT_ID,
            "client_secret": PAYPAL_CLIENT_SECRET
        })
    
    def crear_pago(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un pago con PayPal
        """
        try:
            # Crear pago de PayPal
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": "https://tu-dominio.com/pago-exitoso",
                    "cancel_url": "https://tu-dominio.com/pago-cancelado"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Compra de {datos_pago['cantidad_acciones']} acciones",
                            "sku": f"accion_{datos_pago['referencia_temporal']}",
                            "price": str(datos_pago["total_pago"]),
                            "currency": "USD",  # PayPal usa USD por defecto
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(datos_pago["total_pago"]),
                        "currency": "USD"
                    },
                    "description": f"Compra de {datos_pago['cantidad_acciones']} acciones - {datos_pago['referencia_temporal']}",
                    "custom": datos_pago["referencia_temporal"],
                    "invoice_number": datos_pago["referencia_temporal"]
                }]
            })
            
            # Crear el pago
            if payment.create():
                logging.info(f"Pago PayPal creado: {payment.id}")
                
                # Obtener URL de aprobación
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break
                
                return {
                    "payment_id": payment.id,
                    "state": payment.state,
                    "intent": payment.intent,
                    "amount": {
                        "total": payment.transactions[0].amount.total,
                        "currency": payment.transactions[0].amount.currency
                    },
                    "approval_url": approval_url,
                    "external_reference": datos_pago["referencia_temporal"],
                    "metadata": {
                        "socio_id": str(datos_pago["id_socio"]),
                        "cantidad_acciones": str(datos_pago["cantidad_acciones"]),
                        "precio_unitario": str(datos_pago["precio_unitario"]),
                        "tipo_accion": datos_pago["tipo_accion"],
                        "referencia_temporal": datos_pago["referencia_temporal"]
                    }
                }
            else:
                raise Exception(f"Error creando pago PayPal: {payment.error}")
                
        except Exception as e:
            logging.error(f"Error creando pago PayPal: {str(e)}")
            raise Exception(f"Error creando pago PayPal: {str(e)}")
    
    def ejecutar_pago(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """
        Ejecuta un pago de PayPal
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logging.info(f"Pago PayPal ejecutado: {payment.id}")
                
                return {
                    "payment_id": payment.id,
                    "state": payment.state,
                    "intent": payment.intent,
                    "amount": {
                        "total": payment.transactions[0].amount.total,
                        "currency": payment.transactions[0].amount.currency
                    },
                    "external_reference": payment.transactions[0].custom,
                    "metadata": {
                        "socio_id": payment.transactions[0].custom,
                        "cantidad_acciones": "1",  # Se puede extraer del nombre del item
                        "precio_unitario": payment.transactions[0].amount.total,
                        "tipo_accion": "compra"
                    }
                }
            else:
                raise Exception(f"Error ejecutando pago PayPal: {payment.error}")
                
        except Exception as e:
            logging.error(f"Error ejecutando pago PayPal: {str(e)}")
            raise Exception(f"Error ejecutando pago PayPal: {str(e)}")
    
    def obtener_pago(self, payment_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles de un pago de PayPal
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            return {
                "payment_id": payment.id,
                "state": payment.state,
                "intent": payment.intent,
                "amount": {
                    "total": payment.transactions[0].amount.total,
                    "currency": payment.transactions[0].amount.currency
                },
                "external_reference": payment.transactions[0].custom,
                "create_time": payment.create_time,
                "update_time": payment.update_time,
                "links": [{"rel": link.rel, "href": link.href} for link in payment.links]
            }
            
        except Exception as e:
            logging.error(f"Error obteniendo pago PayPal: {str(e)}")
            raise Exception(f"Error obteniendo pago PayPal: {str(e)}")
    
    def generar_qr_transferencia_bolivia(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera datos para QR de transferencia bancaria en Bolivia
        """
        try:
            qr_data = {
                "banco": "Banco Nacional de Bolivia",
                "cuenta": "1234567890",
                "titular": "Club CEAS",
                "monto": float(datos_pago["total_pago"]),
                "concepto": f"Compra de {datos_pago['cantidad_acciones']} acciones - {datos_pago['referencia_temporal']}",
                "referencia": datos_pago["referencia_temporal"],
                "fecha_limite": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
                "telefono_contacto": "12345678",
                "email_contacto": "contacto@clubceas.com",
                "paypal_payment_id": datos_pago.get("payment_id", "pendiente")
            }
            
            return {
                "tipo": "transferencia_bancaria_bolivia",
                "qr_data": qr_data,
                "instrucciones": [
                    "1. Realiza la transferencia bancaria con los datos mostrados",
                    "2. Envía el comprobante por WhatsApp al 12345678",
                    "3. El pago se confirmará automáticamente",
                    "4. Tu acción será activada inmediatamente"
                ]
            }
            
        except Exception as e:
            logging.error(f"Error generando QR transferencia Bolivia: {str(e)}")
            raise Exception(f"Error generando QR transferencia Bolivia: {str(e)}")
    
    def obtener_configuracion_publica(self) -> Dict[str, str]:
        """
        Obtiene configuración pública de PayPal para el frontend
        """
        return {
            "client_id": PAYPAL_CLIENT_ID,
            "mode": PAYPAL_MODE,
            "currency": "USD",
            "country": "BO",
            "supported_payment_methods": ["paypal", "transferencia_bancaria"]
        }
