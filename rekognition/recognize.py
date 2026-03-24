"""
Reconocimiento facial en tiempo real usando la cámara y Amazon Rekognition.
Captura frames, los envía a Rekognition y retorna el ID del empleado si es reconocido.
"""

import boto3
import os
import io
from typing import Optional
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

COLLECTION_ID = os.getenv("REKOGNITION_COLLECTION_ID", "iqsystems-employees")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "90"))


def get_client():
    return boto3.client("rekognition", region_name=AWS_REGION)


def frame_to_bytes(frame) -> bytes:
    """Convierte un frame de OpenCV a bytes JPEG."""
    import cv2
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


def search_face_in_collection(image_bytes: bytes) -> Optional[dict]:
    """
    Busca un rostro en la colección de Rekognition.

    Returns:
        dict con 'employee_id' y 'confidence', o None si no se reconoce.
    """
    client = get_client()
    try:
        response = client.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={"Bytes": image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=SIMILARITY_THRESHOLD,
        )

        matches = response.get("FaceMatches", [])
        if matches:
            best = matches[0]
            return {
                "employee_id": best["Face"]["ExternalImageId"],
                "confidence": round(best["Similarity"], 2),
                "face_id": best["Face"]["FaceId"],
            }
        return None

    except client.exceptions.InvalidParameterException:
        # No se detectó ningún rostro en la imagen
        return None
    except Exception as e:
        print(f"Error en Rekognition: {e}")
        return None


def draw_result(frame, result: Optional[dict], cooldown_active: bool = False):
    """Dibuja el resultado del reconocimiento sobre el frame."""
    import cv2
    h, w = frame.shape[:2]

    if cooldown_active:
        color = (0, 165, 255)  # Naranja
        label = "Procesando..."
    elif result:
        color = (0, 200, 0)  # Verde
        label = f"{result['employee_id']} ({result['confidence']}%)"
    else:
        color = (0, 0, 220)  # Rojo
        label = "No reconocido"

    # Barra superior
    cv2.rectangle(frame, (0, 0), (w, 50), color, -1)
    cv2.putText(frame, label, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Instrucciones en la parte inferior
    cv2.rectangle(frame, (0, h - 40), (w, h), (50, 50, 50), -1)
    cv2.putText(frame, "ESPACIO: escanear  |  Q: salir", (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    return frame


def capture_and_recognize(on_recognized_callback=None):
    """
    Abre la cámara y permite al usuario escanear su rostro.

    Args:
        on_recognized_callback: función que se llama cuando se reconoce un empleado.
                                 Recibe el dict con employee_id y confidence.
    """
    import cv2
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return

    print("Cámara lista. Presiona ESPACIO para escanear o Q para salir.")

    result = None
    cooldown = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = draw_result(frame.copy(), result, cooldown)
        cv2.imshow("IQSystems - Control de Asistencia", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord(" ") and not cooldown:
            cooldown = True
            result = None

            image_bytes = frame_to_bytes(frame)
            result = search_face_in_collection(image_bytes)

            if result:
                print(f"Reconocido: {result['employee_id']} ({result['confidence']}% similitud)")
                if on_recognized_callback:
                    on_recognized_callback(result)
            else:
                print("Rostro no reconocido o no detectado.")

            cooldown = False

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    def on_match(result):
        print(f"  → Empleado detectado: {result['employee_id']}")

    capture_and_recognize(on_recognized_callback=on_match)
