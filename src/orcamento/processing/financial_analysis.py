# src/orcamento/processing/financial_analysis.py
# --- ATUALIZADO COM A NOVA REGRA DE NEGÓCIO PARA O VALOR FINAL ---

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def process_planning_data(
    df_planejado: pd.DataFrame, 
    df_de_para: pd.DataFrame,
    month_map_inv: dict
) -> pd.DataFrame:
    # (Esta função não precisa de alterações)
    if df_planejado.empty or df_de_para.empty: return pd.DataFrame()
    df_de_para.columns = ['Natureza_Planejamento', 'Grupo_Execucao', 'Tipo_Fluxo']
    df_de_para['Natureza_Planejamento'] = df_de_para['Natureza_Planejamento'].str.upper().str.strip()
    df_planejado['Descrição Natureza'] = df_planejado['Descrição Natureza'].str.upper().str.strip()
    df_mapped = pd.merge(df_planejado, df_de_para, left_on='Descrição Natureza', right_on='Natureza_Planejamento', how='inner')
    df_agg = df_mapped.groupby(['Grupo_Execucao', 'Mês', 'Tipo_Fluxo'])['Valor'].sum().reset_index()
    df_agg.rename(columns={'Grupo_Execucao': 'Grupo', 'Valor': 'Planejado'}, inplace=True)
    df_agg.rename(columns={'Mês': 'MesNum'}, inplace=True)
    df_agg['MesNum'] = pd.to_numeric(df_agg['MesNum'], errors='coerce').astype('Int64')
    logger.info(f"Dados de planejamento mapeados e agregados com sucesso para {len(df_agg)} linhas.")
    return df_agg

def combinar_fontes_financeiras(
    df_planejado_sistema: pd.DataFrame,
    df_executado: pd.DataFrame,
    df_previsao_manual: pd.DataFrame,
    month_map_inv: dict
) -> pd.DataFrame:
    """Combina as fontes e calcula o 'Valor_Final' com a nova regra de negócio."""
    df_planejado = df_planejado_sistema.rename(columns={'Planejado': 'Planejado'})
    df_exec = df_executado.rename(columns={'Valor': 'Executado'})
    df_manual = df_previsao_manual.rename(columns={'Valor': 'Previsão'})

    if not df_manual.empty and 'MesNum' not in df_manual.columns:
        df_manual['MesNum'] = df_manual['Mes'].str.lower().map(month_map_inv)
        df_manual['MesNum'] = pd.to_numeric(df_manual['MesNum'], errors='coerce').astype('Int64')
    
    for df in [df_planejado, df_exec, df_manual]:
        if not df.empty and 'Grupo' in df.columns:
            df['Grupo'] = df['Grupo'].str.upper().str.strip()

    merge_cols = ['Grupo', 'MesNum']
    df_merged = pd.merge(df_planejado, df_exec, on=merge_cols, how='outer')
    df_merged = pd.merge(df_merged, df_manual, on=merge_cols, how='outer')

    cols_to_fill = ['Planejado', 'Executado', 'Previsão']
    for col in cols_to_fill:
        if col not in df_merged.columns: df_merged[col] = 0.0
    df_merged[cols_to_fill] = df_merged[cols_to_fill].fillna(0)
    
    # --- NOVA LÓGICA CENTRALIZADA PARA 'Valor_Final' ---
    condicoes_final = [
        # 1. Se há Previsão, o valor é o MAIOR entre a Previsão e o que já foi Executado.
        df_merged['Previsão'] > 0,
        # 2. Se não há Previsão, mas há Executado, o valor é o Executado.
        (df_merged['Previsão'] == 0) & (df_merged['Executado'] != 0),
    ]
    
    resultados_final = [
        df_merged[['Previsão', 'Executado']].max(axis=1),
        df_merged['Executado'],
    ]
    
    # 3. Fallback: Se não há Previsão nem Executado, usa o Planejado como valor final.
    df_merged['Valor_Final'] = np.select(
        condicoes_final, 
        resultados_final, 
        default=df_merged['Planejado']
    )
    # ----------------------------------------------------
    
    # Retorna o DataFrame com a nova coluna, que será usada por todos os outros módulos
    df_final = df_merged[['Grupo', 'MesNum', 'Planejado', 'Executado', 'Previsão', 'Valor_Final']]
    return df_final.sort_values(by=['MesNum', 'Grupo']).reset_index(drop=True)


def calculate_financial_summary(
    df_receitas: pd.DataFrame, 
    df_despesas: pd.DataFrame
) -> pd.DataFrame:
    # (Esta função não precisa de alterações)
    logger.info("Calculando resumo financeiro (Superávit/Déficit)...")
    value_cols = ['Planejado', 'Executado', 'Previsão', 'Valor_Final']
    df_rec_agg = df_receitas.groupby('MesNum')[value_cols].sum() if not df_receitas.empty else pd.DataFrame(columns=value_cols)
    df_des_agg = df_despesas.groupby('MesNum')[value_cols].sum() if not df_despesas.empty else pd.DataFrame(columns=value_cols)
    rec_aligned, des_aligned = df_rec_agg.align(df_des_agg, fill_value=0)
    df_resumo = (rec_aligned - des_aligned).reset_index()
    df_resumo['Grupo'] = 'SUPERÁVIT/DÉFICIT'
    return df_resumo
