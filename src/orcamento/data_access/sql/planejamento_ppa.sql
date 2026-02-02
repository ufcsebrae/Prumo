-- src/orcamento/data_access/sql/planejamento_ppa.sql
-- VERSÃO FINAL COM OS NOMES CORRETOS DAS COLUNAS E ALIASES

SELECT
    "[PPA].[PPA com Fotografia].[Descrição de PPA com Fotografia].[MEMBER_CAPTION]" AS "PPA com Fotografia",
    "[Unidade Organizacional de Ação].[Unidade Organizacional de Ação].[Nome de Unidade Organizacional de Ação].[MEMBER_CAPTION]" AS "Unidade Organizacional",
    "[Iniciativa].[Iniciativas].[Iniciativa].[MEMBER_CAPTION]" AS "Iniciativa",
    "[Ação].[Ação].[Nome de Ação].[MEMBER_CAPTION]" AS "Ação",
    "[Natureza Orçamentária].[Código Estruturado 4 nível].[Código Estruturado 4 nível].[MEMBER_CAPTION]" AS "Código Natureza",
    "[Natureza Orçamentária].[Descrição de Natureza 4 nível].[Descrição de Natureza 4 nível].[MEMBER_CAPTION]" AS "Descrição Natureza",
    "[Tempo].[Ano].[Número Ano].[MEMBER_CAPTION]" AS "Ano",
    "[Tempo].[Mês].[Número Mês].[MEMBER_CAPTION]" AS "Mês",
    "[ValorAjustado]" AS "Valor"
FROM
    dbo.FatoAjustadoNacional
WHERE
    -- Usa o nome completo e complexo da coluna no filtro
    "[PPA].[PPA com Fotografia].[Descrição de PPA com Fotografia].[MEMBER_CAPTION]" = :ppa_filtro
    AND "[Tempo].[Ano].[Número Ano].[MEMBER_CAPTION]" = :ano_filtro;

