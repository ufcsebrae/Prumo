# src/orcamento/reporting/formatting.py
# --- VERSÃO FINAL COM A CORREÇÃO DO 'Length of values' ---

import pandas as pd
from orcamento.core.config import settings

def pivot_and_format_financial_df(df: pd.DataFrame, month_map: dict) -> pd.DataFrame:
    """Prepara o DataFrame para a estilização, criando tuplas de (Exec, Prev)."""
    if df.empty:
        return pd.DataFrame(columns=['Grupo'])

    df['ValorTupla'] = list(zip(df['Valor_exec'], df['Valor_prev']))

    df_pivot = df.pivot_table(index='Grupo', columns='MesNum', values='ValorTupla', aggfunc='first')
    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns=month_map)

    all_months = [month_map[i] for i in sorted(month_map.keys())]
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Para cada mês que não existe, cria uma nova coluna preenchida com a tupla
    # padrão, repetida para cada linha do DataFrame.
    for month in all_months:
        if month not in df_pivot.columns:
            # Cria uma lista de tuplas com o comprimento correto do índice
            default_values = [(0, 0)] * len(df_pivot.index)
            df_pivot[month] = default_values
    # --------------------------------

    # Preenche qualquer outro valor nulo que possa ter sobrado
    df_pivot = df_pivot.apply(lambda col: col.apply(lambda cell: (0, 0) if pd.isna(cell) else cell))
    
    df_pivot = df_pivot[all_months]
    
    def sum_total_annual(row):
        total = 0
        for cell in row:
            if isinstance(cell, tuple):
                exec_val, prev_val = cell
                total += exec_val + prev_val
        return total

    df_pivot['Total Anual'] = df_pivot.apply(sum_total_annual, axis=1)
    df_pivot['Total Anual'] = df_pivot['Total Anual'].apply(lambda val: (val, 0))

    total_geral_row = df_pivot.apply(sum_total_annual).to_frame('TOTAL GERAL').T
    total_geral_row = total_geral_row.map(lambda val: (val, 0))

    df_final = pd.concat([df_pivot, total_geral_row])
    return df_final.reset_index().rename(columns={'index': 'Grupo'})

def style_df_to_html(df: pd.DataFrame, table_type: str = 'default') -> str:
    """Estiliza o DataFrame de tuplas (Valor_exec, Valor_prev) para HTML."""
    if df.empty or df.shape[1] <= 1:
        return "<p>Não há dados para exibir.</p>"

    def format_brl(value):
        if pd.isna(value) or value == 0: return None
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def format_display(cell_tuple):
        exec_val, prev_val = cell_tuple
        exec_str = format_brl(exec_val)
        prev_str = format_brl(prev_val)

        if exec_str and prev_str: return f"{exec_str} ({prev_str})"
        if exec_str: return exec_str
        if prev_str: return f"({prev_str})"
        return ""
    
    def apply_style(cell_tuple):
        exec_val, prev_val = cell_tuple
        if exec_val == 0 and prev_val > 0:
            return f"color: {settings.colors.forecast}; font-style: italic;"
        if table_type == 'resumo' and exec_val != 0:
             color = settings.colors.positive if exec_val > 0 else settings.colors.negative
             return f"color: {color};"
        return ""

    data_cols = df.columns.drop('Grupo')
    styler = df.style.format(formatter=format_display, subset=data_cols) \
                     .apply(lambda s: s.map(apply_style), subset=data_cols)
        
    return styler.hide(axis="index").to_html(justify="center", classes="table table-striped")
