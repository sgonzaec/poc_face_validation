# Deploy en Dokploy

## 1. Subir el proyecto a GitHub

```bash
git init
git add .
git commit -m "IQSystems - PoC reconocimiento facial"
git remote add origin https://github.com/TU_USUARIO/iqsystems.git
git push -u origin main
```

> Asegúrate de tener un `.gitignore` que excluya `.env`, `venv/`, `logs/` y `data/employees/`.

---

## 2. Crear la app en Dokploy

1. Entra a tu panel de Dokploy
2. Haz clic en **New Application**
3. Selecciona **GitHub** y conecta tu repositorio `iqsystems`
4. Tipo de build: **Dockerfile**
5. Puerto: `8000`

---

## 3. Configurar variables de entorno en Dokploy

En la sección **Environment Variables** agrega:

```
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
REKOGNITION_COLLECTION_ID=iqsystems-employees
SIMILARITY_THRESHOLD=80
ATTENDANCE_COOLDOWN_SECONDS=30
PORT=8000
```

---

## 4. Configurar dominio y HTTPS

> **IMPORTANTE:** La cámara del navegador solo funciona en HTTPS o en localhost.
> Dokploy genera un dominio con SSL automáticamente.

1. En la app, ve a **Domains**
2. Agrega el dominio que Dokploy te asigne (ej: `iqsystems.tuservidor.com`)
3. Activa **HTTPS** con Let's Encrypt

---

## 5. Deploy

Haz clic en **Deploy**. Dokploy construirá la imagen Docker y levantará el contenedor.

La app estará disponible en `https://iqsystems.tuservidor.com`.

---

## 6. Registrar empleados en producción

Una vez desplegado, desde la interfaz web puedes:
- Subir fotos de empleados directamente desde el navegador
- No necesitas correr `--setup` manualmente

O si prefieres hacerlo antes del deploy, corre localmente:
```bash
python main.py --setup
```

---

## Probar localmente con Docker antes de subir

```bash
docker compose up --build
```

Abre `http://localhost:8000` en el navegador.
