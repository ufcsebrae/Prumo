# src/orcamento/reporting/formatting.py
# --- VERSÃO FINAL COM A CORREÇÃO DA REGRA DE NEGÓCIO NOS TOTAIS ---

import pandas as pd
import numpy as np
from orcamento.core.config import settings

def pivot_and_format_financial_df(df: pd.DataFrame, month_map: dict, month_end: int) -> pd.DataFrame:
    """Prepara o DataFrame, usando o 'Valor_Final' pré-calculado para garantir consistência."""
    if df.empty:
        return pd.DataFrame(columns=['Grupo'])

    # A coluna 'Valor_Final' já vem pré-calculada do passo anterior com a regra de negócio correta.
    # Não precisamos mais calculá-la aqui.

    value_cols = ['Executado', 'Planejado', 'Previsão']
    
    # Cria a tabela dinâmica para os valores mensais detalhados
    df_pivot = df.pivot_table(index='Grupo', columns='MesNum', values=value_cols, aggfunc='sum', fill_value=0)

    if not df_pivot.empty:
        df_pivot = df_pivot.swaplevel(0, 1, axis=1)
    
    df_pivot.rename(columns=month_map, level=0, inplace=True)
    
    ordered_months = [month_map[i] for i in range(1, month_end + 1)]
    
    metric_rename_map = {'Executado': 'Exec.', 'Planejado': 'Plan.', 'Previsão': 'Prev.'}
    ordered_metrics = [metric_rename_map[m] for m in value_cols]

    final_col_order = pd.MultiIndex.from_product([ordered_months, ordered_metrics])
    
    df_pivot.rename(columns=metric_rename_map, level=1, inplace=True)
    df_pivot = df_pivot.reindex(columns=final_col_order, fill_value=0)
    
    # Calcula o Total Anual SOMANDO a coluna 'Valor_Final', que agora está correta.
    total_anual = df.groupby('Grupo')['Valor_Final'].sum().to_frame()
    total_anual.rename(columns={'Valor_Final': 'Total Anual'}, inplace=True)
    
    # Junta o pivot dos meses com o total anual correto.
    df_final = pd.concat([df_pivot, total_anual], axis=1)

    # Renomeia a coluna de total para ter um MultiIndex e evitar problemas de formatação
    df_final.columns = pd.MultiIndex.from_tuples(
        [(col[0], col[1]) if isinstance(col, tuple) else (col, '') for col in df_final.columns]
    )
    
    # Calcula o TOTAL GERAL, que agora também será consistente.
    total_geral_row = df_final.sum().to_frame('TOTAL GERAL').T
    df_final = pd.concat([df_final, total_geral_row])
    
    return df_final.reset_index().rename(columns={'index': 'Grupo'})

def style_df_to_html(df: pd.DataFrame, table_type: str = 'default') -> str:
    # (A função de estilo não precisa de alterações)
    if df.empty or df.shape[1] <= 1: return "<p>Não há dados para exibir.</p>"

    def format_value_short(value):
        if pd.isna(value) or value == 0: return "-"
        abs_value = abs(value)
        if abs_value >= 1_000_000:
            formatted_val = f"{value / 1_000_000:.1f}M"
        elif abs_value >= 1_000:
            formatted_val = f"{value / 1_000:.1f}k"
        else:
            formatted_val = f"{value:.0f}"
        return formatted_val.replace('.', ',')

    data_cols = df.columns.drop('Grupo')
    
    # Prepara para aplicar estilo na linha de total
    df_styled = df.set_index('Grupo')
    styler = df_styled.style.format(format_value_short, na_rep="-", subset=data_cols)

    # Aplica negrito nas colunas de 'Total Anual'
    total_anual_cols_styled = df_styled.columns.get_level_values(0) == 'Total Anual'
    styler.set_properties(**{'font-weight': 'bold'}, subset=df_styled.columns[total_anual_cols_styled])

    # Aplica negrito na linha 'TOTAL GERAL'
    styler.set_properties(**{'font-weight': 'bold'}, subset=pd.IndexSlice[df_styled.index[-1], :])
    
    styler = styler.set_table_attributes('class="table table-striped table-grid"')
    
    return styler.to_html(justify="center")
