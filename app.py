"""
IQSystems - Backend FastAPI
"""

import os
import io
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IQSystems - Control de Asistencia")

# Servir archivos estáticos
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ──────────────────────────────────────────
# Rutas principales
# ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    index = Path("static/index.html")
    if index.exists():
        return HTMLResponse(index.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Frontend no encontrado")


# ──────────────────────────────────────────
# API - Reconocimiento y asistencia
# ──────────────────────────────────────────

@app.post("/api/scan")
async def scan_face(image: UploadFile = File(...)):
    """
    Recibe una imagen desde el navegador, la busca en Rekognition
    y registra la asistencia si se reconoce al empleado.
    """
    from rekognition.recognize import search_face_in_collection
    from rekognition.attendance import register_event

    image_bytes = await image.read()

    result = search_face_in_collection(image_bytes)

    if not result:
        return {"recognized": False, "message": "Rostro no reconocido"}

    record = register_event(result["employee_id"], result["confidence"])

    if record is None:
        return {
            "recognized": True,
            "employee_id": result["employee_id"],
            "confidence": result["confidence"],
            "message": "Registro reciente, espera un momento",
            "cooldown": True,
        }

    return {
        "recognized": True,
        "employee_id": result["employee_id"],
        "confidence": result["confidence"],
        "event": record["event"],
        "timestamp": record["timestamp"],
        "cooldown": False,
    }


@app.get("/api/attendance/today")
def get_today_attendance():
    """Retorna los registros de asistencia del día actual."""
    from rekognition.attendance import get_today_records
    records = get_today_records()
    return {"date": datetime.now().strftime("%Y-%m-%d"), "records": records}


# ──────────────────────────────────────────
# API - Gestión de empleados
# ──────────────────────────────────────────

@app.get("/api/employees")
def list_employees():
    """Lista todos los empleados registrados en Rekognition."""
    import boto3
    collection_id = os.getenv("REKOGNITION_COLLECTION_ID", "iqsystems-employees")
    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("rekognition", region_name=region)

    try:
        paginator = client.get_paginator("list_faces")
        employees = {}
        for page in paginator.paginate(CollectionId=collection_id):
            for face in page["Faces"]:
                emp_id = face.get("ExternalImageId", "Desconocido")
                employees[emp_id] = employees.get(emp_id, 0) + 1

        return {"employees": [{"id": k, "faces": v} for k, v in employees.items()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/employees")
async def register_employee(
    employee_id: str = Form(...),
    image: UploadFile = File(...),
):
    """Registra un nuevo empleado subiendo su foto."""
    from rekognition.collection import register_employee as rekognition_register

    # Guardar imagen temporalmente
    uploads_dir = Path("data/employees")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(image.filename).suffix or ".jpg"
    image_path = uploads_dir / f"{employee_id}{suffix}"

    with open(image_path, "wb") as f:
        f.write(await image.read())

    success = rekognition_register(employee_id, str(image_path))

    if not success:
        image_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No se detectó ningún rostro en la imagen")

    return {"success": True, "employee_id": employee_id}


@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: str):
    """Elimina un empleado de la colección."""
    from rekognition.collection import remove_employee
    remove_employee(employee_id)
    return {"success": True, "employee_id": employee_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
