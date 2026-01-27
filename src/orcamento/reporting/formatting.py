# src/orcamento/reporting/formatting.py
# --- VERSÃO FINAL, SEM O BUG DO .fillna() ---

import pandas as pd
from orcamento.core.config import settings

def pivot_and_format_financial_df(df: pd.DataFrame, month_map: dict) -> pd.DataFrame:
    """
    Cria uma tabela pivotada única contendo tuplas de (Valor, Tipo) e garante que
    todas as colunas e totais sejam calculados corretamente.
    """
    if df.empty:
        return pd.DataFrame(columns=['Grupo'])

    df['ValorTipo'] = list(zip(df['Valor'], df['Tipo']))

    df_pivot = df.pivot_table(index='Grupo', columns='MesNum', values='ValorTipo', aggfunc='first')
    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns=month_map)

    all_months = [month_map[i] for i in sorted(month_map.keys())]
    
    for month in all_months:
        if month not in df_pivot.columns:
            df_pivot[month] = pd.NA # Adiciona meses faltantes como N/A

    # --- A CORREÇÃO ESTÁ AQUI ---
    # Substituímos o .fillna() incorreto pelo .apply() que funciona.
    # Ele itera sobre cada célula e, se for nula, a substitui pela tupla padrão.
    df_pivot = df_pivot.apply(
        lambda col: col.apply(lambda cell: (0, 'vazio') if pd.isna(cell) else cell)
    )
    # -----------------------------

    df_pivot = df_pivot[all_months]
    
    def sum_tuples(series):
        return series.apply(lambda x: x[0] if isinstance(x, tuple) else 0).sum()

    df_pivot['Total Anual'] = df_pivot.apply(sum_tuples, axis=1)
    df_pivot['Total Anual'] = df_pivot['Total Anual'].apply(lambda val: (val, 'total'))

    total_geral_row = df_pivot.apply(sum_tuples).to_frame('TOTAL GERAL').T
    total_geral_row = total_geral_row.map(lambda val: (val, 'total'))

    df_final = pd.concat([df_pivot, total_geral_row])
    
    return df_final.reset_index().rename(columns={'index': 'Grupo'})

def style_df_to_html(df: pd.DataFrame, table_type: str = 'default') -> str:
    """
    Estiliza o DataFrame de tuplas (Valor, Tipo) para HTML.
    """
    if df.empty or df.shape[1] <= 1:
        return "<p>Não há dados para exibir.</p>"

    def format_display(cell_tuple):
        val, tipo = cell_tuple
        if pd.isna(val) or val == 0: return ""
        formatted_val = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"({formatted_val})" if tipo in ['previsto', 'combinado'] else formatted_val
    
    def apply_style(cell_tuple):
        val, tipo = cell_tuple
        style = ''
        if tipo == 'previsto':
            style = f"color: {settings.colors.forecast}; font-style: italic;"
        elif tipo == 'combinado':
            style = f"color: {settings.colors.forecast};"
        elif table_type == 'resumo' and tipo != 'total' and val != 0:
            color = settings.colors.positive if val > 0 else settings.colors.negative
            style = f"color: {color};"
        return style

    data_cols = df.columns.drop('Grupo')
    
    styler = df.style.format(formatter=format_display, subset=data_cols) \
                     .apply(lambda df_subset: df_subset.map(apply_style), subset=data_cols)
        
    return styler.hide(axis="index").to_html(
        justify="center",
        classes="table table-striped"
    )
