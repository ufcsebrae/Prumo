import logging
import win32com.client as win32
from jinja2 import Environment, FileSystemLoader
from orcamento.core.config import AppSettings

logger = logging.getLogger(__name__)

def send_report_email(
    settings: AppSettings,
    subject: str,
    template_context: dict[str, str],
) -> None:
    """Renderiza o template HTML e envia o relatório por e-mail via Outlook."""
    logger.info("Renderizando template de e-mail...")
    try:
        env = Environment(
            loader=FileSystemLoader(settings.TEMPLATES_DIR), autoescape=True
        )
        template = env.get_template("email_template.html")
        html_body = template.render(template_context)
    except Exception as e:
        logger.error(f"Erro ao renderizar template de e-mail: {e}")
        raise

    logger.info(f"Enviando e-mail para: {settings.email.recipient}")
    try:
        outlook = win32.Dispatch("Outlook.Application")
        message = outlook.CreateItem(0)
        message.To = settings.email.recipient
        message.Subject = subject
        message.HTMLBody = html_body
        message.Send()
        logger.info("E-mail enviado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail via Outlook: {e}")
        raise
