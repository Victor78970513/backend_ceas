# 🔐 Configuración de Google Drive para Certificados

## 📋 Pasos para configurar Google Drive

### 1️⃣ Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombra el proyecto: `CEAS-Certificados` (o el nombre que prefieras)

### 2️⃣ Habilitar Google Drive API

1. En el menú lateral, ve a **APIs y servicios** > **Biblioteca**
2. Busca "Google Drive API"
3. Haz clic en **HABILITAR**

### 3️⃣ Crear Cuenta de Servicio

1. Ve a **APIs y servicios** > **Credenciales**
2. Haz clic en **CREAR CREDENCIALES** > **Cuenta de servicio**
3. Completa:
   - **Nombre**: `ceas-certificados-service`
   - **Descripción**: `Servicio para subir certificados de CEAS`
4. Haz clic en **CREAR Y CONTINUAR**
5. En **Permisos**, selecciona:
   - **Rol**: `Editor` (o `Propietario` para más permisos)
6. Haz clic en **CONTINUAR** y luego **LISTO**

### 4️⃣ Generar Clave JSON

1. En la lista de cuentas de servicio, encuentra tu cuenta recién creada
2. Haz clic en el ícono de **Claves** (🔑)
3. Haz clic en **AGREGAR CLAVE** > **Crear nueva clave**
4. Selecciona **JSON** y haz clic en **CREAR**
5. Se descargará un archivo JSON

### 5️⃣ Configurar el Archivo

1. Renombra el archivo descargado a: `google_drive_credentials.json`
2. Muévelo a la carpeta: `credentials/google_drive_credentials.json`
3. **IMPORTANTE**: Agrega este archivo al `.gitignore` para no subirlo a Git

### 6️⃣ Estructura Final

```
credentials/
├── README_GOOGLE_DRIVE.md
├── google_drive_credentials.json  ← Tu archivo de credenciales
└── .gitignore                     ← Para excluir el JSON del Git
```

### 7️⃣ Configurar .gitignore

Agrega estas líneas al `.gitignore`:

```gitignore
# Google Drive Credentials
credentials/*.json
!credentials/.gitignore
```

## 🔧 Uso en el Código

Una vez configurado, el servicio se inicializará automáticamente:

```python
from infrastructure.google_drive_service import google_drive_service

# Verificar si está disponible
if google_drive_service.is_available():
    print("✅ Google Drive configurado")
else:
    print("❌ Google Drive no configurado")
```

## 📁 Estructura en Google Drive

El servicio creará automáticamente:

```
Google Drive/
└── CEAS_Certificados/
    ├── originales/          # Certificados PDF sin cifrar
    └── cifrados/           # Certificados cifrados
```

## 🚨 Seguridad

- **NUNCA** subas el archivo `google_drive_credentials.json` a Git
- Mantén las credenciales seguras
- Usa cuentas de servicio con permisos mínimos necesarios
- Considera rotar las credenciales periódicamente

## 🔄 Fallback Local

Si Google Drive no está configurado, el sistema automáticamente usará almacenamiento local como respaldo.
