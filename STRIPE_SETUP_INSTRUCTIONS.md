# 🔧 CONFIGURACIÓN DE STRIPE

## ⚠️ ERROR ACTUAL
El error `500 Server Error` se debe a que las claves de Stripe en `config.py` son de prueba y no válidas.

## 🚀 PASOS PARA CONFIGURAR STRIPE

### **1. Crear Cuenta en Stripe**
1. Ve a https://stripe.com
2. Crea una cuenta gratuita
3. Completa la verificación

### **2. Obtener Claves de API**
1. En el Dashboard de Stripe, ve a **Developers > API keys**
2. Copia las claves:
   - **Publishable key** (pk_test_...)
   - **Secret key** (sk_test_...)

### **3. Actualizar config.py**
```python
# config.py
STRIPE_SECRET_KEY = "sk_test_TU_CLAVE_REAL_AQUI"
STRIPE_PUBLISHABLE_KEY = "pk_test_TU_CLAVE_REAL_AQUI"
STRIPE_WEBHOOK_SECRET = "whsec_TU_WEBHOOK_SECRET_AQUI"
```

### **4. Configurar Webhook (Opcional para pruebas)**
1. Ve a **Developers > Webhooks**
2. Crea endpoint: `http://localhost:8000/acciones/stripe/webhook`
3. Selecciona eventos:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
4. Copia el **Signing Secret**

## 🧪 PRUEBA RÁPIDA SIN STRIPE

Si quieres probar sin configurar Stripe, puedes usar el endpoint anterior:

```http
POST /acciones/generar-qr-pago
```

Este endpoint funciona sin Stripe y genera QR para transferencias bancarias.

## 📋 ENDPOINTS DISPONIBLES

### **Con Stripe (Recomendado):**
- `POST /acciones/stripe/crear-pago`
- `GET /acciones/stripe/verificar-pago/{id}`
- `POST /acciones/stripe/confirmar-pago/{id}`
- `POST /acciones/stripe/webhook`

### **Sin Stripe (Para pruebas):**
- `POST /acciones/generar-qr-pago`
- `POST /acciones/confirmar-pago`

## 🎯 RECOMENDACIÓN

**Para desarrollo:** Usa el endpoint sin Stripe primero
**Para producción:** Configura Stripe para automatización completa

¿Quieres que configuremos Stripe o prefieres usar el sistema sin Stripe por ahora?
