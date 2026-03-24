"""
Gestión de la colección de rostros en Amazon Rekognition.
Permite crear la colección, registrar empleados y eliminarlos.
"""

import boto3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

COLLECTION_ID = os.getenv("REKOGNITION_COLLECTION_ID", "iqsystems-employees")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def get_client():
    return boto3.client("rekognition", region_name=AWS_REGION)


def create_collection():
    """Crea la colección en Rekognition si no existe."""
    client = get_client()
    try:
        response = client.create_collection(CollectionId=COLLECTION_ID)
        print(f"Colección '{COLLECTION_ID}' creada. ARN: {response['CollectionArn']}")
    except client.exceptions.ResourceAlreadyExistsException:
        print(f"La colección '{COLLECTION_ID}' ya existe.")


def delete_collection():
    """Elimina la colección completa (usar con cuidado)."""
    client = get_client()
    try:
        client.delete_collection(CollectionId=COLLECTION_ID)
        print(f"Colección '{COLLECTION_ID}' eliminada.")
    except client.exceptions.ResourceNotFoundException:
        print(f"La colección '{COLLECTION_ID}' no existe.")


def register_employee(employee_id: str, image_path: str):
    """
    Registra un empleado en la colección usando una foto.

    Args:
        employee_id: ID único del empleado (ej: 'EMP001')
        image_path: Ruta a la imagen del empleado (.jpg o .png)
    """
    client = get_client()
    image_path = Path(image_path)

    if not image_path.exists():
        print(f"Error: no se encontró la imagen en '{image_path}'")
        return False

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    try:
        response = client.index_faces(
            CollectionId=COLLECTION_ID,
            Image={"Bytes": image_bytes},
            ExternalImageId=employee_id,
            DetectionAttributes=["DEFAULT"],
            MaxFaces=1,
            QualityFilter="AUTO",
        )

        faces = response.get("FaceRecords", [])
        if faces:
            face_id = faces[0]["Face"]["FaceId"]
            print(f"Empleado '{employee_id}' registrado. FaceId: {face_id}")
            return True
        else:
            print(f"No se detectó ningún rostro en la imagen de '{employee_id}'.")
            return False

    except Exception as e:
        print(f"Error al registrar '{employee_id}': {e}")
        return False


def remove_employee(employee_id: str):
    """Elimina todas las caras asociadas a un empleado."""
    client = get_client()

    # Buscar faces por ExternalImageId
    paginator = client.get_paginator("list_faces")
    face_ids = []

    for page in paginator.paginate(CollectionId=COLLECTION_ID):
        for face in page["Faces"]:
            if face.get("ExternalImageId") == employee_id:
                face_ids.append(face["FaceId"])

    if not face_ids:
        print(f"No se encontraron registros para '{employee_id}'.")
        return

    client.delete_faces(CollectionId=COLLECTION_ID, FaceIds=face_ids)
    print(f"Empleado '{employee_id}' eliminado ({len(face_ids)} rostro(s) removido(s)).")


def list_employees():
    """Lista todos los empleados registrados en la colección."""
    client = get_client()
    paginator = client.get_paginator("list_faces")
    employees = {}

    for page in paginator.paginate(CollectionId=COLLECTION_ID):
        for face in page["Faces"]:
            emp_id = face.get("ExternalImageId", "Desconocido")
            employees.setdefault(emp_id, []).append(face["FaceId"])

    if not employees:
        print("No hay empleados registrados.")
    else:
        print(f"\n{'ID Empleado':<20} {'Rostros registrados'}")
        print("-" * 40)
        for emp_id, faces in employees.items():
            print(f"{emp_id:<20} {len(faces)}")

    return employees


def register_all_from_folder(folder_path: str = "data/employees"):
    """
    Registra todos los empleados desde una carpeta.
    El nombre del archivo (sin extensión) se usa como employee_id.
    Ej: data/employees/EMP001.jpg → employee_id = 'EMP001'
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"La carpeta '{folder_path}' no existe.")
        return

    images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
    if not images:
        print(f"No se encontraron imágenes en '{folder_path}'.")
        return

    print(f"Registrando {len(images)} empleado(s)...\n")
    for img_path in images:
        employee_id = img_path.stem
        register_employee(employee_id, str(img_path))


if __name__ == "__main__":
    create_collection()
    register_all_from_folder()
    list_employees()
