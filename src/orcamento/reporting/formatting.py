# src/orcamento/reporting/formatting.py
# --- VERSÃO COM COLUNAS DINÂMICAS E MELHORIAS VISUAIS ---

import pandas as pd

def format_to_brl(value: int | float) -> str:
    """Formata um valor para BRL, retornando string vazia para 0 ou N/A."""
    if pd.isna(value) or value == 0:
        return ""
    try:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)

def pivot_and_format_financial_df(
    df: pd.DataFrame, month_map: dict[int, str]
) -> pd.DataFrame:
    """
    Transforma, formata e exibe dinamicamente apenas os meses com dados.
    """
    if df.empty:
        return pd.DataFrame(columns=['Grupo', 'Total Anual'])

    df_pivot = df.pivot_table(
        index='Grupo', columns='MesNum', values='Valor', aggfunc='sum'
    )
    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns=month_map)
    
    # --- LÓGICA DE COLUNAS DINÂMICAS ---
    # 1. Identifica quais meses têm valores (soma do valor absoluto > 0)
    all_months = [month_map[i] for i in sorted(month_map.keys())]
    active_months = [
        month for month in all_months 
        if month in df_pivot.columns and df_pivot[month].abs().sum() > 0
    ]
    
    # 2. Seleciona apenas os meses ativos
    df_pivot = df_pivot[active_months]
    
    # 3. Calcula os totais com base apenas nos meses ativos
    df_pivot['Total Anual'] = df_pivot.sum(axis=1)
    total_geral_row = df_pivot.sum().to_frame('TOTAL GERAL').T
    df_final = pd.concat([df_pivot, total_geral_row])
    
    df_formatted = df_final.map(format_to_brl)
    df_with_group = df_formatted.reset_index().rename(columns={'index': 'Grupo'})

    return df_with_group

def style_df_to_html(df: pd.DataFrame) -> str:
    """Converte um DataFrame para uma string de tabela HTML."""
    return df.to_html(
        index=False,
        justify="center",
        border=0,
        classes="table table-striped",
        na_rep=""
    )
