from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    """Configurações de conexão com o banco de dados."""
    servername: str
    dbname: str
    driver: str
    model_config = SettingsConfigDict(env_prefix='DB_', env_file='.env', extra='ignore')

class EmailSettings(BaseSettings):
    """Configurações para envio de e-mail."""
    recipient: str
    subject_prefix: str
    model_config = SettingsConfigDict(env_prefix='MAIL_', env_file='.env', extra='ignore')

class AppSettings(BaseSettings):
    """Agregador de todas as configurações da aplicação."""
    db: DatabaseSettings = DatabaseSettings()
    email: EmailSettings = EmailSettings()
    
    # Define caminhos base para serem usados na aplicação
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    TEMPLATES_DIR: Path = ROOT_DIR / "src/orcamento/reporting/templates"

# Instância única para ser importada e usada em outros módulos
settings = AppSettings()
