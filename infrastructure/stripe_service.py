import stripe
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET

class StripeService:
    def __init__(self):
        stripe.api_key = STRIPE_SECRET_KEY
        self.webhook_secret = STRIPE_WEBHOOK_SECRET
    
    def crear_pago_qr(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un pago con QR usando Stripe
        """
        try:
            # Convertir monto a centavos (Stripe usa centavos)
            amount_cents = int(float(datos_pago["total_pago"]) * 100)
            
            # Crear PaymentIntent con método de pago QR
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',  # Stripe no soporta BOB directamente, usar USD
                payment_method_types=['card', 'alipay', 'wechat_pay'],  # Métodos que soportan QR
                metadata={
                    'socio_id': str(datos_pago["id_socio"]),
                    'cantidad_acciones': str(datos_pago["cantidad_acciones"]),
                    'precio_unitario': str(datos_pago["precio_unitario"]),
                    'referencia_temporal': datos_pago["referencia_temporal"],
                    'tipo_accion': datos_pago["tipo_accion"]
                },
                description=f"Compra de {datos_pago['cantidad_acciones']} acciones - {datos_pago['referencia_temporal']}"
            )
            
            logging.info(f"PaymentIntent creado: {payment_intent.id}")
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
                "description": payment_intent.description
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Error de Stripe: {str(e)}")
            raise Exception(f"Error de Stripe: {str(e)}")
        except Exception as e:
            logging.error(f"Error creando pago QR: {str(e)}")
            raise Exception(f"Error creando pago QR: {str(e)}")
    
    def crear_pago_qr_boliviano(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un pago con QR específico para Bolivia usando métodos locales
        """
        try:
            # Para Bolivia, usaremos un enfoque híbrido:
            # 1. Crear un PaymentIntent
            # 2. Generar un QR con datos de transferencia bancaria
            # 3. Usar webhooks para confirmar cuando llegue el pago
            
            amount_cents = int(float(datos_pago["total_pago"]) * 100)
            
            # Crear PaymentIntent con estado "requires_payment_method"
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                payment_method_types=['card'],
                capture_method='manual',  # Capturar manualmente cuando confirmemos el pago
                metadata={
                    'socio_id': str(datos_pago["id_socio"]),
                    'cantidad_acciones': str(datos_pago["cantidad_acciones"]),
                    'precio_unitario': str(datos_pago["precio_unitario"]),
                    'referencia_temporal': datos_pago["referencia_temporal"],
                    'tipo_accion': datos_pago["tipo_accion"],
                    'metodo_pago': 'transferencia_bancaria_bolivia',
                    'fecha_creacion': datetime.now().isoformat()
                },
                description=f"Compra de {datos_pago['cantidad_acciones']} acciones - {datos_pago['referencia_temporal']}"
            )
            
            # Generar datos para QR de transferencia bancaria
            qr_data = {
                "banco": "Banco Nacional de Bolivia",
                "cuenta": "1234567890",
                "titular": "Club CEAS",
                "monto": datos_pago["total_pago"],
                "concepto": f"Compra de {datos_pago['cantidad_acciones']} acciones - {datos_pago['referencia_temporal']}",
                "referencia": datos_pago["referencia_temporal"],
                "fecha_limite": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
                "telefono_contacto": "12345678",
                "email_contacto": "contacto@clubceas.com",
                "stripe_payment_intent": payment_intent.id
            }
            
            logging.info(f"PaymentIntent creado para Bolivia: {payment_intent.id}")
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
                "description": payment_intent.description,
                "qr_data": qr_data,
                "metodo_pago": "transferencia_bancaria_bolivia"
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Error de Stripe: {str(e)}")
            raise Exception(f"Error de Stripe: {str(e)}")
        except Exception as e:
            logging.error(f"Error creando pago QR boliviano: {str(e)}")
            raise Exception(f"Error creando pago QR boliviano: {str(e)}")
    
    def verificar_pago(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Verifica el estado de un pago en Stripe
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata,
                "created": payment_intent.created,
                "charges": payment_intent.charges.data if payment_intent.charges else []
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Error verificando pago: {str(e)}")
            raise Exception(f"Error verificando pago: {str(e)}")
    
    def confirmar_pago(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirma un pago en Stripe (para pagos manuales)
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata,
                "charges": payment_intent.charges.data if payment_intent.charges else []
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Error confirmando pago: {str(e)}")
            raise Exception(f"Error confirmando pago: {str(e)}")
    
    def cancelar_pago(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Cancela un pago en Stripe
        """
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Error cancelando pago: {str(e)}")
            raise Exception(f"Error cancelando pago: {str(e)}")
    
    def procesar_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Procesa webhooks de Stripe
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Manejar diferentes tipos de eventos
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                return self._procesar_pago_exitoso(payment_intent)
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                return self._procesar_pago_fallido(payment_intent)
            elif event['type'] == 'payment_intent.canceled':
                payment_intent = event['data']['object']
                return self._procesar_pago_cancelado(payment_intent)
            else:
                return {
                    "event_type": event['type'],
                    "status": "unhandled",
                    "message": f"Evento no manejado: {event['type']}"
                }
                
        except stripe.error.SignatureVerificationError as e:
            logging.error(f"Error verificando firma del webhook: {str(e)}")
            raise Exception(f"Error verificando firma del webhook: {str(e)}")
        except Exception as e:
            logging.error(f"Error procesando webhook: {str(e)}")
            raise Exception(f"Error procesando webhook: {str(e)}")
    
    def _procesar_pago_exitoso(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un pago exitoso
        """
        logging.info(f"Pago exitoso: {payment_intent['id']}")
        
        return {
            "event_type": "payment_intent.succeeded",
            "payment_intent_id": payment_intent['id'],
            "status": "success",
            "amount": payment_intent['amount'],
            "currency": payment_intent['currency'],
            "metadata": payment_intent['metadata'],
            "action": "crear_accion"
        }
    
    def _procesar_pago_fallido(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un pago fallido
        """
        logging.info(f"Pago fallido: {payment_intent['id']}")
        
        return {
            "event_type": "payment_intent.payment_failed",
            "payment_intent_id": payment_intent['id'],
            "status": "failed",
            "amount": payment_intent['amount'],
            "currency": payment_intent['currency'],
            "metadata": payment_intent['metadata'],
            "action": "notificar_fallo"
        }
    
    def _procesar_pago_cancelado(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un pago cancelado
        """
        logging.info(f"Pago cancelado: {payment_intent['id']}")
        
        return {
            "event_type": "payment_intent.canceled",
            "payment_intent_id": payment_intent['id'],
            "status": "canceled",
            "amount": payment_intent['amount'],
            "currency": payment_intent['currency'],
            "metadata": payment_intent['metadata'],
            "action": "limpiar_pago_temporal"
        }
    
    def obtener_configuracion_publica(self) -> Dict[str, str]:
        """
        Obtiene configuración pública de Stripe para el frontend
        """
        return {
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
            "currency": "usd",
            "country": "BO",
            "supported_payment_methods": ["card", "transferencia_bancaria"]
        }
