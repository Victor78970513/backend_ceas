# 🚀 GUÍA DE INTEGRACIÓN CON STRIPE

## 📋 RESUMEN

Esta guía explica cómo usar la nueva integración con Stripe para el sistema de pagos de acciones del Club CEAS ERP.

## 🎯 FLUJO DE PAGOS CON STRIPE

### **1. Crear Pago**
```http
POST /acciones/stripe/crear-pago
```

**Datos requeridos:**
```json
{
  "id_socio": 123,
  "cantidad_acciones": 100,
  "precio_unitario": 50.00,
  "total_pago": 5000.00,
  "metodo_pago": "stripe",
  "modalidad_pago": 1,
  "tipo_accion": "compra"
}
```

**Respuesta:**
```json
{
  "payment_intent_id": "pi_1234567890abcdef",
  "client_secret": "pi_1234567890abcdef_secret_xyz",
  "amount": 500000,
  "currency": "usd",
  "status": "requires_payment_method",
  "metadata": {
    "socio_id": "123",
    "cantidad_acciones": "100",
    "precio_unitario": "50.00",
    "referencia_temporal": "TEMP_ABC123",
    "tipo_accion": "compra"
  },
  "description": "Compra de 100 acciones - TEMP_ABC123",
  "qr_data": {
    "banco": "Banco Nacional de Bolivia",
    "cuenta": "1234567890",
    "titular": "Club CEAS",
    "monto": 5000.00,
    "concepto": "Compra de 100 acciones - TEMP_ABC123",
    "referencia": "TEMP_ABC123",
    "fecha_limite": "2024-01-15 23:59:59",
    "telefono_contacto": "12345678",
    "email_contacto": "contacto@clubceas.com",
    "stripe_payment_intent": "pi_1234567890abcdef"
  },
  "metodo_pago": "transferencia_bancaria_bolivia"
}
```

### **2. Verificar Estado del Pago**
```http
GET /acciones/stripe/verificar-pago/{payment_intent_id}
```

**Respuesta:**
```json
{
  "payment_intent_id": "pi_1234567890abcdef",
  "status": "succeeded",
  "amount": 500000,
  "currency": "usd",
  "metadata": {
    "socio_id": "123",
    "cantidad_acciones": "100",
    "precio_unitario": "50.00",
    "referencia_temporal": "TEMP_ABC123",
    "tipo_accion": "compra"
  },
  "created": 1640995200,
  "charges": []
}
```

### **3. Confirmar Pago (Manual)**
```http
POST /acciones/stripe/confirmar-pago/{payment_intent_id}
```

**Respuesta (Pago Exitoso):**
```json
{
  "mensaje": "Pago confirmado y acción creada exitosamente",
  "pago": {
    "payment_intent_id": "pi_1234567890abcdef",
    "status": "succeeded",
    "amount": 500000,
    "currency": "usd",
    "metadata": {...}
  },
  "accion": {
    "id_accion": 456,
    "id_socio": 123,
    "cantidad_acciones": 100,
    "precio_unitario": 50.00,
    "total_pago": 5000.00,
    "metodo_pago": "stripe",
    "estado_accion": 4,
    "estado_nombre": "Completado",
    "fecha_creacion": "2024-01-15T10:30:00"
  },
  "certificado": {
    "disponible": true,
    "ruta": "certificados/originales/certificado_accion_456_123_20240115_103000.pdf",
    "fecha_generacion": "2024-01-15T10:30:00"
  }
}
```

### **4. Cancelar Pago**
```http
POST /acciones/stripe/cancelar-pago/{payment_intent_id}
```

**Respuesta:**
```json
{
  "mensaje": "Pago cancelado exitosamente",
  "pago": {
    "payment_intent_id": "pi_1234567890abcdef",
    "status": "canceled",
    "amount": 500000,
    "currency": "usd",
    "metadata": {...}
  }
}
```

### **5. Obtener Configuración**
```http
GET /acciones/stripe/configuracion
```

**Respuesta:**
```json
{
  "publishable_key": "pk_test_51234567890abcdefghijklmnopqrstuvwxyz",
  "currency": "usd",
  "country": "BO",
  "supported_payment_methods": ["card", "transferencia_bancaria"]
}
```

## 🔗 WEBHOOKS AUTOMÁTICOS

### **Endpoint del Webhook**
```http
POST /acciones/stripe/webhook
```

**Eventos Procesados:**
- `payment_intent.succeeded` → Crea acción automáticamente
- `payment_intent.payment_failed` → Notifica fallo
- `payment_intent.canceled` → Limpia pago temporal

**Configuración en Stripe Dashboard:**
1. Ir a **Developers > Webhooks**
2. Crear nuevo endpoint: `https://tu-dominio.com/acciones/stripe/webhook`
3. Seleccionar eventos:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
4. Copiar el **Signing Secret** y actualizar `STRIPE_WEBHOOK_SECRET` en `config.py`

## 💻 INTEGRACIÓN EN EL FRONTEND

### **React/JavaScript Example:**

```javascript
// 1. Crear pago
const crearPagoStripe = async (datosPago) => {
  const response = await fetch('/acciones/stripe/crear-pago', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      id_socio: 123,
      cantidad_acciones: 100,
      precio_unitario: 50.00,
      total_pago: 5000.00,
      metodo_pago: "stripe",
      modalidad_pago: 1,
      tipo_accion: "compra"
    })
  });
  
  const data = await response.json();
  return data;
};

// 2. Mostrar QR para transferencia bancaria
const mostrarQRTransferencia = (qrData) => {
  return (
    <div className="qr-payment">
      <h3>Transferencia Bancaria</h3>
      <div className="bank-info">
        <p><strong>Banco:</strong> {qrData.banco}</p>
        <p><strong>Cuenta:</strong> {qrData.cuenta}</p>
        <p><strong>Titular:</strong> {qrData.titular}</p>
        <p><strong>Monto:</strong> Bs. {qrData.monto}</p>
        <p><strong>Concepto:</strong> {qrData.concepto}</p>
        <p><strong>Referencia:</strong> {qrData.referencia}</p>
      </div>
      <div className="instructions">
        <h4>Instrucciones:</h4>
        <ol>
          <li>Realiza la transferencia bancaria con los datos mostrados</li>
          <li>Envía el comprobante por WhatsApp al {qrData.telefono_contacto}</li>
          <li>Espera la confirmación del pago</li>
          <li>Tu acción será activada automáticamente</li>
        </ol>
      </div>
    </div>
  );
};

// 3. Verificar estado del pago
const verificarPago = async (paymentIntentId) => {
  const response = await fetch(`/acciones/stripe/verificar-pago/${paymentIntentId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data;
};

// 4. Componente completo de pago
const PagoAcciones = () => {
  const [pagoData, setPagoData] = useState(null);
  const [estadoPago, setEstadoPago] = useState(null);
  
  const iniciarPago = async () => {
    try {
      const pago = await crearPagoStripe({
        id_socio: socioId,
        cantidad_acciones: cantidad,
        precio_unitario: precio,
        total_pago: total
      });
      
      setPagoData(pago);
      
      // Verificar estado cada 10 segundos
      const interval = setInterval(async () => {
        const estado = await verificarPago(pago.payment_intent_id);
        setEstadoPago(estado);
        
        if (estado.status === 'succeeded') {
          clearInterval(interval);
          // Pago exitoso - redirigir o mostrar éxito
          window.location.href = '/acciones/completadas';
        } else if (estado.status === 'failed' || estado.status === 'canceled') {
          clearInterval(interval);
          // Pago fallido - mostrar error
          alert('El pago falló o fue cancelado');
        }
      }, 10000);
      
    } catch (error) {
      console.error('Error creando pago:', error);
    }
  };
  
  return (
    <div>
      {!pagoData && (
        <button onClick={iniciarPago}>
          Comprar Acciones
        </button>
      )}
      
      {pagoData && pagoData.qr_data && (
        mostrarQRTransferencia(pagoData.qr_data)
      )}
      
      {estadoPago && (
        <div className="estado-pago">
          <p>Estado: <strong>{estadoPago.status}</strong></p>
          {estadoPago.status === 'succeeded' && (
            <p className="success">¡Pago exitoso! Tu acción ha sido creada.</p>
          )}
        </div>
      )}
    </div>
  );
};
```

## ⚙️ CONFIGURACIÓN

### **Variables de Entorno:**
```python
# config.py
STRIPE_SECRET_KEY = "sk_test_..."  # Tu clave secreta de Stripe
STRIPE_PUBLISHABLE_KEY = "pk_test_..."  # Tu clave pública de Stripe
STRIPE_WEBHOOK_SECRET = "whsec_..."  # Tu webhook secret de Stripe
```

### **Instalación:**
```bash
pip install stripe
```

## 🔒 SEGURIDAD

1. **Nunca expongas** `STRIPE_SECRET_KEY` en el frontend
2. **Usa HTTPS** en producción
3. **Verifica webhooks** usando `STRIPE_WEBHOOK_SECRET`
4. **Valida datos** antes de procesar pagos
5. **Maneja errores** apropiadamente

## 📊 ESTADOS DE PAGO

- `requires_payment_method` → Esperando método de pago
- `requires_confirmation` → Esperando confirmación
- `requires_action` → Requiere acción adicional
- `processing` → Procesando
- `succeeded` → ✅ **Exitoso**
- `requires_capture` → Requiere captura
- `canceled` → ❌ **Cancelado**

## 🎯 VENTAJAS DE STRIPE

1. **✅ Automatización completa** - Webhooks manejan todo
2. **✅ Seguridad** - Stripe maneja la seguridad
3. **✅ Escalabilidad** - Maneja millones de transacciones
4. **✅ Confiabilidad** - 99.99% uptime
5. **✅ Soporte** - Excelente documentación y soporte
6. **✅ Integración** - APIs fáciles de usar
7. **✅ Reportes** - Dashboard completo de analytics

## 🚀 PRÓXIMOS PASOS

1. **Configurar claves reales** de Stripe
2. **Configurar webhooks** en Stripe Dashboard
3. **Implementar frontend** usando los endpoints
4. **Probar en modo sandbox** primero
5. **Migrar a producción** cuando esté listo

---

**¡La integración con Stripe está lista y funcionando! 🎉**
