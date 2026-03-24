"""
Registro de asistencia (entrada/salida) para IQSystems.
Guarda los registros en un archivo CSV en la carpeta logs/.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Tiempo mínimo en segundos entre registros del mismo empleado
COOLDOWN_SECONDS = int(os.getenv("ATTENDANCE_COOLDOWN_SECONDS", "30"))

# Caché en memoria para evitar registros duplicados rápidos
_last_seen: dict[str, datetime] = {}


def _get_log_file() -> Path:
    """Retorna el archivo CSV del día actual."""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOGS_DIR / f"attendance_{today}.csv"


def _ensure_headers(file_path: Path):
    """Crea el archivo CSV con encabezados si no existe."""
    if not file_path.exists():
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["employee_id", "event", "timestamp", "confidence"])


def _determine_event(employee_id: str) -> str:
    """
    Determina si el evento es ENTRADA o SALIDA basado en los registros del día.
    El primer registro del día es ENTRADA, el segundo es SALIDA, y así alternando.
    """
    log_file = _get_log_file()
    if not log_file.exists():
        return "ENTRADA"

    count = 0
    with open(log_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["employee_id"] == employee_id:
                count += 1

    return "ENTRADA" if count % 2 == 0 else "SALIDA"


def register_event(employee_id: str, confidence: float) -> Optional[dict]:
    """
    Registra un evento de entrada o salida para un empleado.

    Args:
        employee_id: ID del empleado.
        confidence: Porcentaje de similitud del reconocimiento.

    Returns:
        dict con los detalles del evento registrado, o None si está en cooldown.
    """
    now = datetime.now()

    # Verificar cooldown para evitar doble registro accidental
    last = _last_seen.get(employee_id)
    if last and (now - last).total_seconds() < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - int((now - last).total_seconds())
        print(f"[{employee_id}] Espera {remaining}s antes del próximo registro.")
        return None

    event = _determine_event(employee_id)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    log_file = _get_log_file()
    _ensure_headers(log_file)

    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([employee_id, event, timestamp, f"{confidence:.2f}%"])

    _last_seen[employee_id] = now

    record = {
        "employee_id": employee_id,
        "event": event,
        "timestamp": timestamp,
        "confidence": confidence,
    }

    icon = "→" if event == "ENTRADA" else "←"
    print(f"{icon} [{event}] {employee_id} a las {now.strftime('%H:%M:%S')} ({confidence:.1f}% confianza)")

    return record


def get_today_records(employee_id: str = None) -> List[dict]:
    """
    Retorna los registros del día actual.

    Args:
        employee_id: Si se especifica, filtra solo ese empleado.
    """
    log_file = _get_log_file()
    if not log_file.exists():
        return []

    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if employee_id is None or row["employee_id"] == employee_id:
                records.append(dict(row))

    return records


def print_today_summary():
    """Imprime un resumen de asistencia del día."""
    records = get_today_records()
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*50}")
    print(f"  Resumen de asistencia - {today}")
    print(f"{'='*50}")

    if not records:
        print("  Sin registros para hoy.")
    else:
        print(f"  {'Empleado':<15} {'Evento':<10} {'Hora':<10} {'Confianza'}")
        print(f"  {'-'*45}")
        for r in records:
            hora = r["timestamp"].split(" ")[1] if " " in r["timestamp"] else r["timestamp"]
            print(f"  {r['employee_id']:<15} {r['event']:<10} {hora:<10} {r['confidence']}")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    # Prueba local sin AWS
    register_event("EMP001", 97.5)
    register_event("EMP002", 94.2)
    register_event("EMP001", 95.8)
    print_today_summary()
