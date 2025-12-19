import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr

# Configuración básica (se recomienda mover a variables de entorno)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = "Shady's Nails 💅"

def send_email(subject: str, recipient: str, body_html: str):
    """
    Envía un correo electrónico en formato HTML.
    Si no hay credenciales configuradas, solo imprime el log por seguridad/demo.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"📧 [SIMULACIÓN EMAIL] Para: {recipient} | Asunto: {subject}")
        print(f"📝 Contenido omitido en log (formato HTML)")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email enviado exitosamente a {recipient}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
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
