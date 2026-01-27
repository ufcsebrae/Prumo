# src/orcamento/data_access/database.py
# --- VERSÃO FINAL COM A SINTAXE CORRETA DO try...finally ---

import logging
from typing import Any
import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from orcamento.core.config import DatabaseSettings

logger = logging.getLogger(__name__)

def get_engine(db_settings: DatabaseSettings) -> Engine:
    """Cria e retorna uma engine de conexão do SQLAlchemy."""
    try:
        conn_url = (
            f"mssql+pyodbc://@{db_settings.servername}/{db_settings.dbname}?"
            f"trusted_connection=yes&driver={db_settings.driver.replace(' ', '+')}"
            f"&TrustServerCertificate=yes"
        )
        engine = create_engine(conn_url, echo=False)
        with engine.connect() as connection:
            logger.info(f"Conexão com '{db_settings.servername}' estabelecida com sucesso.")
        return engine
    except Exception as e:
        logger.critical(f"Falha ao criar a engine de conexão: {e}")
        raise

def execute_query(
    engine: Engine,
    sql_query: str,
    params: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Executa uma consulta parametrizada usando o método mais direto e com
    o tratamento de recursos (conexão) corrigido.
    """
    logger.info("Executando consulta no banco de dados (MÉTODO DIRETO E FINAL)...")
    
    # Pega a conexão "bruta" - NÃO PODE SER USADA COM 'with'
    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()

        params_tuple = None
        if params:
            for key in params.keys():
                sql_query = sql_query.replace(f":{key}", "?")
            params_tuple = tuple(params.values())

        # ================== PROVA FINAL (ainda aqui para garantir) ==================
        print("\n" + "="*80)
        print("=== CONSULTA FINAL ENVIADA AO CURSOR ===")
        print(f"SQL: {sql_query}")
        print(f"PARÂMETROS: {params_tuple}")
        print("="*80 + "\n")
        # =========================================================================

        cursor.execute(sql_query, params_tuple or ())
        
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
        
        cursor.close()

        logger.info(f"Consulta retornou {len(df)} linhas.")
        return df
            
    except Exception as e:
        logger.error(f"Erro do PyODBC ao executar consulta: {e}", exc_info=True)
        raise
    finally:
        # O bloco 'finally' garante que a conexão será fechada SEMPRE,
        # mesmo que ocorra um erro no bloco 'try'.
        logger.info("Fechando a conexão 'bruta'...")
        raw_conn.close()
