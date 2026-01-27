-- Retorna os dados de receita em formato longo (normalizado) para um ano específico.
-- O parâmetro :year será preenchido pela aplicação Python.
SELECT
    CASE WHEN UPPER(DESCNVL4) = 'CONTRIBUIÇÃO SOCIAL DO NACIONAL(CSN)' THEN 'CONTRIBUIÇÃO SOCIAL DO NACIONAL (CSN)' ELSE UPPER(DESCNVL3) END AS 'Grupo',
    MONTH(DATA) AS 'MesNum',
    SUM(VALOR) AS 'Valor'
FROM
    FatoFechamento_v2
WHERE
    YEAR(DATA) = :year
    AND DESCNVL1 IN ('RECEITAS', 'RECEITAS EXCLUSIVAS DO ORÇAMENTO')
GROUP BY
    DESCNVL4,
    DESCNVL3,
    MONTH(DATA)
ORDER BY
    Grupo, MesNum;
