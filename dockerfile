# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar primero el archivo de requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# 4. Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del proyecto al contenedor
COPY . .

# 6. Exponer el puerto en el que correrá Gunicorn
EXPOSE 5000

# 7. Comando para arrancar la app en producción usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
