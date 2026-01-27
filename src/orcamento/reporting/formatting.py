# src/orcamento/reporting/formatting.py

import pandas as pd
from orcamento.core.config import settings

def format_as_brl(value: int | float) -> str:
    """Formata um valor para BRL, retornando string vazia para 0 ou N/A."""
    if pd.isna(value) or value == 0:
        return ""
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)

def apply_semantic_color(value: int | float) -> str:
    """Retorna uma string de estilo CSS com cor baseada no valor (positivo/negativo)."""
    if pd.isna(value) or value == 0:
        return ""
    color = settings.colors.positive if value > 0 else settings.colors.negative
    return f"color: {color};"

def pivot_and_format_financial_df(df: pd.DataFrame, month_map: dict) -> pd.DataFrame:
    """Transforma, formata e exibe dinamicamente apenas os meses com dados."""
    if df.empty:
        return pd.DataFrame(columns=['Grupo', 'Total Anual'])

    df_pivot = df.pivot_table(index='Grupo', columns='MesNum', values='Valor', aggfunc='sum')
    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns=month_map)
    
    all_months = [month_map[i] for i in sorted(month_map.keys())]
    active_months = [
        month for month in all_months 
        if month in df_pivot.columns and df_pivot[month].abs().sum() > 0.01
    ]
    
    df_pivot = df_pivot.reindex(columns=active_months, fill_value=0)
    
    df_pivot['Total Anual'] = df_pivot.sum(axis=1)
    total_geral_row = df_pivot.sum().to_frame('TOTAL GERAL').T
    df_final = pd.concat([df_pivot, total_geral_row])
    
    return df_final.reset_index().rename(columns={'index': 'Grupo'})

def style_df_to_html(df: pd.DataFrame, table_type: str = 'default') -> str:
    """
    Converte e estiliza um DataFrame para HTML.
    Aplica cores semânticas se table_type for 'resumo'.
    """
    if df.empty:
        return "<p>Não há dados para exibir.</p>"

    # Seleciona colunas numéricas (exclui a primeira, 'Grupo')
    numeric_cols = df.columns[1:]
    
    styler = df.style.format(format_as_brl, subset=numeric_cols)

    # Aplica cor condicional apenas na tabela de resumo
    if table_type == 'resumo':
        styler = styler.apply(
            lambda r: r.map(apply_semantic_color), 
            subset=numeric_cols
        )
        
    return styler.hide(axis="index").to_html(
        justify="center",
        classes="table table-striped"
    )
