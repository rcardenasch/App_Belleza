Migraciones manuales

Este proyecto usa Flask-Migrate/Alembic en desarrollo, pero la carpeta `migrations/` actualmente contiene migraciones SQL manuales para ejecutar si no se desea usar `flask db`.

Para agregar la columna faltante `duracion_promedio_minutos` a la tabla `disponibilidades`, ejecutar (ejemplo usando psql):

Windows (PowerShell):

```powershell
# Exportar URL de la BD si usas variables de entorno
$env:DATABASE_URL = "postgresql://user:pass@host:port/dbname"
psql $env:DATABASE_URL -f migrations/versions/0001_add_duracion_promedio.sql
```

Linux/macOS:

```bash
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
psql $DATABASE_URL -f migrations/versions/0001_add_duracion_promedio.sql
```

Alternativas preferidas:
- Si usas Flask-Migrate: ejecutar `flask db migrate -m "Add duracion_promedio_minutos"` y luego `flask db upgrade`.
- Si prefieres aplicar el SQL manualmente, el archivo anterior aplica el `ALTER TABLE` necesario.

Notas:
- Asegúrate de tener copia de seguridad antes de ejecutar migraciones en producción.
- Después de aplicar la migración, reinicia la aplicación si usa UWSGI/Gunicorn para que los cambios en el modelo y la DB estén sincronizados.
