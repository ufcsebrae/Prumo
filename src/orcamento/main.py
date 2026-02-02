# src/orcamento/main.py
# --- VERSÃO FINAL COM CORREÇÃO NO BLOCO DE VISUALIZAÇÃO ---

import logging
import sys
from datetime import datetime
import pandas as pd
import numpy as np

from orcamento.core.config import settings
from orcamento.core.logging_config import setup_logging
from orcamento.data_access.database import get_sql_engine, execute_query
from orcamento.data_access.queries import get_queries
from orcamento.processing.financial_analysis import process_planning_data, combinar_fontes_financeiras, calculate_financial_summary
from orcamento.reporting.formatting import pivot_and_format_financial_df, style_df_to_html
from orcamento.reporting.email_sender import send_report_email

MONTH_MAP = {
    1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
    7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
}

def run_financial_report_flow(year: int, month_end: int) -> None:
    """Orquestra o fluxo completo de geração do relatório."""
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Iniciando processo para o ano de {year}, com dados até o mês {month_end}...")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.expand_frame_repr', False)

    try:
        queries = get_queries()
        sql_conn = get_sql_engine(settings.db)
        month_map_inv = {v.lower(): k for k, v in MONTH_MAP.items()}
        ppa_params = {"ano_filtro": year, "ppa_filtro": settings.filters.ppa_filtro}
        
        df_de_para = pd.read_csv(settings.ROOT_DIR / "forecast_data/de_para_planejamento.csv")
        try:
            df_receitas_manual = pd.read_csv(settings.ROOT_DIR / "forecast_data/previsao_receitas.csv")
        except FileNotFoundError: df_receitas_manual = pd.DataFrame()
        try:
            df_despesas_manual = pd.read_csv(settings.ROOT_DIR / "forecast_data/previsao_despesas.csv")
        except FileNotFoundError: df_despesas_manual = pd.DataFrame()

        df_receitas_exec = execute_query(sql_conn, queries["RECEITAS"].sql, {"year": year})
        df_despesas_exec = execute_query(sql_conn, queries["DESPESAS"].sql, {"year": year})
        df_planejado_despesas_raw = execute_query(sql_conn, queries["PLANEJADO_DESPESAS"].sql, ppa_params)
        df_planejado_receitas_raw = execute_query(sql_conn, queries["PLANEJADO_RECEITAS"].sql, ppa_params)

        df_planejado_unificado = pd.concat([df_planejado_despesas_raw, df_planejado_receitas_raw], ignore_index=True)
        df_planejado_sistema = process_planning_data(df_planejado_unificado, df_de_para, month_map_inv)
        
        df_receitas_sistema = df_planejado_sistema[df_planejado_sistema['Tipo_Fluxo'].str.lower() == 'receita'].copy()
        df_despesas_sistema = df_planejado_sistema[df_planejado_sistema['Tipo_Fluxo'].str.lower() == 'despesa'].copy()

        df_receitas_full = combinar_fontes_financeiras(df_receitas_sistema, df_receitas_exec, df_receitas_manual, month_map_inv)
        df_despesas_full = combinar_fontes_financeiras(df_despesas_sistema, df_despesas_exec, df_despesas_manual, month_map_inv)

        logger.info(f"Filtrando dados para incluir apenas até o mês {month_end}.")
        df_receitas_full = df_receitas_full[df_receitas_full['MesNum'] <= month_end].copy()
        df_despesas_full = df_despesas_full[df_despesas_full['MesNum'] <= month_end].copy()
        
        df_resumo_full = calculate_financial_summary(df_receitas_full, df_despesas_full)

        def calculate_total_from_df(df: pd.DataFrame) -> float:
            if df.empty: return 0.0
            return df['Valor_Final'].sum()

        kpis = {
            "receita_total": calculate_total_from_df(df_receitas_full),
            "despesa_total": calculate_total_from_df(df_despesas_full),
        }
        kpis["resultado_mes"] = kpis["receita_total"] - kpis["despesa_total"]
        
        logger.info("🎨 Formatando dados para o relatório HTML...")
        df_receitas_fmt = pivot_and_format_financial_df(df_receitas_full, MONTH_MAP, month_end)
        df_despesas_fmt = pivot_and_format_financial_df(df_despesas_full, MONTH_MAP, month_end)
        df_resumo_fmt = pivot_and_format_financial_df(df_resumo_full, MONTH_MAP, month_end)

        # --- BLOCO DE VISUALIZAÇÃO CORRIGIDO E LIMPO ---
        print("\n\n" + "="*120)
        print(" VISUALIZAÇÃO DAS TABELAS FINAIS PARA O CONSOLE ".center(120, "="))
        print("="*120)
        
        print("\n--- TABELA DE RESUMO (SUPERÁVIT/DÉFICIT) ---")
        print(df_resumo_fmt)
        
        print("\n\n--- TABELA DE RECEITAS ---")
        print(df_receitas_fmt)
        
        print("\n\n--- TABELA DE DESPESAS ---")
        print(df_despesas_fmt)
        
        print("\n" + "="*120)
        print(" FIM DA VISUALIZAÇÃO ".center(120, "="))
        print("="*120 + "\n\n")
        # -----------------------------------------------
        
        tabelas_html = {
            "tabela_receitas": style_df_to_html(df_receitas_fmt),
            "tabela_despesas": style_df_to_html(df_despesas_fmt),
            "tabela_resumo": style_df_to_html(df_resumo_fmt, table_type='resumo'),
        }

        today_str = datetime.now().strftime('%d/%m/%Y')
        subject = f"{settings.email.subject_prefix} - {today_str} (Prévia até {MONTH_MAP[month_end].capitalize()})"
        texto_email = f"<p>Prezados,</p><p>Segue prévia da execução orçamentária para o ano de {year} (valores acumulados até {MONTH_MAP[month_end].capitalize()}), gerada em <strong>{today_str}</strong>.</p>"

        send_report_email(
            settings=settings, subject=subject,
            template_context={
                "assunto": subject, "texto_email": texto_email,
                "kpis": kpis, "settings": settings, **tabelas_html,
            }
        )

    except Exception as e:
        logger.critical("🔥 Ocorreu um erro fatal no processo: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("✅ Processo concluído com sucesso!")

def main():
    """Ponto de entrada principal da aplicação."""
    setup_logging()
    run_financial_report_flow(
        year=settings.filters.ano_filtro, 
        month_end=settings.filters.mes_filtro
    )

if __name__ == "__main__":
    main()
