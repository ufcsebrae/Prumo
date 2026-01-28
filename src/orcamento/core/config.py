# src/orcamento/core/config.py

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    servername: str = Field(..., alias='DB_SERVERNAME')
    dbname: str = Field(..., alias='DB_DBNAME')
    driver: str = Field(..., alias='DB_DRIVER')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- NOVA CLASSE PARA CONFIGURAÇÕES OLAP ---
class OLAPSettings(BaseSettings):
    source: str = Field(..., alias='OLAP_SOURCE')
    catalog: str = Field(..., alias='OLAP_CATALOG')
    provider: str = Field(..., alias='OLAP_PROVIDER')
    adomd_dll_path: str = Field(..., alias='ADOMD_DLL_PATH')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- NOVA CLASSE PARA FILTROS DE NEGÓCIO ---
class FilterSettings(BaseSettings):
    ppa_filtro: str = Field(..., alias='PPA_FILTRO')
    ano_filtro: int = Field(..., alias='ANO_FILTRO')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

class ColorSettings(BaseSettings):
    positive: str = '#107C10'; negative: str = '#D83B01'; forecast: str = '#605E5C'
    model_config = SettingsConfigDict(env_prefix='COLOR_', env_file='.env', extra='ignore')

class AppSettings(BaseSettings):
    """Agregador de todas as configurações da aplicação."""
    db: DatabaseSettings = DatabaseSettings()
    olap: OLAPSettings = OLAPSettings()
    filters: FilterSettings = FilterSettings()
    colors: ColorSettings = ColorSettings()
    
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    TEMPLATES_DIR: Path = ROOT_DIR / "src/orcamento/reporting/templates"

settings = AppSettings()
