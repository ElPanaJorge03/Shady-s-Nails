import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

# Configuración desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
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
    """Función interna que realiza el envío real con soporte para SSL"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        if cc: msg['Cc'] = cc
        if bcc: msg['Bcc'] = bcc

        msg.attach(MIMEText(body_html, 'html'))

        # Intentar conectar según el puerto
        if SMTP_PORT == 465:
            # Puerto 465 usa SSL directo
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15)
        else:
            # Otros puertos (como 587) usan STARTTLS
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
            server.starttls()
            
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        recipients = [recipient]
        if cc: recipients.append(cc)
        if bcc: recipients.append(bcc)
        
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        server.quit()
        print(f"✅ Email enviado con éxito a {recipient}")
    except Exception as e:
        print(f"❌ Error de red SMTP (Puerto {SMTP_PORT}): {e}")

def send_email(
    subject: str, 
    recipient: str, 
    body_html: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> bool:
    """
    Envía un correo electrónico de forma asíncrona (no bloqueante).
    """
    if not EMAIL_ENABLED or not SMTP_USER or not SMTP_PASSWORD:
        print(f"📧 [SIMULACIÓN] Email para: {recipient} | Asunto: {subject}")
        return True

    if not validate_email(recipient):
        return False

    # Enviar al pool de hilos y retornar éxito de encolado inmediatamente
    executor.submit(_actually_send_email, subject, recipient, body_html, cc, bcc)
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
