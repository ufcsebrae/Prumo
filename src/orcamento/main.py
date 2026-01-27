import logging
import sys
from datetime import datetime

from orcamento.core.config import settings
from orcamento.core.logging_config import setup_logging
from orcamento.data_access.database import get_engine, execute_query
from orcamento.data_access.queries import get_queries
from orcamento.processing.financial_analysis import calculate_financial_summary
from orcamento.reporting.email_sender import send_report_email
from orcamento.reporting.formatting import pivot_and_format_financial_df, style_df_to_html

# Mapeamento de meses usado na camada de formatação
MONTH_MAP = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
}

# src/orcamento/main.py

def run_financial_report_flow(year: int) -> None:
    """Orquestra o fluxo de geração e envio do relatório financeiro."""
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando processo para o ano de %d...", year)

    try:
        queries = get_queries()
        engine = get_engine(settings.db)

        params = {"year": year}
        df_receitas_raw = execute_query(engine, queries["RECEITAS"].sql, params)
        df_despesas_raw = execute_query(engine, queries["DESPESAS"].sql, params)

        df_resumo_raw = calculate_financial_summary(df_receitas_raw, df_despesas_raw)

        # --- CÁLCULO DOS KPIs PARA O SUMÁRIO EXECUTIVO ---
        kpis = {"receita_total": 0, "despesa_total": 0, "resultado_mes": 0}
        if not df_receitas_raw.empty:
            kpis["receita_total"] = df_receitas_raw['Valor'].sum()
        if not df_despesas_raw.empty:
            kpis["despesa_total"] = df_despesas_raw['Valor'].sum()
        kpis["resultado_mes"] = kpis["receita_total"] - kpis["despesa_total"]
        # ---------------------------------------------------

        logger.info("🎨 Formatando dados para o relatório HTML...")
        df_receitas_fmt = pivot_and_format_financial_df(df_receitas_raw, MONTH_MAP)
        df_despesas_fmt = pivot_and_format_financial_df(df_despesas_raw, MONTH_MAP)
        df_resumo_fmt = pivot_and_format_financial_df(df_resumo_raw, MONTH_MAP)
        
        tabelas_html = {
            "tabela_receitas": style_df_to_html(df_receitas_fmt),
            "tabela_despesas": style_df_to_html(df_despesas_fmt),
            # Passa um identificador para a função de estilo saber quando colorir
            "tabela_resumo": style_df_to_html(df_resumo_fmt, table_type='resumo'),
        }

        today_str = datetime.now().strftime('%d/%m/%Y')
        subject = f"{settings.email.subject_prefix} - {today_str}"
        
        texto_email = f"""
        <p>Prezados,</p>
        <p>Segue prévia da execução orçamentária para o ano de {year},
        gerada em <strong>{today_str}</strong>.</p>
        """

        send_report_email(
            settings=settings,
            subject=subject,
            template_context={
                "assunto": subject,
                "texto_email": texto_email,
                "kpis": kpis,
                "settings": settings,  # <--- ESTA É A LINHA QUE FALTAVA
                **tabelas_html,
            },
        )

    except Exception as e:
        logger.critical("🔥 Ocorreu um erro fatal no processo: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("✅ Processo concluído com sucesso!")


def main() -> None:
    """Ponto de entrada da aplicação."""
    setup_logging()
    # O ano pode ser parametrizado (ex: via argumentos de linha de comando)
    # Por enquanto, usa o ano seguinte ao atual, como no SQL original.
    run_financial_report_flow(year=datetime.now().year)

if __name__ == "__main__":
    main()
