# IQSystems - Control de Asistencia con Reconocimiento Facial

PoC de sistema de marcación de entrada/salida de empleados usando **Amazon Rekognition** y **FastAPI**.

## Cómo funciona

1. El empleado se para frente a la cámara y presiona **Escanear**
2. El navegador captura la imagen y la envía al backend
3. El backend consulta Amazon Rekognition para identificar el rostro
4. Si es reconocido, registra automáticamente **ENTRADA** o **SALIDA** según el último evento del día
5. El registro queda guardado en un CSV con timestamp

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Python 3.11 |
| Reconocimiento facial | Amazon Rekognition |
| Frontend | HTML + JavaScript vanilla |
| Deploy | Docker + Dokploy |

## Requisitos

- Python 3.9+
- Cuenta de AWS con permisos `AmazonRekognitionFullAccess`
- Docker (para deploy)

## Instalación local

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
cp .env.example .env
# Edita .env con tus credenciales de AWS
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1

REKOGNITION_COLLECTION_ID=iqsystems-employees
SIMILARITY_THRESHOLD=80
ATTENDANCE_COOLDOWN_SECONDS=30
```

| Variable | Descripción | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Clave de acceso AWS | — |
| `AWS_SECRET_ACCESS_KEY` | Clave secreta AWS | — |
| `AWS_REGION` | Región de AWS | `us-east-1` |
| `REKOGNITION_COLLECTION_ID` | Nombre de la colección | `iqsystems-employees` |
| `SIMILARITY_THRESHOLD` | % mínimo de similitud para reconocer | `80` |
| `ATTENDANCE_COOLDOWN_SECONDS` | Segundos entre registros del mismo empleado | `30` |

## Uso

### Iniciar el servidor web

```bash
python app.py
```

Abre `http://localhost:8000` en el navegador.

### Registrar empleados (CLI)

```bash
# Agregar fotos a data/employees/ y ejecutar:
python main.py --setup

# O registrar uno individual:
python main.py --add EMP001 data/employees/foto.jpg
```

Las fotos deben ser `.jpg`, `.jpeg` o `.png`, con el rostro visible y bien iluminado. El nombre del archivo se usa como ID del empleado.

### Otros comandos CLI

```bash
python main.py --list      # Ver empleados registrados
python main.py --summary   # Resumen de asistencia de hoy
```

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/scan` | Escanear rostro y registrar asistencia |
| `GET` | `/api/attendance/today` | Registros de asistencia del día |
| `GET` | `/api/employees` | Listar empleados registrados |
| `POST` | `/api/employees` | Registrar nuevo empleado |
| `DELETE` | `/api/employees/{id}` | Eliminar empleado |
| `POST` | `/api/setup` | Crear colección en Rekognition |

## Deploy en Dokploy

Ver [DOKPLOY_DEPLOY.md](DOKPLOY_DEPLOY.md) para instrucciones detalladas.

Resumen:
1. Sube el proyecto a GitHub
2. Crea la app en Dokploy con **Build Type: Dockerfile**
3. Configura las variables de entorno
4. Agrega un dominio con **HTTPS** (requerido para acceso a la cámara)
5. Deploy

## Estructura del proyecto

```
IQSystems/
├── app.py                  # Backend FastAPI
├── main.py                 # CLI para gestión local
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── rekognition/
│   ├── collection.py       # Gestión de colección en Rekognition
│   ├── recognize.py        # Búsqueda de rostros
│   └── attendance.py       # Lógica de entrada/salida
├── static/
│   └── index.html          # Interfaz web
├── data/
│   └── employees/          # Fotos de empleados
└── logs/                   # CSVs de asistencia por día
```

## Costos AWS (Free Tier)

Para un PoC con menos de 5,000 escaneos al mes el costo es **$0**.

| Operación | Free Tier |
|-----------|-----------|
| Registro de rostros (`IndexFaces`) | 5,000 llamadas/mes gratis |
| Reconocimiento (`SearchFacesByImage`) | 5,000 llamadas/mes gratis |
