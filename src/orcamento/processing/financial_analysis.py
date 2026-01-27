# src/orcamento/processing/financial_analysis.py
# --- VERSÃO FINAL COM A LÓGICA DE MERGE CORRIGIDA E ROBUSTA ---

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def combine_executed_and_forecast(
    df_executado: pd.DataFrame, 
    df_previsto: pd.DataFrame, 
    month_map_inv: dict
) -> pd.DataFrame:
    """
    Combina dados executados e previstos com uma lógica de merge robusta
    que padroniza os nomes dos grupos para garantir a correspondência.
    """
    df_executado = df_executado.copy()
    
    # Padroniza a coluna 'Grupo' dos dados executados
    if not df_executado.empty:
        df_executado['Grupo'] = df_executado['Grupo'].str.upper().str.strip()
        df_executado['Tipo'] = 'executado'
    else:
        # Garante que as colunas existam mesmo se o DataFrame estiver vazio
        df_executado = pd.DataFrame(columns=['Grupo', 'MesNum', 'Valor', 'Tipo'])

    if df_previsto.empty:
        return df_executado

    # Padroniza a coluna 'Grupo' dos dados de previsão
    df_previsto = df_previsto.copy()
    df_previsto['Grupo'] = df_previsto['Grupo'].str.upper().str.strip()
    df_previsto['MesNum'] = df_previsto['Mes'].str.lower().map(month_map_inv)
    df_previsto = df_previsto.dropna(subset=['MesNum'])
    df_previsto['MesNum'] = df_previsto['MesNum'].astype(int)
    
    # Agrega os dados de previsão para o caso de múltiplas entradas no CSV
    df_previsto_agg = df_previsto.groupby(['Grupo', 'MesNum'])['Valor'].sum().reset_index()

    # Faz o merge dos dois dataframes, mantendo todas as linhas de ambos
    df_merged = pd.merge(
        df_executado,
        df_previsto_agg,
        on=['Grupo', 'MesNum'],
        how='outer',
        suffixes=('_exec', '_prev')
    )

    # Lógica de Prioridade: Executado > Previsto
    df_merged['Valor'] = np.where(df_merged['Valor_exec'].notna(), df_merged['Valor_exec'], df_merged['Valor_prev'])
    df_merged['Tipo'] = np.where(df_merged['Valor_exec'].notna(), 'executado', 'previsto')
    
    # Retorna o DataFrame limpo, pronto para a próxima etapa
    return df_merged[['Grupo', 'MesNum', 'Valor', 'Tipo']].copy()


def calculate_financial_summary(
    df_receitas: pd.DataFrame, df_despesas: pd.DataFrame
) -> pd.DataFrame:
    """Calcula o superávit/déficit a partir dos dataframes combinados."""
    if df_receitas.empty and df_despesas.empty:
        return pd.DataFrame()

    df_rec = df_receitas.groupby('MesNum')['Valor'].sum()
    df_des = df_despesas.groupby('MesNum')['Valor'].sum()

    total_receitas, total_despesas = df_rec.align(df_des, fill_value=0)
    
    df_resumo = (total_receitas - total_despesas).reset_index()
    df_resumo = df_resumo.rename(columns={0: 'Valor'})
    df_resumo['Grupo'] = 'SUPERÁVIT/DÉFICIT'
    df_resumo['Tipo'] = 'resumo' # Tipo especial para a tabela de resumo
    return df_resumo

