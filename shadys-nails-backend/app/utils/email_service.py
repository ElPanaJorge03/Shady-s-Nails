import os
import re
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import requests

# Configuración desde variables de entorno
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Shady's Nails 💅")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

# Pool de hilos para enviar correos sin bloquear al servidor
executor = ThreadPoolExecutor(max_workers=3)

# Regex simple para validar emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """Valida formato de email usando regex simple"""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))

def _actually_send_email_async(subject: str, recipient: str, body_html: str, cc: Optional[str] = None, bcc: Optional[str] = None):
    """Función interna que realiza el envío real usando Resend API"""
    try:
        url = "https://api.resend.com/emails"
        
        payload = {
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to": [recipient],
            "subject": subject,
            "html": body_html
        }
        
        # Agregar CC y BCC si existen
        if cc:
            payload["cc"] = [cc]
        if bcc:
            payload["bcc"] = [bcc]
        
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Email enviado con éxito a {recipient}")
        else:
            print(f"❌ Error Resend ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error enviando email: {e}")

def send_email(
    subject: str, 
    recipient: str, 
    body_html: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> bool:
    """
    Envía un correo electrónico de forma asíncrona usando Resend.
    """
    if not EMAIL_ENABLED or not RESEND_API_KEY or not SENDER_EMAIL:
        print(f"📧 [SIMULACIÓN] Email para: {recipient} | Asunto: {subject}")
        return True

    if not validate_email(recipient):
        return False

    # Enviar al pool de hilos y retornar éxito de encolado inmediatamente
    executor.submit(_actually_send_email_async, subject, recipient, body_html, cc, bcc)
    return True

def get_confirmation_template(customer_name: str, service_name: str, date: str, time: str):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ffccf2; border-radius: 10px;">
            <h2 style="color: #d63384;">💅 ¡Cita Confirmada!</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Tu cita en <strong>Shady's Nails</strong> ha sido agendada con éxito.</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p><strong>Detalles de tu cita:</strong></p>
            <ul>
                <li><strong>Servicio:</strong> {service_name}</li>
                <li><strong>Fecha:</strong> {date}</li>
                <li><strong>Hora:</strong> {time}</li>
            </ul>
            <p>Te esperamos para consentirte como te mereces.</p>
            <p style="font-size: 0.9em; color: #666;">Si necesitas cancelar o reprogramar, por favor inicia sesión en nuestra app.</p>
            <br>
            <p>Atentamente,<br><strong>Shady's Nails</strong></p>
        </div>
    </body>
    </html>
    """

def get_update_template(
    customer_name: str, 
    service_name: str, 
    date: str, 
    time: str,
    changes: str = "Se han actualizado los detalles de tu cita"
) -> str:
    """
    Template para notificación de actualización de cita.
    
    Args:
        customer_name: Nombre del cliente
        service_name: Nombre del servicio
        date: Fecha de la cita
        time: Hora de la cita
        changes: Descripción de los cambios realizados
    """
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #d1ecf1; border-radius: 10px;">
            <h2 style="color: #0c5460;">📝 Cita Actualizada</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Te informamos que tu cita en <strong>Shady's Nails</strong> ha sido actualizada.</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p><strong>Nuevos detalles de tu cita:</strong></p>
            <ul>
                <li><strong>Servicio:</strong> {service_name}</li>
                <li><strong>Fecha:</strong> {date}</li>
                <li><strong>Hora:</strong> {time}</li>
            </ul>
            <p style="background-color: #d1ecf1; padding: 10px; border-radius: 5px; font-size: 0.9em;">
                ℹ️ {changes}
            </p>
            <p>Si tienes alguna duda, no dudes en contactarnos.</p>
            <br>
            <p>Atentamente,<br><strong>Shady's Nails</strong></p>
        </div>
    </body>
    </html>
    """



def get_cancellation_template(customer_name: str, service_name: str, date: str, time: str):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #f8d7da; border-radius: 10px;">
            <h2 style="color: #721c24;">🚫 Cita Cancelada</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Te informamos que tu cita para <strong>{service_name}</strong> el día <strong>{date}</strong> a las <strong>{time}</strong> ha sido cancelada.</p>
            <p>Si esto fue un error o deseas agendar una nueva cita, puedes hacerlo directamente en nuestra aplicación.</p>
            <br>
            <p>Atentamente,<br><strong>Shady's Nails</strong></p>
        </div>
    </body>
    </html>
    """

def get_request_received_template(customer_name: str, service_name: str, date: str, time: str):
    """Template para el cliente cuando solicita una cita (estado pendiente)"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #fff3cd; border-radius: 10px;">
            <h2 style="color: #856404;">⏳ Solicitud Recibida</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Hemos recibido tu solicitud de cita en <strong>Shady's Nails</strong>.</p>
            <p>Tu cita está <strong>pendiente de aprobación</strong>. Te notificaremos por correo tan pronto como sea confirmada por nuestro equipo.</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p><strong>Detalles solicitados:</strong></p>
            <ul>
                <li><strong>Servicio:</strong> {service_name}</li>
                <li><strong>Fecha:</strong> {date}</li>
                <li><strong>Hora:</strong> {time}</li>
            </ul>
            <br>
            <p>Atentamente,<br><strong>Shady's Nails</strong></p>
        </div>
    </body>
    </html>
    """

def get_new_appointment_request_admin_template(worker_name: str, customer_name: str, service_name: str, date: str, time: str):
    """Template para el worker cuando recibe una nueva solicitud"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #d1ecf1; border-radius: 10px;">
            <h2 style="color: #0c5460;">💅 Nueva Solicitud de Cita</h2>
            <p>Hola <strong>{worker_name}</strong>,</p>
            <p>Tienes una nueva solicitud de cita de <strong>{customer_name}</strong>.</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <ul>
                <li><strong>Cliente:</strong> {customer_name}</li>
                <li><strong>Servicio:</strong> {service_name}</li>
                <li><strong>Fecha:</strong> {date}</li>
                <li><strong>Hora:</strong> {time}</li>
            </ul>
            <p>Por favor ingresa a tu Dashboard para <strong>Aprobar</strong> o <strong>Rechazar</strong> esta solicitud.</p>
        </div>
    </body>
    </html>
    """

def get_completion_template(customer_name: str, service_name: str):
    """Template para el cliente cuando la cita se completa"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #d4edda; border-radius: 10px;">
            <h2 style="color: #155724;">✨ ¡Gracias por tu visita!</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Esperamos que hayas disfrutado tu servicio de <strong>{service_name}</strong>.</p>
            <p>Tu cita ha sido marcada como <strong>completada</strong>.</p>
            <p>Nos encantaría verte de nuevo pronto para seguir cuidando de ti.</p>
            <br>
            <p>¡Hasta la próxima!</p>
            <p>Atentamente,<br><strong>Shady's Nails Team</strong></p>
        </div>
    </body>
    </html>
    """

def get_reset_password_template(customer_name: str, code: str):
    """Template para recuperación de contraseña"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #d1ecf1; border-radius: 10px; text-align: center;">
            <h2 style="color: #6f42c1;">🔐 Recuperación de Contraseña</h2>
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Has solicitado restablecer tu contraseña en <strong>Shady's Nails</strong>.</p>
            <p>Usa el siguiente código para completar el proceso:</p>
            <div style="background-color: #f8f9fa; padding: 20px; font-size: 2rem; font-weight: bold; letter-spacing: 5px; color: #6f42c1; border-radius: 8px; margin: 20px 0;">
                {code}
            </div>
            <p>Este código expirará en <strong>15 minutos</strong>.</p>
            <p style="font-size: 0.8em; color: #888;">Si no solicitaste este cambio, puedes ignorar este correo.</p>
            <br>
            <p>Atentamente,<br><strong>Shady's Nails Team</strong></p>
        </div>
    </body>
    </html>
    """
