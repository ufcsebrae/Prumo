-- src/orcamento/data_access/sql/planejamento_despesas.sql
-- Busca as despesas planejadas e padroniza as colunas para unificação.

SELECT
    [Descrio_de_PPA_com_Fotografia] AS "PPA com Fotografia",
    [Nome_de_Unidade_Organizacional_de_Ao]AS "Unidade Organizacional",
    [Iniciativa]AS "Iniciativa",
    [Nome_de_Ao] AS "Ação",
    [Cdigo_Estruturado_4_nvel] AS "Código Natureza",
    [Descrio_de_Natureza_4_nvel] AS "Descrição Natureza",
    [Nmero_Ano] AS "Ano",
    [Nmero_Ms] AS "Mês",
    [ValorAjustado] AS "Valor"
FROM
    dbo.FatoAjustadoNacional
WHERE
    [Descrio_de_PPA_com_Fotografia] = :ppa_filtro
    AND [Nmero_Ano] = :ano_filtro;
