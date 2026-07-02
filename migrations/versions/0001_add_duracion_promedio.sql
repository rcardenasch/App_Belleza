-- Añade la columna `duracion_promedio_minutos` a la tabla `disponibilidades`.
-- Ejecutar con psql o herramienta equivalente conectada a la BD de producción/local.

BEGIN;

ALTER TABLE disponibilidades
    ADD COLUMN IF NOT EXISTS duracion_promedio_minutos integer DEFAULT 60;

COMMIT;
