# Configuración de AWS para IQSystems

## 1. Crear usuario IAM

1. Entra a la consola de AWS → **IAM** → **Usuarios** → **Crear usuario**
2. Nombre de usuario: `iqsystems-rekognition`
3. En **Permisos**, selecciona **Adjuntar políticas directamente**
4. Busca y selecciona: `AmazonRekognitionFullAccess`
5. Crea el usuario y ve a **Credenciales de seguridad**
6. Haz clic en **Crear clave de acceso** → selecciona **Aplicación local**
7. Guarda el **Access Key ID** y el **Secret Access Key**

---

## 2. Configurar credenciales

### Opción A: Archivo .env (recomendado para desarrollo)

Crea un archivo `.env` en la raíz del proyecto:

```env
AWS_ACCESS_KEY_ID=KEY
AWS_SECRET_ACCESS_KEY=TOKEN
AWS_REGION=us-east-1

REKOGNITION_COLLECTION_ID=iqsystems-employees
SIMILARITY_THRESHOLD=90
ATTENDANCE_COOLDOWN_SECONDS=30
```

### Opción B: AWS CLI

```bash
pip install awscli
aws configure
```

Ingresa tus claves cuando se solicite.

---

## 3. Instalar dependencias del proyecto

```bash
pip install -r requirements.txt
```

---

## 4. Registrar empleados

1. Agrega fotos de los empleados en `data/employees/`
   - El nombre del archivo será el ID del empleado
   - Ejemplo: `EMP001.jpg`, `EMP002.png`
   - Usa fotos claras, bien iluminadas, de frente

2. Ejecuta el setup:

```bash
python main.py --setup
```

---

## 5. Usar el sistema

```bash
# Iniciar control de asistencia (cámara en tiempo real)
python main.py

# Ver empleados registrados
python main.py --list

# Ver resumen de asistencia de hoy
python main.py --summary

# Registrar un empleado individual
python main.py --add EMP003 data/employees/EMP003.jpg
```

---

## Costos estimados de AWS Rekognition (Free Tier)

| Operación             | Free Tier                 | Costo después  |
| --------------------- | ------------------------- | -------------- |
| IndexFaces (registro) | 5,000 llamadas/mes gratis | $0.001/llamada |
| SearchFacesByImage    | 5,000 llamadas/mes gratis | $0.001/llamada |

Para un PoC con menos de 5,000 escaneos al mes, **el costo es $0**.
