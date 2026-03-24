"""
IQSystems - Sistema de Control de Asistencia con Reconocimiento Facial
Punto de entrada principal.

Uso:
  python main.py                  → Inicia el sistema de asistencia
  python main.py --setup          → Crea la colección y registra empleados desde data/employees/
  python main.py --list           → Lista empleados registrados
  python main.py --summary        → Muestra resumen de asistencia de hoy
  python main.py --add EMP001 foto.jpg  → Registra un empleado individual
"""

import argparse
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def check_aws_config():
    """Verifica que las credenciales de AWS estén configuradas."""
    required = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print("Error: Faltan variables de entorno de AWS:")
        for k in missing:
            print(f"  - {k}")
        print("\nCrea un archivo .env con tus credenciales o ejecuta 'aws configure'.")
        print("Consulta AWS_SETUP.md para instrucciones detalladas.")
        sys.exit(1)


def run_attendance_system():
    """Inicia el sistema de reconocimiento facial en tiempo real."""
    from rekognition.recognize import capture_and_recognize
    from rekognition.attendance import register_event

    def on_recognized(result):
        register_event(result["employee_id"], result["confidence"])

    print("\nIQSystems - Control de Asistencia")
    print("Presiona ESPACIO para escanear | Q para salir\n")
    capture_and_recognize(on_recognized_callback=on_recognized)


def run_setup():
    """Crea la colección y registra todos los empleados de data/employees/."""
    from rekognition.collection import create_collection, register_all_from_folder, list_employees

    print("Configurando colección en Amazon Rekognition...\n")
    create_collection()
    register_all_from_folder("data/employees")
    print()
    list_employees()


def main():
    parser = argparse.ArgumentParser(
        description="IQSystems - Control de Asistencia con Reconocimiento Facial"
    )
    parser.add_argument("--setup", action="store_true", help="Crear colección y registrar empleados")
    parser.add_argument("--list", action="store_true", help="Listar empleados registrados")
    parser.add_argument("--summary", action="store_true", help="Ver resumen de asistencia de hoy")
    parser.add_argument("--add", nargs=2, metavar=("EMPLOYEE_ID", "IMAGE_PATH"),
                        help="Registrar un empleado individual")

    args = parser.parse_args()
    check_aws_config()

    if args.setup:
        run_setup()

    elif args.list:
        from rekognition.collection import list_employees
        list_employees()

    elif args.summary:
        from rekognition.attendance import print_today_summary
        print_today_summary()

    elif args.add:
        from rekognition.collection import register_employee
        employee_id, image_path = args.add
        register_employee(employee_id, image_path)

    else:
        run_attendance_system()


if __name__ == "__main__":
    main()
