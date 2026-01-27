import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_financial_summary(
    df_receitas: pd.DataFrame, 
    df_despesas: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula o superávit/déficit com base nos DataFrames de receitas e despesas.
    Ambos os DataFrames de entrada devem estar no formato longo (Grupo, MesNum, Valor).
    """
    logger.info("Calculando resumo financeiro (superávit/déficit).")

    # 1. Agrega os totais por mês para receitas e despesas
    series_receitas_total = df_receitas.groupby('MesNum')['Valor'].sum()
    series_despesas_total = df_despesas.groupby('MesNum')['Valor'].sum()

    # Alinha os dados, preenchendo meses sem dados com 0 para segurança
    series_receitas_total, series_despesas_total = series_receitas_total.align(
        series_despesas_total, fill_value=0
    )
    
    # 2. Calcula o superávit/déficit padrão
    df_summary = (series_receitas_total - series_despesas_total).to_frame('SUPERÁVIT/DÉFICIT').T

    # 3. Calcula o superávit sem aplicações financeiras
    series_aplicacoes = df_receitas[
        df_receitas['Grupo'] == 'APLICAÇÕES FINANCEIRAS'
    ].groupby('MesNum')['Valor'].sum()
    series_aplicacoes, _ = series_aplicacoes.align(series_receitas_total, fill_value=0)
    
    series_sem_aplicacoes = series_receitas_total - series_aplicacoes - series_despesas_total
    df_sem_aplicacoes = series_sem_aplicacoes.to_frame('SUPERÁVIT/DÉFICIT (SEM APLICAÇÕES FINANCEIRAS)').T
    
    # 4. Concatena os dois resultados e formata para o padrão longo
    df_resumo_final = pd.concat([df_summary, df_sem_aplicacoes])
    df_resumo_final.reset_index(inplace=True)
    df_resumo_final = df_resumo_final.rename(columns={'index': 'Grupo'})
    
    return df_resumo_final.melt(
        id_vars=['Grupo'], 
        var_name='MesNum', 
        value_name='Valor'
    )
