-- ==========================================
-- USUARIOS
-- ==========================================

CREATE TABLE usuarios
(
    id              SERIAL PRIMARY KEY,

    username        VARCHAR(100) UNIQUE NOT NULL,

    password_hash   VARCHAR(255) NOT NULL,

    rol             VARCHAR(50) NOT NULL,

    activo          BOOLEAN DEFAULT TRUE,

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- CLIENTES
-- ==========================================

CREATE TABLE clientes
(
    id              SERIAL PRIMARY KEY,

    nombres         VARCHAR(200) NOT NULL,

    telefono        VARCHAR(20) UNIQUE,

    email           VARCHAR(150),

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- SERVICIOS
-- ==========================================

CREATE TABLE servicios
(
    id                  SERIAL PRIMARY KEY,

    nombre              VARCHAR(150) NOT NULL,

    descripcion         TEXT,

    precio              NUMERIC(10,2) NOT NULL,

    duracion_minutos    INTEGER NOT NULL,

    imagen_url          VARCHAR(500),

    video_url           VARCHAR(500),

    activo              BOOLEAN DEFAULT TRUE,

    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- PROFESIONALES
-- ==========================================

CREATE TABLE profesionales
(
    id              SERIAL PRIMARY KEY,

    nombres         VARCHAR(150) NOT NULL,

    telefono        VARCHAR(20),

    foto_url        VARCHAR(500),

    activo          BOOLEAN DEFAULT TRUE,

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- RELACION PROFESIONAL - SERVICIO
-- ==========================================

CREATE TABLE profesional_servicio
(
    profesional_id INTEGER NOT NULL,

    servicio_id INTEGER NOT NULL,

    PRIMARY KEY
    (
        profesional_id,
        servicio_id
    ),

    CONSTRAINT fk_ps_profesional
        FOREIGN KEY (profesional_id)
        REFERENCES profesionales(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ps_servicio
        FOREIGN KEY (servicio_id)
        REFERENCES servicios(id)
        ON DELETE CASCADE
);

-- ==========================================
-- DISPONIBILIDAD SEMANAL
-- ==========================================

CREATE TABLE disponibilidades
(
    id SERIAL PRIMARY KEY,

    profesional_id INTEGER NOT NULL,

    dia_semana INTEGER NOT NULL,

    hora_inicio TIME NOT NULL,

    hora_fin TIME NOT NULL,

    activo BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_disp_profesional
        FOREIGN KEY (profesional_id)
        REFERENCES profesionales(id)
);

-- ==========================================
-- BLOQUEOS
-- ==========================================

CREATE TABLE bloqueos
(
    id SERIAL PRIMARY KEY,

    profesional_id INTEGER NOT NULL,

    fecha_inicio TIMESTAMP NOT NULL,

    fecha_fin TIMESTAMP NOT NULL,

    motivo VARCHAR(200),

    CONSTRAINT fk_bloqueo_profesional
        FOREIGN KEY (profesional_id)
        REFERENCES profesionales(id)
);

---

CREATE TABLE citas
(
    id SERIAL PRIMARY KEY,

    cliente_id INTEGER NOT NULL,

    profesional_id INTEGER NOT NULL,

    servicio_id INTEGER NOT NULL,

    fecha_inicio TIMESTAMP NOT NULL,

    fecha_fin TIMESTAMP NOT NULL,

    estado VARCHAR(30) NOT NULL,

    observacion TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cita_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),

    CONSTRAINT fk_cita_profesional
        FOREIGN KEY (profesional_id)
        REFERENCES profesionales(id),

    CONSTRAINT fk_cita_servicio
        FOREIGN KEY (servicio_id)
        REFERENCES servicios(id)
);
CREATE TABLE pagos
(
    id SERIAL PRIMARY KEY,

    cita_id INTEGER NOT NULL,

    monto NUMERIC(10,2) NOT NULL,

    comprobante_url VARCHAR(500),

    validado BOOLEAN DEFAULT FALSE,

    fecha_pago TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pago_cita
        FOREIGN KEY (cita_id)
        REFERENCES citas(id)
);

CREATE TABLE galeria_resultados
(
    id SERIAL PRIMARY KEY,

    servicio_id INTEGER NOT NULL,

    imagen_antes_url VARCHAR(500),

    imagen_despues_url VARCHAR(500),

    instagram_url VARCHAR(500),

    tiktok_url VARCHAR(500),

    testimonio TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_galeria_servicio
        FOREIGN KEY (servicio_id)
        REFERENCES servicios(id)
);

CREATE INDEX idx_citas_fecha
ON citas(fecha_inicio);

CREATE INDEX idx_citas_profesional
ON citas(profesional_id);

CREATE INDEX idx_citas_estado
ON citas(estado);

CREATE INDEX idx_cliente_telefono
ON clientes(telefono);

CREATE INDEX idx_profesional_nombre
ON profesionales(nombres);

CREATE INDEX idx_servicio_nombre
ON servicios(nombre);

-- datos iniciales
INSERT INTO usuarios
(
    username,
    password_hash,
    rol
)
VALUES
(
    'admin',
    'AQUI_HASH_GENERADO_POR_WERKZEUG',
    'admin'
);

INSERT INTO servicios
(
    nombre,
    descripcion,
    precio,
    duracion_minutos
)
VALUES

('Microblading',
 'Diseño profesional de cejas',
 250,
 120),

('Pestañas Premium',
 'Extensiones de pestañas',
 120,
 90),

('Laminado HD',
 'Laminado profesional',
 100,
 60);

 CREATE TABLE banners
(
    id SERIAL PRIMARY KEY,

    titulo VARCHAR(200),

    subtitulo TEXT,

    imagen_url VARCHAR(500),

    boton_texto VARCHAR(100),

    boton_url VARCHAR(300),

    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE testimonios
(
    id SERIAL PRIMARY KEY,

    cliente_nombre VARCHAR(150),

    comentario TEXT,

    puntuacion INTEGER,

    foto_url VARCHAR(500),

    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE promociones
(
    id SERIAL PRIMARY KEY,

    titulo VARCHAR(200),

    descripcion TEXT,

    descuento NUMERIC(5,2),

    fecha_inicio DATE,

    fecha_fin DATE,

    imagen_url VARCHAR(500),

    activo BOOLEAN DEFAULT TRUE
);
