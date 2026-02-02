# src/orcamento/core/config.py
# --- ATUALIZADO COM O FILTRO DE MÊS ---

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    servername: str = Field(..., alias='DB_SERVERNAME')
    dbname: str = Field(..., alias='DB_DBNAME')
    driver: str = Field(..., alias='DB_DRIVER')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

class EmailSettings(BaseSettings):
    recipient: str = Field(..., alias='MAIL_RECIPIENT')
    subject_prefix: str = Field(..., alias='MAIL_SUBJECT_PREFIX')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- CLASSE DE FILTRO ATUALIZADA ---
class FilterSettings(BaseSettings):
    ppa_filtro: str = Field(..., alias='PPA_FILTRO')
    ano_filtro: int = Field(..., alias='ANO_FILTRO')
    mes_filtro: int = Field(12, alias='MES_FILTRO') # <-- NOVA OPÇÃO. Padrão 12 (dezembro)
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
# ------------------------------------

class ColorSettings(BaseSettings):
    positive: str = '#107C10'
    negative: str = '#D83B01'
    forecast_manual: str = '#D83B01'
    forecast_system: str = '#605E5C'

class AppSettings(BaseSettings):
    """Agregador de todas as configurações da aplicação."""
    db: DatabaseSettings = DatabaseSettings()
    email: EmailSettings = EmailSettings()
    filters: FilterSettings = FilterSettings()
    colors: ColorSettings = ColorSettings()
    
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    TEMPLATES_DIR: Path = ROOT_DIR / "src/orcamento/reporting/templates"

settings = AppSettings()
