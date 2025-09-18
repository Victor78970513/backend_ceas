-- =====================================================
-- SCRIPT COMPLETO DE CREACIÓN DE BASE DE DATOS CEAS
-- =====================================================
-- Este script recrea toda la estructura de la base de datos
-- para el sistema ERP de CEAS (Club de Emprendedores y Accionistas)

-- Crear la base de datos si no existe
-- CREATE DATABASE ceas_bd;

-- Conectar a la base de datos ceas_bd
-- \c ceas_bd;

-- =====================================================
-- TABLAS DE CATÁLOGOS (TABLAS MAESTRAS)
-- =====================================================

-- Tabla de clubes
CREATE TABLE IF NOT EXISTS club (
    id_club BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_club TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT,
    correo_electronico TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado BOOLEAN DEFAULT TRUE
);

-- Tabla de roles de usuario
CREATE TABLE IF NOT EXISTS roles (
    id_rol BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_rol TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    permisos TEXT[]
);

-- Tabla de estados de socio
CREATE TABLE IF NOT EXISTS estado_socio (
    id_estado BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_estado TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de estados de acción
CREATE TABLE IF NOT EXISTS estado_accion (
    id_estado_accion BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_estado_accion TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de modalidades de pago
CREATE TABLE IF NOT EXISTS modalidad_pago (
    id_modalidad_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL,
    meses_de_gracia INT NOT NULL DEFAULT 0,
    porcentaje_renovacion_inicial DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    porcentaje_renovacion_mensual DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    costo_renovacion_estandar DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    cantidad_cuotas INT NOT NULL DEFAULT 1,
    estado BOOLEAN DEFAULT TRUE
);

-- Tabla de estados de pago
CREATE TABLE IF NOT EXISTS estado_pago (
    id_estado_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL UNIQUE,
    descripcion_larga TEXT
);

-- Tabla de tipos de pago
CREATE TABLE IF NOT EXISTS tipo_pago (
    id_tipo_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL UNIQUE,
    descripcion_larga TEXT
);

-- Tabla de cargos
CREATE TABLE IF NOT EXISTS cargos (
    id_cargo BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_cargo TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    departamento TEXT,
    nivel_hierarquico INT DEFAULT 1
);

-- =====================================================
-- TABLAS PRINCIPALES DEL SISTEMA
-- =====================================================

-- Tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol BIGINT NOT NULL REFERENCES roles(id_rol),
    estado TEXT NOT NULL DEFAULT 'activo',
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    correo_electronico TEXT UNIQUE,
    ultimo_acceso TIMESTAMP WITH TIME ZONE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de socios
CREATE TABLE IF NOT EXISTS socio (
    id_socio BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    ci_nit TEXT NOT NULL,
    telefono TEXT,
    correo_electronico TEXT,
    direccion TEXT,
    estado BIGINT NOT NULL REFERENCES estado_socio(id_estado),
    fecha_de_registro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_nacimiento DATE,
    tipo_membresia TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de acciones
CREATE TABLE IF NOT EXISTS accion (
    id_accion BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    modalidad_pago BIGINT NOT NULL REFERENCES modalidad_pago(id_modalidad_pago),
    estado_accion BIGINT NOT NULL REFERENCES estado_accion(id_estado_accion),
    certificado_pdf TEXT,
    certificado_cifrado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_emision_certificado TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    saldo_pendiente DECIMAL(10,2) DEFAULT 0.00,
    tipo_accion TEXT,
    socio_titular TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de pagos de acciones
CREATE TABLE IF NOT EXISTS pago_accion (
    id_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_accion BIGINT NOT NULL REFERENCES accion(id_accion),
    fecha_de_pago TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto DECIMAL(10,2) NOT NULL,
    tipo_pago BIGINT NOT NULL REFERENCES tipo_pago(id_tipo_pago),
    estado_pago BIGINT NOT NULL REFERENCES estado_pago(id_estado_pago),
    observaciones TEXT,
    numero_comprobante TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de personal
CREATE TABLE IF NOT EXISTS personal (
    id_personal BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    cargo BIGINT NOT NULL REFERENCES cargos(id_cargo),
    fecha_ingreso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    salario DECIMAL(10,2) NOT NULL,
    correo TEXT,
    departamento TEXT,
    estado BOOLEAN DEFAULT TRUE,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de asistencia
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_personal BIGINT NOT NULL REFERENCES personal(id_personal),
    fecha DATE NOT NULL,
    hora_ingreso TIME,
    hora_salida TIME,
    observaciones TEXT,
    estado TEXT DEFAULT 'PRESENTE',
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de movimientos financieros
CREATE TABLE IF NOT EXISTS movimiento_financiero (
    id_movimiento BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    tipo_movimiento TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado TEXT NOT NULL,
    referencia_relacionada TEXT,
    metodo_pago TEXT,
    numero_comprobante TEXT,
    categoria TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de logs del sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id_log BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL REFERENCES usuario(id_usuario),
    accion_realizada TEXT NOT NULL,
    fecha_y_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modulo_o_tabla_afectada TEXT NOT NULL,
    id_afectado BIGINT,
    descripcion_detallada TEXT,
    ip_address INET,
    user_agent TEXT
);

-- Tabla de inventario
CREATE TABLE IF NOT EXISTS inventario (
    id_producto BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_producto TEXT NOT NULL,
    descripcion TEXT,
    cantidad_en_stock INT NOT NULL DEFAULT 0,
    precio_unitario DECIMAL(10,2) NOT NULL,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    categoria TEXT,
    codigo_producto TEXT UNIQUE,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id_evento BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_evento TEXT NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    estado TEXT NOT NULL DEFAULT 'programado',
    capacidad_maxima INT,
    costo_participacion DECIMAL(10,2) DEFAULT 0.00,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id_reserva BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    id_evento BIGINT NOT NULL REFERENCES eventos(id_evento),
    fecha_de_reserva TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado TEXT NOT NULL DEFAULT 'confirmada',
    observaciones TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_proveedor TEXT NOT NULL,
    contacto TEXT,
    telefono TEXT,
    correo_electronico TEXT,
    direccion TEXT,
    nit TEXT UNIQUE,
    estado BOOLEAN DEFAULT TRUE,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de compras
CREATE TABLE IF NOT EXISTS compras (
    id_compra BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_proveedor BIGINT NOT NULL REFERENCES proveedores(id_proveedor),
    fecha_de_compra TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto_total DECIMAL(10,2) NOT NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    numero_factura TEXT,
    observaciones TEXT,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de facturación
CREATE TABLE IF NOT EXISTS facturacion (
    id_factura BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    fecha_de_emision TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto_total DECIMAL(10,2) NOT NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    numero_factura TEXT UNIQUE,
    concepto TEXT,
    fecha_vencimiento DATE,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INSERTAR DATOS INICIALES
-- =====================================================

-- Insertar club por defecto
INSERT INTO club (nombre_club, direccion, telefono, correo_electronico) 
VALUES ('Club de Emprendedores y Accionistas', 'Dirección Principal', '123456789', 'info@ceas.com')
ON CONFLICT DO NOTHING;

-- Insertar roles
INSERT INTO roles (nombre_rol, descripcion, permisos) VALUES 
('administrador', 'Administrador del sistema', ARRAY['all']),
('secretario', 'Secretario del club', ARRAY['socios', 'acciones', 'pagos']),
('contador', 'Contador del club', ARRAY['finanzas', 'reportes']),
('usuario', 'Usuario básico', ARRAY['consulta'])
ON CONFLICT (nombre_rol) DO NOTHING;

-- Insertar estados de socio
INSERT INTO estado_socio (nombre_estado, descripcion) VALUES 
('activo', 'Socio activo'),
('inactivo', 'Socio inactivo'),
('suspendido', 'Socio suspendido'),
('retirado', 'Socio retirado')
ON CONFLICT (nombre_estado) DO NOTHING;

-- Insertar estados de acción
INSERT INTO estado_accion (nombre_estado_accion, descripcion) VALUES 
('pendiente', 'Acción pendiente de aprobación'),
('aprobada', 'Acción aprobada'),
('rechazada', 'Acción rechazada'),
('cancelada', 'Acción cancelada')
ON CONFLICT (nombre_estado_accion) DO NOTHING;

-- Insertar modalidades de pago
INSERT INTO modalidad_pago (descripcion, meses_de_gracia, porcentaje_renovacion_inicial, porcentaje_renovacion_mensual, costo_renovacion_estandar, cantidad_cuotas) VALUES 
('Mensual', 0, 5.00, 2.50, 100.00, 12),
('Trimestral', 1, 10.00, 3.00, 250.00, 4),
('Semestral', 2, 15.00, 3.50, 500.00, 2),
('Anual', 3, 20.00, 4.00, 1000.00, 1)
ON CONFLICT DO NOTHING;

-- Insertar estados de pago
INSERT INTO estado_pago (descripcion, descripcion_larga) VALUES 
('pendiente', 'Pago pendiente'),
('pagado', 'Pago completado'),
('anulado', 'Pago anulado'),
('vencido', 'Pago vencido')
ON CONFLICT (descripcion) DO NOTHING;

-- Insertar tipos de pago
INSERT INTO tipo_pago (descripcion, descripcion_larga) VALUES 
('efectivo', 'Pago en efectivo'),
('transferencia', 'Transferencia bancaria'),
('tarjeta', 'Pago con tarjeta'),
('cheque', 'Pago con cheque')
ON CONFLICT (descripcion) DO NOTHING;

-- Insertar cargos
INSERT INTO cargos (nombre_cargo, descripcion, departamento, nivel_hierarquico) VALUES 
('presidente', 'Presidente del club', 'Dirección', 1),
('vicepresidente', 'Vicepresidente del club', 'Dirección', 2),
('secretario', 'Secretario del club', 'Administración', 3),
('tesorero', 'Tesorero del club', 'Finanzas', 3),
('contador', 'Contador del club', 'Finanzas', 4),
('administrador', 'Administrador del sistema', 'Sistemas', 2)
ON CONFLICT (nombre_cargo) DO NOTHING;

-- =====================================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para tabla socio
CREATE INDEX IF NOT EXISTS idx_socio_club ON socio(id_club);
CREATE INDEX IF NOT EXISTS idx_socio_estado ON socio(estado);
CREATE INDEX IF NOT EXISTS idx_socio_ci_nit ON socio(ci_nit);
CREATE INDEX IF NOT EXISTS idx_socio_fecha_registro ON socio(fecha_de_registro);

-- Índices para tabla accion
CREATE INDEX IF NOT EXISTS idx_accion_socio ON accion(id_socio);
CREATE INDEX IF NOT EXISTS idx_accion_club ON accion(id_club);
CREATE INDEX IF NOT EXISTS idx_accion_estado ON accion(estado_accion);
CREATE INDEX IF NOT EXISTS idx_accion_fecha ON accion(fecha_emision_certificado);

-- Índices para tabla pago_accion
CREATE INDEX IF NOT EXISTS idx_pago_accion ON pago_accion(id_accion);
CREATE INDEX IF NOT EXISTS idx_pago_fecha ON pago_accion(fecha_de_pago);
CREATE INDEX IF NOT EXISTS idx_pago_estado ON pago_accion(estado_pago);

-- Índices para tabla personal
CREATE INDEX IF NOT EXISTS idx_personal_club ON personal(id_club);
CREATE INDEX IF NOT EXISTS idx_personal_cargo ON personal(cargo);
CREATE INDEX IF NOT EXISTS idx_personal_estado ON personal(estado);

-- Índices para tabla asistencia
CREATE INDEX IF NOT EXISTS idx_asistencia_personal ON asistencia(id_personal);
CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(fecha);

-- Índices para tabla movimiento_financiero
CREATE INDEX IF NOT EXISTS idx_movimiento_club ON movimiento_financiero(id_club);
CREATE INDEX IF NOT EXISTS idx_movimiento_tipo ON movimiento_financiero(tipo_movimiento);
CREATE INDEX IF NOT EXISTS idx_movimiento_fecha ON movimiento_financiero(fecha);

-- Índices para tabla logs_sistema
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON logs_sistema(id_usuario);
CREATE INDEX IF NOT EXISTS idx_logs_fecha ON logs_sistema(fecha_y_hora);
CREATE INDEX IF NOT EXISTS idx_logs_modulo ON logs_sistema(modulo_o_tabla_afectada);

-- =====================================================
-- CREAR TRIGGERS PARA FECHAS DE ACTUALIZACIÓN
-- =====================================================

-- Función para actualizar fecha_actualizacion
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar fecha_actualizacion automáticamente
CREATE TRIGGER update_usuario_updated_at BEFORE UPDATE ON usuario FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_socio_updated_at BEFORE UPDATE ON socio FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accion_updated_at BEFORE UPDATE ON accion FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pago_accion_updated_at BEFORE UPDATE ON pago_accion FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_personal_updated_at BEFORE UPDATE ON personal FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_asistencia_updated_at BEFORE UPDATE ON asistencia FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_movimiento_financiero_updated_at BEFORE UPDATE ON movimiento_financiero FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventario_updated_at BEFORE UPDATE ON inventario FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_eventos_updated_at BEFORE UPDATE ON eventos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON reservas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_proveedores_updated_at BEFORE UPDATE ON proveedores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_compras_updated_at BEFORE UPDATE ON compras FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_facturacion_updated_at BEFORE UPDATE ON facturacion FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VERIFICACIÓN FINAL
-- =====================================================

-- Verificar que todas las tablas se crearon correctamente
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Mostrar resumen de tablas creadas
SELECT 
    COUNT(*) as total_tables,
    'Tablas creadas exitosamente' as mensaje
FROM pg_tables 
WHERE schemaname = 'public';

-- =====================================================
-- MENSAJE FINAL
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'BASE DE DATOS CEAS CREADA EXITOSAMENTE';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Todas las tablas, índices y datos iniciales han sido creados.';
    RAISE NOTICE 'El sistema está listo para usar.';
    RAISE NOTICE '=====================================================';
END $$;
