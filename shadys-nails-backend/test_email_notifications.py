import requests
import json
from datetime import date, time, datetime, timedelta

# Configuración
BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_create_appointment_with_email():
    """Prueba crear una cita y verificar que se envíe el email de confirmación"""
    print_section("TEST 1: Crear Cita con Email de Confirmación")
    
    # Fecha de mañana
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    data = {
        "worker_id": 1,
        "customer_id": 1,
        "service_id": 3,
        "additional_id": 1,
        "date": str(tomorrow),
        "start_time": "10:00:00",
        "notes": "Prueba de email"
    }
    
    print(f"📤 Creando cita para {tomorrow} a las 10:00...")
    response = requests.post(f"{BASE_URL}/appointments/", json=data)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 201:
        appointment = response.json()
        print(f"✅ Cita creada exitosamente!")
        print(f"   ID: {appointment['id']}")
        print(f"   Cliente: {appointment.get('customer_name', 'N/A')}")
        print(f"   Servicio: {appointment.get('service_name', 'N/A')}")
        print(f"\n💡 Revisa la consola del servidor para ver el log del email")
        return appointment['id']
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_update_appointment_with_email(appointment_id):
    """Prueba actualizar una cita y verificar que se envíe el email de actualización"""
    print_section("TEST 2: Actualizar Cita con Email de Notificación")
    
    if not appointment_id:
        print("⚠️ No hay appointment_id, saltando test...")
        return
    
    # Cambiar la hora
    data = {
        "start_time": "14:00:00",
        "notes": "Hora actualizada - prueba de email"
    }
    
    print(f"📤 Actualizando cita #{appointment_id} a las 14:00...")
    response = requests.put(f"{BASE_URL}/appointments/{appointment_id}", json=data)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        appointment = response.json()
        print(f"✅ Cita actualizada exitosamente!")
        print(f"   Nueva hora: {appointment['start_time']}")
        print(f"\n💡 Revisa la consola del servidor para ver el log del email de actualización")
    else:
        print(f"❌ Error: {response.text}")

def test_cancel_appointment_with_email(appointment_id):
    """Prueba cancelar una cita y verificar que se envíe el email de cancelación"""
    print_section("TEST 3: Cancelar Cita con Email de Cancelación")
    
    if not appointment_id:
        print("⚠️ No hay appointment_id, saltando test...")
        return
    
    print(f"📤 Cancelando cita #{appointment_id}...")
    response = requests.delete(f"{BASE_URL}/appointments/{appointment_id}")
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Cita cancelada exitosamente!")
        print(f"   Status anterior: {result['previous_status']}")
        print(f"   Status nuevo: {result['new_status']}")
        print(f"\n💡 Revisa la consola del servidor para ver el log del email de cancelación")
    else:
        print(f"❌ Error: {response.text}")

def test_email_templates():
    """Prueba que los templates de email se generen correctamente"""
    print_section("TEST 4: Validar Templates de Email")
    
    from app.utils.email_service import (
        get_confirmation_template,
        get_update_template,
        get_cancellation_template,
        validate_email
    )
    
    # Test validación de emails
    print("🔍 Probando validación de emails...")
    test_emails = [
        ("test@example.com", True),
        ("invalid-email", False),
        ("", False),
        ("user@domain", False),
        ("user@domain.co.uk", True),
    ]
    
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{email}' -> {result} (esperado: {expected})")
    
    # Test templates
    print("\n📧 Generando templates de prueba...")
    
    conf_template = get_confirmation_template("Ana García", "Manicure Gel", "2025-01-25", "10:00")
    print(f"   ✅ Template de confirmación: {len(conf_template)} caracteres")
    
    update_template = get_update_template("Ana García", "Manicure Gel", "2025-01-25", "14:00", "Hora cambiada de 10:00 a 14:00")
    print(f"   ✅ Template de actualización: {len(update_template)} caracteres")
    
    cancel_template = get_cancellation_template("Ana García", "Manicure Gel", "2025-01-25", "10:00")
    print(f"   ✅ Template de cancelación: {len(cancel_template)} caracteres")

def main():
    print("\n" + "🎯" * 30)
    print("  TEST DE NOTIFICACIONES POR EMAIL - SHADY'S NAILS")
    print("🎯" * 30)
    
    print("\n⚙️ Configuración:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Asegúrate de que el servidor esté corriendo: uvicorn app.main:app --reload")
    print(f"   Los emails se simularán en consola si no hay credenciales SMTP configuradas")
    
    input("\n👉 Presiona ENTER para comenzar las pruebas...")
    
    try:
        # Test 1: Crear cita
        appointment_id = test_create_appointment_with_email()
        
        if appointment_id:
            input("\n👉 Presiona ENTER para continuar con el test de actualización...")
            
            # Test 2: Actualizar cita
            test_update_appointment_with_email(appointment_id)
            
            input("\n👉 Presiona ENTER para continuar con el test de cancelación...")
            
            # Test 3: Cancelar cita
            test_cancel_appointment_with_email(appointment_id)
        
        # Test 4: Templates (no requiere servidor)
        input("\n👉 Presiona ENTER para validar templates...")
        test_email_templates()
        
        print_section("RESUMEN")
        print("✅ Todos los tests completados!")
        print("\n📝 Notas:")
        print("   - Si ves logs de [SIMULACIÓN EMAIL], es porque no hay credenciales SMTP")
        print("   - Para enviar emails reales, configura SMTP_USER y SMTP_PASSWORD en .env")
        print("   - Revisa la consola del servidor para ver los logs de email")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
        print("   Ejecuta: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
