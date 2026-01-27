from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Query:
    """Representa uma consulta SQL com um título e o corpo do script."""
    def __init__(self, titulo: str, sql: str):
        self.titulo = titulo
        self.sql = sql

def _load_query_from_file(filepath: Path) -> str:
    """Carrega uma string de consulta de um arquivo .sql."""
    try:
        sql_content = filepath.read_text(encoding='utf-8')
        logger.info(f"Query carregada com sucesso do arquivo: {filepath.name}")
        return sql_content
    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: Arquivo de query não encontrado: {filepath}")
        raise

def get_queries() -> dict[str, Query]:
    """
    Carrega dinamicamente todas as consultas dos arquivos .sql
    e as retorna em um dicionário.
    """
    sql_dir = Path(__file__).parent / "sql"
    
    queries = {
        "RECEITAS": Query(
            titulo="Receitas",
            sql=_load_query_from_file(sql_dir / "receitas.sql")
        ),
        "DESPESAS": Query(
            titulo="Despesas",
            sql=_load_query_from_file(sql_dir / "despesas.sql")
        ),
    }
    return queries
