# src/orcamento/data_access/queries.py
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Query:
    def __init__(self, titulo: str, sql: str, query_type: str):
        self.titulo = titulo; self.sql = sql; self.query_type = query_type

def _load_query(filepath: Path) -> str:
    try:
        content = filepath.read_text(encoding='utf-8')
        logger.info(f"Query carregada de: {filepath.name}")
        return content
    except FileNotFoundError:
        logger.error(f"Arquivo de query não encontrado: {filepath}")
        raise

def get_queries() -> dict[str, Query]:
    """Carrega todas as consultas SQL dos arquivos."""
    sql_dir = Path(__file__).parent / "sql"
    
    return {
        "RECEITAS": Query(titulo="Receitas Executadas", sql=_load_query(sql_dir / "receitas.sql"), query_type="sql"),
        "DESPESAS": Query(titulo="Despesas Executadas", sql=_load_query(sql_dir / "despesas.sql"), query_type="sql"),
        "PLANEJADO_DESPESAS": Query(titulo="Planejamento PPA Despesas", sql=_load_query(sql_dir / "planejamento_despesas.sql"), query_type="sql"),
        "PLANEJADO_RECEITAS": Query(titulo="Planejamento PPA Receitas", sql=_load_query(sql_dir / "planejamento_receitas.sql"), query_type="sql"),
    }
