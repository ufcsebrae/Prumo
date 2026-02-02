# src/orcamento/data_access/database.py
# --- VERSÃO FINAL COM ORDENAÇÃO DE PARÂMETROS GARANTIDA ---

import logging
import pandas as pd
from sqlalchemy import create_engine, Engine
import re  # Importa a biblioteca de Expressões Regulares

from orcamento.core.config import DatabaseSettings

logger = logging.getLogger(__name__)

def get_sql_engine(config: DatabaseSettings) -> Engine:
    """Cria e retorna uma engine de conexão para SQL Server."""
    conn_url = f"mssql+pyodbc://@{config.servername}/{config.dbname}?trusted_connection=yes&driver={config.driver.replace(' ', '+')}&TrustServerCertificate=yes"
    engine = create_engine(conn_url)
    with engine.connect() as connection:
        logger.info(f"Conexão SQL com '{config.servername}' estabelecida.")
    return engine

def execute_query(engine: Engine, query_script: str, params: dict = None) -> pd.DataFrame:
    """Executa uma consulta SQL, garantindo a ordem correta dos parâmetros."""
    logger.info("Executando consulta SQL...")
    
    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        
        # --- LÓGICA DE PARÂMETROS CORRIGIDA E FINAL ---
        if params:
            # 1. Encontra todos os placeholders (ex: ':ppa_filtro', ':ano_filtro') 
            #    na ordem exata em que aparecem na query.
            param_keys_in_order = re.findall(r":(\w+)", query_script)
            
            # 2. Cria a tupla de valores usando a ordem correta das chaves encontradas.
            params_tuple = tuple(params[key] for key in param_keys_in_order)
            
            # 3. Substitui todos os placeholders :key por '?' para o pyodbc.
            query_for_exec = re.sub(r":\w+", "?", query_script)
            
            logger.info(f"SQL Final Enviado: {query_for_exec} | Parâmetros: {params_tuple}")
            cursor.execute(query_for_exec, params_tuple)
        else:
            cursor.execute(query_script)
        # -----------------------------------------------
        
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
        
        cursor.close()
        logger.info(f"Consulta SQL retornou {len(df)} linhas.")
        return df
    finally:
        raw_conn.close() # Garante que a conexão seja fechada
