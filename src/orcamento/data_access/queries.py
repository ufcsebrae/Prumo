# src/orcamento/data_access/queries.py
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Query:
    """Representa uma consulta com tipo (sql/mdx), título e script."""
    def __init__(self, titulo: str, sql: str, query_type: str):
        self.titulo = titulo
        self.sql = sql
        self.query_type = query_type

def _load_query(filepath: Path) -> str:
    # ... (função _load_query_from_file, renomeada para _load_query)
    try:
        content = filepath.read_text(encoding='utf-8')
        logger.info(f"Query carregada de: {filepath.name}")
        return content
    except FileNotFoundError:
        logger.error(f"Arquivo de query não encontrado: {filepath}")
        raise

def get_queries() -> dict[str, Query]:
    """Carrega todas as consultas (SQL e MDX) dos arquivos."""
    sql_dir = Path(__file__).parent / "sql"
    mdx_dir = Path(__file__).parent / "mdx"
    
    return {
        "RECEITAS": Query(titulo="Receitas", sql=_load_query(sql_dir / "receitas.sql"), query_type="sql"),
        "DESPESAS": Query(titulo="Despesas", sql=_load_query(sql_dir / "despesas.sql"), query_type="sql"),
        "PPA": Query(titulo="Planejamento PPA", sql=_load_query(mdx_dir / "planejamento_ppa.mdx"), query_type="mdx"),
    }
