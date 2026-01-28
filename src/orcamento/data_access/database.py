# src/orcamento/data_access/database.py
# --- VERSÃO FINAL COM A CORREÇÃO DA CONEXÃO OLAP ---

import logging
from typing import Union
import pandas as pd
from sqlalchemy import create_engine, Engine, text
import sys
import clr
from pathlib import Path

from orcamento.core.config import OLAPSettings, DatabaseSettings
settings_olap = OLAPSettings()
try:
    dll_path_str = settings_olap.adomd_dll_path
    dll_path = Path(dll_path_str)
    dll_dir = str(dll_path.parent)
    if dll_dir not in sys.path:
        sys.path.append(dll_dir)
        logging.info(f"Adicionado diretório da DLL ADOMD ao sys.path: {dll_dir}")
    clr.AddReference("Microsoft.AnalysisServices.AdomdClient")
    logging.info("Referência ao assembly 'Microsoft.AnalysisServices.AdomdClient' adicionada com sucesso.")
except Exception as e:
    logging.critical(f"Falha ao carregar DLL AdomdClient: {e}", exc_info=True)
    sys.exit(1)
from pyadomd import Pyadomd

logger = logging.getLogger(__name__)
Conexao = Union[Engine, Pyadomd]

def get_sql_engine(config: DatabaseSettings) -> Engine:
    conn_url = f"mssql+pyodbc://@{config.servername}/{config.dbname}?trusted_connection=yes&driver={config.driver.replace(' ', '+')}&TrustServerCertificate=yes"
    engine = create_engine(conn_url)
    with engine.connect() as connection:
        logger.info(f"Conexão SQL com '{config.servername}' estabelecida.")
    return engine

def get_olap_connection(config: OLAPSettings) -> Pyadomd:
    """Cria e abre uma conexão para o cubo OLAP usando a string de conexão correta."""
    # --- CORREÇÃO APLICADA AQUI ---
    # Substituído 'Trusted_Connection=yes' por 'Integrated Security=SSPI', que é o correto para ADOMD.
    conn_str = (
        f"Provider={config.provider};Data Source={config.source};"
        f"Initial Catalog={config.catalog};Integrated Security=SSPI;"
    )
    try:
        # A conexão será aberta dentro da função execute_query
        conn = Pyadomd(conn_str)
        logger.info(f"Objeto de conexão OLAP com '{config.source}' criado com sucesso.")
        return conn
    except Exception as e:
        logger.critical(f"Falha ao criar objeto de conexão OLAP: {e}")
        raise

def execute_query(conexao: Conexao, query_script: str, params: dict = None) -> pd.DataFrame:
    """Executa uma consulta, usando o método correto para cada tipo de conexão."""
    logger.info("Executando consulta...")
    
    if isinstance(conexao, Engine):
        # Lógica SQL (permanece a mesma)
        logger.info("Executando via Raw Connection (SQL - Método Anti-Fantasma)...")
        raw_conn = conexao.raw_connection()
        try:
            cursor = raw_conn.cursor()
            params_tuple = None
            if params:
                for key in params.keys():
                    query_script = query_script.replace(f":{key}", "?")
                params_tuple = tuple(params.values())

            logger.info(f"SQL Final Enviado: {query_script} | Parâmetros: {params_tuple}")
            cursor.execute(query_script, params_tuple or ())
            
            columns = [column[0] for column in cursor.description]
            df = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
            
            cursor.close()
            logger.info(f"Consulta SQL retornou {len(df)} linhas.")
            return df
        finally:
            raw_conn.close()
            
    elif isinstance(conexao, Pyadomd):
        logger.info("Executando via Pyadomd (MDX)...")
        if params:
            for key, value in params.items():
                query_script = query_script.replace(f"{{{key}}}", str(value))
        
        cursor = None
        try:
            conexao.open()
            cursor = conexao.cursor()
            cursor.execute(query_script)
            columns = [col.name for col in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            logger.info(f"Consulta MDX retornou {len(df)} linhas.")
            return df
        finally:
            # --- CORREÇÃO APLICADA AQUI ---
            # Remove a verificação 'is_connected' que não existe no Pyadomd.
            # O bloco try/finally já garante o fechamento correto.
            if cursor: cursor.close()
            # A biblioteca Pyadomd gerencia o fechamento da conexão principal no seu próprio 'finally'.
            logger.info("Recursos Pyadomd (cursor) liberados.")
    else:
        raise TypeError(f"Tipo de conexão não suportado: {type(conexao)}")
