-- Crear tablas faltantes que son referenciadas por otras tablas

-- Tabla estado_socio (referenciada por socio.estado)
CREATE TABLE IF NOT EXISTS estado_socio (
    id_estado BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_estado TEXT NOT NULL
);

-- Insertar datos básicos
INSERT INTO estado_socio (nombre_estado) VALUES 
    ('activo'),
    ('inactivo'),
    ('suspendido')
ON CONFLICT DO NOTHING;

-- Tabla estado_accion (referenciada por accion.estado_accion)
CREATE TABLE IF NOT EXISTS estado_accion (
    id_estado_accion BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_estado_accion TEXT NOT NULL
);

-- Insertar datos básicos
INSERT INTO estado_accion (nombre_estado_accion) VALUES 
    ('pendiente'),
    ('aprobada'),
    ('rechazada')
ON CONFLICT DO NOTHING;

-- Tabla modalidad_pago (referenciada por accion.modalidad_pago)
CREATE TABLE IF NOT EXISTS modalidad_pago (
    id_modalidad_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL,
    meses_de_gracia INT NOT NULL,
    porcentaje_renovacion_inicial DECIMAL(5,2) NOT NULL,
    porcentaje_renovacion_mensual DECIMAL(5,2) NOT NULL,
    costo_renovacion_estandar DECIMAL(10,2) NOT NULL
);

-- Insertar datos básicos
INSERT INTO modalidad_pago (descripcion, meses_de_gracia, porcentaje_renovacion_inicial, porcentaje_renovacion_mensual, costo_renovacion_estandar) VALUES 
    ('Mensual', 0, 5.00, 2.50, 100.00),
    ('Trimestral', 1, 10.00, 3.00, 250.00)
ON CONFLICT DO NOTHING;

-- Tabla estado_pago (referenciada por pago_accion.estado_pago)
CREATE TABLE IF NOT EXISTS estado_pago (
    id_estado_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL
);

-- Insertar datos básicos
INSERT INTO estado_pago (descripcion) VALUES 
    ('pendiente'),
    ('pagado'),
    ('anulado')
ON CONFLICT DO NOTHING;

-- Tabla tipo_pago (referenciada por pago_accion.tipo_pago)
CREATE TABLE IF NOT EXISTS tipo_pago (
    id_tipo_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion TEXT NOT NULL
);

-- Insertar datos básicos
INSERT INTO tipo_pago (descripcion) VALUES 
    ('efectivo'),
    ('transferencia'),
    ('tarjeta')
ON CONFLICT DO NOTHING;

-- Tabla cargos (referenciada por personal.cargo)
CREATE TABLE IF NOT EXISTS cargos (
    id_cargo BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_cargo TEXT NOT NULL
);

-- Insertar datos básicos
INSERT INTO cargos (nombre_cargo) VALUES 
    ('administrador'),
    ('secretario'),
    ('contador')
ON CONFLICT DO NOTHING;

-- Crear las demás tablas que faltan
CREATE TABLE IF NOT EXISTS accion (
    id_accion BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    modalidad_pago BIGINT NOT NULL REFERENCES modalidad_pago(id_modalidad_pago),
    estado_accion BIGINT NOT NULL REFERENCES estado_accion(id_estado_accion),
    certificado_pdf TEXT,
    certificado_cifrado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_emision_certificado TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    saldo_pendiente DECIMAL(10,2),
    tipo_accion TEXT
);

CREATE TABLE IF NOT EXISTS pago_accion (
    id_pago BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_accion BIGINT NOT NULL REFERENCES accion(id_accion),
    fecha_de_pago TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto DECIMAL(10,2) NOT NULL,
    tipo_pago BIGINT NOT NULL REFERENCES tipo_pago(id_tipo_pago),
    estado_pago BIGINT NOT NULL REFERENCES estado_pago(id_estado_pago),
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS personal (
    id_personal BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    cargo BIGINT NOT NULL REFERENCES cargos(id_cargo),
    fecha_ingreso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    salario DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_personal BIGINT NOT NULL REFERENCES personal(id_personal),
    fecha DATE NOT NULL,
    hora_ingreso TIME NOT NULL,
    hora_salida TIME,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS movimiento_financiero (
    id_movimiento BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    tipo_movimiento TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado TEXT NOT NULL,
    referencia_relacionada TEXT,
    metodo_pago TEXT
);

CREATE TABLE IF NOT EXISTS logs_sistema (
    id_log BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL REFERENCES usuario(id_usuario),
    accion_realizada TEXT NOT NULL,
    fecha_y_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modulo_o_tabla_afectada TEXT NOT NULL,
    id_afectado BIGINT,
    descripcion_detallada TEXT
);

CREATE TABLE IF NOT EXISTS inventario (
    id_producto BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_producto TEXT NOT NULL,
    descripcion TEXT,
    cantidad_en_stock INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    id_club BIGINT NOT NULL REFERENCES club(id_club)
);

CREATE TABLE IF NOT EXISTS eventos (
    id_evento BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_evento TEXT NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_club BIGINT NOT NULL REFERENCES club(id_club),
    estado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reservas (
    id_reserva BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    id_evento BIGINT NOT NULL REFERENCES eventos(id_evento),
    fecha_de_reserva TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_proveedor TEXT NOT NULL,
    contacto TEXT,
    telefono TEXT,
    correo_electronico TEXT,
    direccion TEXT
);

CREATE TABLE IF NOT EXISTS compras (
    id_compra BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_proveedor BIGINT NOT NULL REFERENCES proveedores(id_proveedor),
    fecha_de_compra TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto_total DECIMAL(10,2) NOT NULL,
    estado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facturacion (
    id_factura BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_socio BIGINT NOT NULL REFERENCES socio(id_socio),
    fecha_de_emision TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monto_total DECIMAL(10,2) NOT NULL,
    estado TEXT NOT NULL
); 