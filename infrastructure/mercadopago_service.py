import mercadopago
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from config import MERCADOPAGO_ACCESS_TOKEN, MERCADOPAGO_PUBLIC_KEY

class MercadoPagoService:
    def __init__(self):
        self.access_token = MERCADOPAGO_ACCESS_TOKEN
        self.public_key = MERCADOPAGO_PUBLIC_KEY
        self.sdk = mercadopago.SDK(self.access_token)
    
    def crear_pago_qr(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un pago con QR usando MercadoPago
        """
        try:
            # Crear preferencia de pago
            preference_data = {
                "items": [
                    {
                        "title": f"Compra de {datos_pago['cantidad_acciones']} acciones",
                        "quantity": 1,
                        "unit_price": float(datos_pago["total_pago"]),
                        "currency_id": "BOB"  # Bolivianos
                    }
                ],
                "external_reference": datos_pago["referencia_temporal"],
                "notification_url": "https://tu-dominio.com/mercadopago/webhook",
                "back_urls": {
                    "success": "https://tu-dominio.com/pago-exitoso",
                    "failure": "https://tu-dominio.com/pago-fallido",
                    "pending": "https://tu-dominio.com/pago-pendiente"
                },
                "auto_return": "approved",
                "metadata": {
                    "socio_id": str(datos_pago["id_socio"]),
                    "cantidad_acciones": str(datos_pago["cantidad_acciones"]),
                    "precio_unitario": str(datos_pago["precio_unitario"]),
                    "tipo_accion": datos_pago["tipo_accion"],
                    "referencia_temporal": datos_pago["referencia_temporal"]
                }
            }
            
            # Crear preferencia
            preference_response = self.sdk.preference().create(preference_data)
            
            if preference_response["status"] == 201:
                preference = preference_response["response"]
                
                logging.info(f"Preferencia MercadoPago creada: {preference['id']}")
                
                return {
                    "preference_id": preference["id"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference["sandbox_init_point"],
                    "status": "created",
                    "amount": datos_pago["total_pago"],
                    "currency": "BOB",
                    "external_reference": preference["external_reference"],
                    "metadata": preference["metadata"],
                    "qr_code": preference["init_point"],  # URL para QR
                    "checkout_url": preference["init_point"]
                }
            else:
                raise Exception(f"Error creando preferencia: {preference_response}")
                
        except Exception as e:
            logging.error(f"Error creando pago MercadoPago: {str(e)}")
            raise Exception(f"Error creando pago MercadoPago: {str(e)}")
    
    def verificar_pago(self, preference_id: str) -> Dict[str, Any]:
        """
        Verifica el estado de un pago en MercadoPago
        """
        try:
            # Obtener preferencia
            preference_response = self.sdk.preference().get(preference_id)
            
            if preference_response["status"] == 200:
                preference = preference_response["response"]
                
                return {
                    "preference_id": preference["id"],
                    "status": preference["status"],
                    "external_reference": preference["external_reference"],
                    "metadata": preference["metadata"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference["sandbox_init_point"]
                }
            else:
                raise Exception(f"Error obteniendo preferencia: {preference_response}")
                
        except Exception as e:
            logging.error(f"Error verificando pago MercadoPago: {str(e)}")
            raise Exception(f"Error verificando pago MercadoPago: {str(e)}")
    
    def buscar_pagos_por_referencia(self, external_reference: str) -> Dict[str, Any]:
        """
        Busca pagos por referencia externa
        """
        try:
            # Buscar pagos por referencia externa
            search_response = self.sdk.payment().search({
                "external_reference": external_reference
            })
            
            if search_response["status"] == 200:
                results = search_response["response"]
                
                return {
                    "total": results["total"],
                    "payments": results["results"],
                    "external_reference": external_reference
                }
            else:
                raise Exception(f"Error buscando pagos: {search_response}")
                
        except Exception as e:
            logging.error(f"Error buscando pagos MercadoPago: {str(e)}")
            raise Exception(f"Error buscando pagos MercadoPago: {str(e)}")
    
    def obtener_pago(self, payment_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles de un pago específico
        """
        try:
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                payment = payment_response["response"]
                
                return {
                    "payment_id": payment["id"],
                    "status": payment["status"],
                    "status_detail": payment["status_detail"],
                    "external_reference": payment["external_reference"],
                    "transaction_amount": payment["transaction_amount"],
                    "currency_id": payment["currency_id"],
                    "date_approved": payment["date_approved"],
                    "date_created": payment["date_created"],
                    "metadata": payment.get("metadata", {}),
                    "payment_method_id": payment["payment_method_id"],
                    "payment_type_id": payment["payment_type_id"]
                }
            else:
                raise Exception(f"Error obteniendo pago: {payment_response}")
                
        except Exception as e:
            logging.error(f"Error obteniendo pago MercadoPago: {str(e)}")
            raise Exception(f"Error obteniendo pago MercadoPago: {str(e)}")
    
    def procesar_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa webhooks de MercadoPago
        """
        try:
            action = webhook_data.get("action")
            data = webhook_data.get("data", {})
            
            if action == "payment.created":
                payment_id = data.get("id")
                payment_info = self.obtener_pago(payment_id)
                
                return {
                    "event_type": "payment.created",
                    "payment_id": payment_id,
                    "status": payment_info["status"],
                    "external_reference": payment_info["external_reference"],
                    "metadata": payment_info["metadata"],
                    "action": "monitorear_pago"
                }
            
            elif action == "payment.updated":
                payment_id = data.get("id")
                payment_info = self.obtener_pago(payment_id)
                
                if payment_info["status"] == "approved":
                    return {
                        "event_type": "payment.updated",
                        "payment_id": payment_id,
                        "status": "approved",
                        "external_reference": payment_info["external_reference"],
                        "metadata": payment_info["metadata"],
                        "action": "crear_accion"
                    }
                elif payment_info["status"] == "rejected":
                    return {
                        "event_type": "payment.updated",
                        "payment_id": payment_id,
                        "status": "rejected",
                        "external_reference": payment_info["external_reference"],
                        "metadata": payment_info["metadata"],
                        "action": "notificar_fallo"
                    }
                else:
                    return {
                        "event_type": "payment.updated",
                        "payment_id": payment_id,
                        "status": payment_info["status"],
                        "external_reference": payment_info["external_reference"],
                        "metadata": payment_info["metadata"],
                        "action": "monitorear_pago"
                    }
            
            else:
                return {
                    "event_type": action,
                    "status": "unhandled",
                    "message": f"Evento no manejado: {action}"
                }
                
        except Exception as e:
            logging.error(f"Error procesando webhook MercadoPago: {str(e)}")
            raise Exception(f"Error procesando webhook MercadoPago: {str(e)}")
    
    def obtener_configuracion_publica(self) -> Dict[str, str]:
        """
        Obtiene configuración pública de MercadoPago para el frontend
        """
        return {
            "public_key": self.public_key,
            "currency": "BOB",
            "country": "BO",
            "supported_payment_methods": ["boliviano", "transferencia_bancaria", "qr_code"]
        }
    
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
                "mercadopago_preference": datos_pago.get("preference_id", "pendiente")
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
