import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Configuración desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Shady's Nails 💅")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

# Regex simple para validar emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """Valida formato de email usando regex simple"""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


def send_email(
    subject: str, 
    recipient: str, 
    body_html: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> bool:
    """
    Envía un correo electrónico en formato HTML.
    
    Args:
        subject: Asunto del correo
        recipient: Email del destinatario principal
        body_html: Contenido HTML del correo
        cc: Email para copia (opcional)
        bcc: Email para copia oculta (opcional)
    
    Returns:
        True si el email se envió exitosamente, False en caso contrario
    """
    # Validar email del destinatario
    if not validate_email(recipient):
        print(f"⚠️ Email inválido: {recipient}")
        return False
    
    # Si EMAIL_ENABLED está en False, modo simulación
    if not EMAIL_ENABLED:
        print(f"📧 [EMAIL DESHABILITADO] Para: {recipient} | Asunto: {subject}")
        return True
    
    # Si no hay credenciales, modo simulación
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"📧 [SIMULACIÓN EMAIL] Para: {recipient} | Asunto: {subject}")
        print(f"📝 Contenido omitido en log (formato HTML)")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc

        msg.attach(MIMEText(body_html, 'html'))

        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Enviar a todos los destinatarios
        recipients = [recipient]
        if cc:
            recipients.append(cc)
        if bcc:
            recipients.append(bcc)
        
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        server.quit()
        
        print(f"✅ Email enviado exitosamente a {recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"❌ Error de autenticación SMTP. Verifica SMTP_USER y SMTP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado enviando email: {str(e)}")
        return False

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
