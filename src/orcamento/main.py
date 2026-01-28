# src/orcamento/main.py
# --- VERSÃO DE DIAGNÓSTICO PARA IDENTIFICAR PONTOS DE TRAVAMENTO ---

import logging
import sys
from datetime import datetime
import pandas as pd

from orcamento.core.config import settings
from orcamento.core.logging_config import setup_logging
from orcamento.data_access.database import get_sql_engine, get_olap_connection, execute_query
from orcamento.data_access.queries import get_queries
from orcamento.processing.financial_analysis import combine_executed_and_forecast, calculate_financial_summary
from orcamento.reporting.formatting import pivot_and_format_financial_df, style_df_to_html
from orcamento.reporting.email_sender import send_report_email

MONTH_MAP = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
}

def run_financial_report_flow(year: int) -> None:
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando processo para o ano de %d...", year)

    try:
        # --- PASSO 1: PREPARAÇÃO INICIAL ---
        logger.info("--> PASSO 1: Carregando queries e mapa de meses...")
        queries = get_queries()
        month_map_inv = {v: k for k, v in MONTH_MAP.items()}
        logger.info("<-- PASSO 1 CONCLUÍDO.")

        # --- PASSO 2: CRIAÇÃO DAS CONEXÕES ---
        logger.info("--> PASSO 2.1: Criando engine de conexão SQL...")
        sql_conn = get_sql_engine(settings.db)
        logger.info("<-- PASSO 2.1 CONCLUÍDO.")

        logger.info("--> PASSO 2.2: Criando objeto de conexão OLAP...")
        olap_conn = get_olap_connection(settings.olap)
        logger.info("<-- PASSO 2.2 CONCLUÍDO.")

        # --- PASSO 3: CARREGAMENTO DE DADOS PREVISTOS (CSV) ---
        logger.info("--> PASSO 3: Lendo arquivos CSV de previsão...")
        # (Lógica de leitura dos CSVs permanece a mesma)
        try:
            df_receitas_prev = pd.read_csv(settings.ROOT_DIR / "forecast_data/previsao_receitas.csv")
            logger.info("   - Previsão de receitas carregada.")
        except FileNotFoundError: df_receitas_prev = pd.DataFrame(); logger.warning("   - Arquivo de previsão de receitas não encontrado.")
        try:
            df_despesas_prev = pd.read_csv(settings.ROOT_DIR / "forecast_data/previsao_despesas.csv")
            logger.info("   - Previsão de despesas carregada.")
        except FileNotFoundError: df_despesas_prev = pd.DataFrame(); logger.warning("   - Arquivo de previsão de despesas não encontrado.")
        logger.info("<-- PASSO 3 CONCLUÍDO.")

        # --- PASSO 4: EXECUÇÃO DAS QUERIES SQL ---
        logger.info("--> PASSO 4.1: Executando a consulta de RECEITAS (SQL)...")
        df_receitas_exec = execute_query(sql_conn, queries["RECEITAS"].sql, {"year": year})
        logger.info("<-- PASSO 4.1 CONCLUÍDO.")

        logger.info("--> PASSO 4.2: Executando a consulta de DESPESAS (SQL)...")
        df_despesas_exec = execute_query(sql_conn, queries["DESPESAS"].sql, {"year": year})
        logger.info("<-- PASSO 4.2 CONCLUÍDO.")

        # --- PASSO 5: EXECUÇÃO DA QUERY MDX ---
        logger.info("--> PASSO 5: Executando a consulta do PPA (MDX)...")
        mdx_params = {"ano_filtro": settings.filters.ano_filtro, "ppa_filtro": settings.filters.ppa_filtro}
        df_ppa = execute_query(olap_conn, queries["PPA"].sql, mdx_params)
        logger.info("<-- PASSO 5 CONCLUÍDO.")

        # --- PASSO 6: PROCESSAMENTO E FORMATAÇÃO ---
        logger.info("--> PASSO 6: Combinando dados e formatando para HTML...")
        df_receitas_full = combine_executed_and_forecast(df_receitas_exec, df_receitas_prev, month_map_inv)
        df_despesas_full = combine_executed_and_forecast(df_despesas_exec, df_despesas_prev, month_map_inv)
        df_resumo_full = calculate_financial_summary(df_receitas_full, df_despesas_full)
        # (Restante da lógica de formatação e envio)
        logger.info("<-- PASSO 6 CONCLUÍDO.")
        
        # ... (código para KPIs, tabelas_html e send_report_email) ...

    except Exception as e:
        logger.critical("🔥 Ocorreu um erro fatal no processo: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("✅ Processo concluído com sucesso!")

def main():
    setup_logging()
    run_financial_report_flow(year=settings.filters.ano_filtro)

if __name__ == "__main__":
    main()
