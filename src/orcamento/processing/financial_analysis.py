# src/orcamento/processing/financial_analysis.py
# --- VERSÃO FINAL QUE MANTÉM VALORES SEPARADOS PARA A CAMADA DE VISUALIZAÇÃO ---

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def combine_executed_and_forecast(
    df_executado: pd.DataFrame, 
    df_previsto: pd.DataFrame, 
    month_map_inv: dict
) -> pd.DataFrame:
    """
    Combina dados executados e previstos, mantendo os valores em colunas separadas
    ('Valor_exec', 'Valor_prev') para uso na camada de formatação.
    """
    df_executado = df_executado.copy()
    
    # Padroniza e prepara os dados executados
    if not df_executado.empty:
        df_executado['Grupo'] = df_executado['Grupo'].str.upper().str.strip()
    else:
        df_executado = pd.DataFrame(columns=['Grupo', 'MesNum', 'Valor'])

    # Renomeia a coluna para clareza
    df_executado.rename(columns={'Valor': 'Valor_exec'}, inplace=True)

    if df_previsto.empty:
        df_executado['Valor_prev'] = 0 # Garante que a coluna exista
        return df_executado

    # Padroniza e prepara os dados de previsão
    df_previsto = df_previsto.copy()
    df_previsto['Grupo'] = df_previsto['Grupo'].str.upper().str.strip()
    df_previsto['MesNum'] = df_previsto['Mes'].str.lower().map(month_map_inv)
    df_previsto = df_previsto.dropna(subset=['MesNum'])
    df_previsto['MesNum'] = df_previsto['MesNum'].astype(int)
    
    # Agrega os dados de previsão em caso de múltiplas entradas no CSV
    df_previsto_agg = df_previsto.groupby(['Grupo', 'MesNum'])['Valor'].sum().reset_index()
    df_previsto_agg.rename(columns={'Valor': 'Valor_prev'}, inplace=True)

    # Faz o merge, mantendo todas as linhas de ambos
    df_merged = pd.merge(
        df_executado,
        df_previsto_agg,
        on=['Grupo', 'MesNum'],
        how='outer'
    )

    # Preenche com 0 onde não há valor, para garantir que os cálculos funcionem
    df_merged.fillna({'Valor_exec': 0, 'Valor_prev': 0}, inplace=True)
    
    return df_merged

def calculate_financial_summary(
    df_receitas: pd.DataFrame, df_despesas: pd.DataFrame
) -> pd.DataFrame:
    """Calcula o superávit/déficit a partir dos dataframes que contêm valores separados."""
    # Para o resumo, o "Valor" é a soma do executado e previsto
    df_receitas['Valor'] = df_receitas['Valor_exec'] + df_receitas['Valor_prev']
    df_despesas['Valor'] = df_despesas['Valor_exec'] + df_despesas['Valor_prev']

    df_rec = df_receitas.groupby('MesNum')['Valor'].sum()
    df_des = df_despesas.groupby('MesNum')['Valor'].sum()
    total_receitas, total_despesas = df_rec.align(df_des, fill_value=0)
    
    df_resumo = (total_receitas - total_despesas).reset_index()
    df_resumo = df_resumo.rename(columns={0: 'Valor'})
    df_resumo['Grupo'] = 'SUPERÁVIT/DÉFICIT'
    
    # O resumo precisa das colunas separadas para a formatação funcionar
    df_resumo['Valor_exec'] = df_resumo['Valor']
    df_resumo['Valor_prev'] = 0
    df_resumo['Tipo'] = 'resumo' # Adiciona o tipo para a estilização

    return df_resumo
