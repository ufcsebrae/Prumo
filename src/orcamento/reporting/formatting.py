# src/orcamento/reporting/formatting.py
# --- VERSÃO FINAL E CORRETA, REMOVENDO O NOME DO EIXO DA COLUNA ---

import pandas as pd

def format_to_brl(value: int | float) -> str:
    """Formata um valor numérico para a moeda brasileira (BRL)."""
    if pd.isna(value):
        return ""
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)

def pivot_and_format_financial_df(
    df: pd.DataFrame, month_map: dict[int, str]
) -> pd.DataFrame:
    """
    Transforma dados do formato longo para largo, calcula totais,
    e formata os valores como moeda.
    """
    df_pivot = df.pivot_table(
        index='Grupo', columns='MesNum', values='Valor', aggfunc='sum'
    ).fillna(0)

    # ================== A NOVA LINHA DE CORREÇÃO ESTÁ AQUI ==================
    # Remove o nome 'MesNum' do eixo das colunas, que é a causa do problema.
    df_pivot.columns.name = None
    # =======================================================================
    
    df_pivot = df_pivot.rename(columns=month_map)
    ordered_months = [month_map[i] for i in sorted(month_map.keys())]
    
    for month in ordered_months:
        if month not in df_pivot.columns:
            df_pivot[month] = 0
            
    df_pivot = df_pivot[ordered_months]
    
    df_pivot['Total Anual'] = df_pivot.sum(axis=1)
    total_geral_row = df_pivot.sum().to_frame('TOTAL GERAL').T
    df_final = pd.concat([df_pivot, total_geral_row])
    
    df_formatted = df_final.map(format_to_brl)
    
    df_with_group = df_formatted.reset_index().rename(columns={'index': 'Grupo'})

    return df_with_group

def style_df_to_html(df: pd.DataFrame) -> str:
    """Converte um DataFrame para uma string de tabela HTML com classes CSS."""
    return df.to_html(
        index=False,
        justify="center",
        border=0,
        classes="table table-striped",
        na_rep=""
    )
