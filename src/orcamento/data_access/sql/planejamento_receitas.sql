-- src/orcamento/data_access/sql/planejamento_receitas.sql
-- Busca as receitas planejadas e padroniza as colunas para unificação.

SELECT
    [Descrio_de_PPA_com_Fotografia] AS "PPA com Fotografia",
    NULL AS "Unidade Organizacional",
    NULL AS "Iniciativa",
    NULL AS "Ação",
    [Cdigo_Estruturado_4_nvel] AS "Código Natureza",
    [Descrio_de_Natureza_4_nvel] AS "Descrição Natureza",
    [Nmero_Ano] AS "Ano",
    [Nmero_Ms] AS "Mês",
    [ValorAjustado] AS "Valor"
FROM
    [FatoAjustadoNacional_receita]

WHERE
    -- Mantém os mesmos filtros para consistência
    [Descrio_de_PPA_com_Fotografia] = :ppa_filtro
    AND [Nmero_Ano] = :ano_filtro;
