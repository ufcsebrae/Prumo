# src/orcamento/processing/financial_analysis.py

import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

def combine_executed_and_forecast(
    df_executado: pd.DataFrame, 
    df_previsto: pd.DataFrame, 
    month_map_inv: dict
) -> pd.DataFrame:
    """
    Combina dados executados e previstos, criando uma estrutura de valor unificada.
    """
    if df_previsto.empty:
        df_executado['Tipo'] = 'executado'
        return df_executado.rename(columns={'Valor': 'ValorFinal'})

    # Prepara o DataFrame de previsão
    df_previsto['MesNum'] = df_previsto['Mes'].str.lower().map(month_map_inv)
    df_previsto = df_previsto.dropna(subset=['MesNum'])
    df_previsto['MesNum'] = df_previsto['MesNum'].astype(int)

    # Combina os dois DataFrames
    df_merged = pd.merge(
        df_executado,
        df_previsto[['Grupo', 'MesNum', 'Valor']],
        on=['Grupo', 'MesNum'],
        how='outer',
        suffixes=('_exec', '_prev')
    )

    # Calcula o valor final e determina o tipo
    df_merged['ValorFinal'] = df_merged['Valor_exec'].fillna(0) + df_merged['Valor_prev'].fillna(0)
    
    conditions = [
        (df_merged['Valor_exec'].notna()) & (df_merged['Valor_prev'].notna()),
        (df_merged['Valor_exec'].notna()),
        (df_merged['Valor_prev'].notna())
    ]
    choices = ['combinado', 'executado', 'previsto']
    df_merged['Tipo'] = np.select(conditions, choices, default='vazio')
    
    # Retorna o DataFrame limpo com as colunas necessárias
    return df_merged[['Grupo', 'MesNum', 'ValorFinal', 'Tipo']].copy()


def calculate_financial_summary(
    df_receitas: pd.DataFrame, df_despesas: pd.DataFrame
) -> pd.DataFrame:
    """Calcula o superávit/déficit, agora considerando os tipos de valor."""
    
    def get_valor(row, tipo_valor):
        return row['ValorFinal'] if row['Tipo'] == tipo_valor else 0

    if df_receitas.empty and df_despesas.empty:
        return pd.DataFrame()

    df_merged = pd.merge(
        df_receitas, df_despesas, 
        on='MesNum', 
        how='outer', 
        suffixes=('_rec', '_des')
    ).fillna(0)
    
    df_merged['ValorFinal'] = df_merged['ValorFinal_rec'] - df_merged['ValorFinal_des']
    df_merged['Tipo'] = 'resumo' # O tipo do resumo é sempre 'resumo'
    
    df_summary = df_merged[['MesNum', 'ValorFinal', 'Tipo']]
    df_summary['Grupo'] = 'SUPERÁVIT/DÉFICIT' # Adiciona a coluna Grupo
    
    # Lógica para "sem aplicações" pode ser adicionada aqui se necessário
    
    return df_summary
