# src/orcamento/core/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    servername: str; dbname: str; driver: str
    model_config = SettingsConfigDict(env_prefix='DB_', env_file='.env', extra='ignore')

class EmailSettings(BaseSettings):
    recipient: str; subject_prefix: str
    model_config = SettingsConfigDict(env_prefix='MAIL_', env_file='.env', extra='ignore')

# --- NOVA CLASSE PARA CORES ---
class ColorSettings(BaseSettings):
    """Define as cores semânticas para os relatórios."""
    positive: str = '#107C10'  # Verde escuro acessível
    negative: str = '#D83B01'  # Vermelho/Laranja escuro acessível
    model_config = SettingsConfigDict(env_prefix='COLOR_', env_file='.env', extra='ignore')

class AppSettings(BaseSettings):
    """Agregador de todas as configurações da aplicação."""
    db: DatabaseSettings = DatabaseSettings()
    email: EmailSettings = EmailSettings()
    colors: ColorSettings = ColorSettings() # Adiciona as cores às configurações
    
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    TEMPLATES_DIR: Path = ROOT_DIR / "src/orcamento/reporting/templates"

settings = AppSettings()
