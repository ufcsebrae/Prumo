# src/orcamento/main.py
# --- VERSÃO FINAL COM TESTES DE CAMINHO INTEGRADOS ---

import logging
import sys
from datetime import datetime
import pandas as pd
from pathlib import Path  # Importa a classe Path para manipulação de caminhos

# Importa as configurações e módulos da nossa própria aplicação
from orcamento.core.config import settings
from orcamento.core.logging_config import setup_logging
from orcamento.data_access.database import get_engine, execute_query
from orcamento.data_access.queries import get_queries
from orcamento.processing.financial_analysis import combine_executed_and_forecast, calculate_financial_summary
from orcamento.reporting.formatting import pivot_and_format_financial_df, style_df_to_html
from orcamento.reporting.email_sender import send_report_email

# Mapeamento de meses (número para nome abreviado)
MONTH_MAP = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
}

def run_financial_report_flow(year: int) -> None:
    """
    Orquestra o fluxo completo de geração e envio do relatório financeiro.
    """
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando processo para o ano de %d...", year)

    try:
        # --- 1. PREPARAÇÃO ---
        queries = get_queries()
        engine = get_engine(settings.db)
        params = {"year": year}
        month_map_inv = {v: k for k, v in MONTH_MAP.items()}

        # --- 2. CARREGAMENTO DE DADOS PREVISTOS (COM TESTES DE DEPURAÇÃO) ---
        
        # Teste para o arquivo de RECEITAS
        forecast_receitas_path = settings.ROOT_DIR / "src/orcamento/forecast_data/previsao_receitas.csv"
        logger.info(f"🔎 [TESTE] Procurando arquivo de previsão de receitas em: {forecast_receitas_path}")
        
        if forecast_receitas_path.exists():
            df_receitas_prev = pd.read_csv(forecast_receitas_path)
            logger.info("✅ [SUCESSO] Arquivo de previsão de receitas encontrado e carregado.")
        else:
            df_receitas_prev = pd.DataFrame()
            logger.warning("❌ [FALHA] ARQUIVO DE PREVISÃO DE RECEITAS NÃO ENCONTRADO. Verifique o caminho e o nome do arquivo. Continuando sem previsões de receita.")

        # Teste para o arquivo de DESPESAS
        forecast_despesas_path = settings.ROOT_DIR / "src/orcamento/forecast_data/previsao_despesas.csv"
        logger.info(f"🔎 [TESTE] Procurando arquivo de previsão de despesas em: {forecast_despesas_path}")
        
        if forecast_despesas_path.exists():
            df_despesas_prev = pd.read_csv(forecast_despesas_path)
            logger.info("✅ [SUCESSO] Arquivo de previsão de despesas encontrado e carregado.")
        else:
            df_despesas_prev = pd.DataFrame()
            logger.warning("❌ [FALHA] ARQUIVO DE PREVISÃO DE DESPESAS NÃO ENCONTRADO. Verifique o caminho e o nome do arquivo. Continuando sem previsões de despesa.")

        # --- 3. EXTRAÇÃO E COMBINAÇÃO ---
        df_receitas_exec = execute_query(engine, queries["RECEITAS"].sql, params)
        df_despesas_exec = execute_query(engine, queries["DESPESAS"].sql, params)

        df_receitas_full = combine_executed_and_forecast(df_receitas_exec, df_receitas_prev, month_map_inv)
        df_despesas_full = combine_executed_and_forecast(df_despesas_exec, df_despesas_prev, month_map_inv)

        # --- 4. PROCESSAMENTO E FORMATAÇÃO ---
        df_resumo_full = calculate_financial_summary(df_receitas_full, df_despesas_full)

        kpis = {
            "receita_total": df_receitas_full['Valor'].sum() if not df_receitas_full.empty else 0,
            "despesa_total": df_despesas_full['Valor'].sum() if not df_despesas_full.empty else 0,
        }
        kpis["resultado_mes"] = kpis["receita_total"] - kpis["despesa_total"]
        
        logger.info("🎨 Formatando dados para o relatório HTML...")
        df_receitas_fmt = pivot_and_format_financial_df(df_receitas_full, MONTH_MAP)
        df_despesas_fmt = pivot_and_format_financial_df(df_despesas_full, MONTH_MAP)
        df_resumo_fmt = pivot_and_format_financial_df(df_resumo_full, MONTH_MAP)
        
        tabelas_html = {
            "tabela_receitas": style_df_to_html(df_receitas_fmt),
            "tabela_despesas": style_df_to_html(df_despesas_fmt),
            "tabela_resumo": style_df_to_html(df_resumo_fmt, table_type='resumo'),
        }

        # --- 5. PREPARAÇÃO E ENVIO DO E-MAIL ---
        today_str = datetime.now().strftime('%d/%m/%Y')
        subject = f"{settings.email.subject_prefix} - {today_str}"
        
        texto_email = f"<p>Prezados,</p><p>Segue prévia da execução orçamentária para o ano de {year}, gerada em <strong>{today_str}</strong>.</p>"

        send_report_email(
            settings=settings,
            subject=subject,
            template_context={
                "assunto": subject, "texto_email": texto_email,
                "kpis": kpis, "settings": settings, **tabelas_html,
            },
        )

    except Exception as e:
        logger.critical("🔥 Ocorreu um erro fatal no processo: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("✅ Processo concluído com sucesso!")

def main() -> None:
    """Ponto de entrada principal da aplicação."""
    setup_logging()
    run_financial_report_flow(year=datetime.now().year)

if __name__ == "__main__":
    main()
