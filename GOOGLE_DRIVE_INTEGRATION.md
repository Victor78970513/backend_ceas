# ☁️ Integración con Google Drive para Certificados

## 📋 Resumen

He implementado una **integración completa con Google Drive** para almacenar los certificados de acciones. El sistema funciona de manera híbrida:

- **✅ Google Drive** (cuando está configurado) - Almacenamiento principal en la nube
- **📁 Almacenamiento local** - Respaldo automático cuando Google Drive no está disponible

## 🚀 Características Implementadas

### ✅ **Servicio de Google Drive**
- **Archivo**: `infrastructure/google_drive_service.py`
- **Funcionalidades**:
  - ✅ Subir certificados (originales y cifrados)
  - ✅ Descargar certificados
  - ✅ Listar certificados
  - ✅ Eliminar certificados
  - ✅ Crear carpetas automáticamente
  - ✅ Manejo de errores y fallback

### ✅ **Integración Automática**
- **Modificado**: `infrastructure/certificate_service.py`
- **Comportamiento**:
  - Genera certificados localmente
  - Intenta subir a Google Drive automáticamente
  - Si Google Drive falla, continúa con almacenamiento local
  - Retorna información de ambos almacenamientos

### ✅ **Estructura en Google Drive**
```
Google Drive/
└── CEAS_Certificados/
    ├── originales/          # Certificados PDF sin cifrar
    └── cifrados/           # Certificados cifrados por usuario
```

## 🔧 Configuración

### 1️⃣ **Instalar Dependencias**
```bash
python install_google_drive.py
```

### 2️⃣ **Configurar Google Cloud**
1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar Google Drive API
3. Crear cuenta de servicio
4. Descargar archivo JSON de credenciales

### 3️⃣ **Colocar Credenciales**
```
credentials/
├── google_drive_credentials.json  ← Tu archivo de credenciales
├── README_GOOGLE_DRIVE.md        ← Instrucciones detalladas
└── .gitignore                    ← Para excluir credenciales del Git
```

### 4️⃣ **Verificar Configuración**
```bash
python check_storage_status.py
python test_google_drive.py
```

## 📊 Estado Actual

### ✅ **Implementado y Funcionando**
- ✅ Generación automática de certificados
- ✅ Almacenamiento local (10 archivos originales, 10 cifrados)
- ✅ Integración con Google Drive lista para usar
- ✅ Fallback automático a almacenamiento local
- ✅ Cifrado por usuario con ID del socio

### ⚠️ **Pendiente de Configuración**
- ❌ Google Drive (requiere credenciales)
- ⚠️ 16 pagos temporales activos (se pueden limpiar)

## 🎯 Flujo de Funcionamiento

### **Con Google Drive Configurado:**
1. Usuario confirma pago
2. Se genera certificado localmente
3. Se cifra el certificado
4. Se sube **ambos** a Google Drive automáticamente
5. Se mantiene **respaldo local**
6. Respuesta incluye enlaces de Google Drive

### **Sin Google Drive:**
1. Usuario confirma pago
2. Se genera certificado localmente
3. Se cifra el certificado
4. Se almacena **solo localmente**
5. Respuesta indica almacenamiento local

## 🔐 Seguridad

### **Certificados Cifrados**
- ✅ Cifrado AES-256 con clave derivada del ID del socio
- ✅ Solo el socio correcto puede descifrar su certificado
- ✅ Archivos cifrados tienen extensión `.bin`

### **Credenciales**
- ✅ Archivos JSON excluidos del Git
- ✅ Cuenta de servicio con permisos mínimos
- ✅ Manejo seguro de errores

## 📈 Ventajas de Google Drive

### **✅ Para Producción**
- **Escalabilidad**: Sin límites de espacio local
- **Respaldo**: Archivos seguros en la nube
- **Acceso**: Descarga desde cualquier lugar
- **Colaboración**: Múltiples administradores pueden acceder
- **Auditoría**: Historial de cambios en Google Drive

### **✅ Para Desarrollo**
- **Fallback**: Si Google Drive falla, continúa con local
- **Testing**: Fácil de probar con archivos de prueba
- **Debugging**: Logs detallados de cada operación

## 🛠️ Scripts Disponibles

### **Instalación y Configuración**
```bash
python install_google_drive.py      # Instalar dependencias
python check_storage_status.py      # Verificar estado
python test_google_drive.py         # Probar funcionalidad
```

### **Uso en el Código**
```python
from infrastructure.google_drive_service import google_drive_service

# Verificar disponibilidad
if google_drive_service.is_available():
    # Subir certificado
    result = google_drive_service.upload_certificate(
        file_content, filename, is_encrypted=False
    )
```

## 🎉 Resultado Final

**¡Los certificados ahora se pueden guardar en Google Drive automáticamente!**

- ✅ **Funciona inmediatamente** con almacenamiento local
- ✅ **Se mejora automáticamente** cuando configures Google Drive
- ✅ **Sin cambios en el frontend** - todo es transparente
- ✅ **Respaldos automáticos** en ambos lugares
- ✅ **Escalable** para miles de certificados

**¿Quieres configurar Google Drive ahora o prefieres seguir con almacenamiento local por el momento?** 🤔
