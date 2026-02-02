-- Retorna os dados de despesa em formato longo (normalizado) para um ano específico.
-- O parâmetro de ano será preenchido pela aplicação Python.

SELECT
    UPPER(DESCNVL3) AS 'Grupo',
    MONTH(DATA) AS 'MesNum',
    SUM(VALOR) AS 'Valor'
FROM
    FatoFechamento_v2
WHERE
    YEAR(DATA) = :year
    AND DESCNVL1 IN ('DESPESAS', 'DESPESAS EXCLUSIVAS DO ORÇAMENTO')
GROUP BY
    DESCNVL3,
    MONTH(DATA)
ORDER BY
    Grupo, MesNum;
