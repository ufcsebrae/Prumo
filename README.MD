# Projeto Prumo: Geração de Relatórios de Orçamento

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

## 🎯 Descrição

O **Projeto Prumo** é um pipeline de dados automatizado para a geração de relatórios financeiros que consolidam múltiplas fontes de dados: valores **executados** do banco de dados, previsões manuais via arquivos CSV e o **planejamento** orçamentário extraído de tabelas SQL.

A aplicação gera um e-mail em HTML, formatado profissionalmente e com design responsivo, contendo um sumário executivo (KPIs) e tabelas detalhadas de Receitas, Despesas e o resultado de Superávit/Déficit.

## 🏛️ Arquitetura

O projeto segue uma arquitetura modular para separação de responsabilidades, facilitando a manutenção e a evolução do código.

-   **`src/orcamento/core`**: Contém a lógica central da aplicação, como a gestão de configurações (`.env`) e a inicialização do sistema de logs.
-   **`src/orcamento/data_access`**: Responsável por toda a interação com bancos de dados. Contém a lógica de conexão e os scripts SQL em arquivos `.sql` dedicados.
-   **`src/orcamento/processing`**: O cérebro do sistema. Contém a lógica de negócio para combinar as diferentes fontes de dados e aplicar as regras de prioridade de previsão.
-   **`src/orcamento/reporting`**: Camada de apresentação. Formata os dados para exibição, estiliza as tabelas e renderiza o template de e-mail.
-   **`main.py`**: O ponto de entrada que orquestra todo o fluxo, da extração de dados ao envio do relatório.

## 🧠 Fluxo de Dados e Lógica de Negócio

O relatório final é construído com base em uma hierarquia clara de fontes de dados para cada categoria (`Grupo`) e mês.

1.  **Valor Executado:** Se existe um valor executado vindo do banco de dados, ele tem **prioridade máxima** e é o único valor exibido.
2.  **Valor de Previsão:** Se não há valor executado, o sistema busca um valor de previsão seguindo esta ordem de prioridade:
    *   **Prioridade 1: Previsão Manual (CSV):** Um valor inserido no arquivo `previsao_despesas.csv` ou `previsao_receitas.csv` sobrescreve qualquer outra previsão.
    *   **Prioridade 2: Previsão do Sistema (SQL):** Se não há previsão manual, o sistema utiliza o valor do planejamento orçamentário vindo das tabelas `FatoAjustadoNacional` e `orcado_receitas_cenario`.
    *   **Prioridade 3: Projeção Calculada:** Se existe um valor executado, mas não há previsão manual, a previsão é calculada como `Planejado do Sistema - Executado`.

## 🛠️ Pré-requisitos

Para que o projeto funcione em uma nova máquina, os seguintes componentes são **obrigatórios**:

1.  **Python:** Versão 3.9 ou superior.
2.  **Git:** Para clonar o repositório.
3.  **Microsoft Outlook:** O aplicativo Desktop deve estar instalado e configurado, pois o envio de e-mail é feito através dele.
4.  **Drivers Microsoft:**
    *   **ODBC Driver for SQL Server:** Essencial para a conexão com o banco de dados SQL. Recomenda-se a versão 17 ou 18. [Link para Download](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento em uma nova máquina.

1.  **Clone o Repositório**
    ```bash
    git clone https://github.com/ufcsebrae/Prumo.git
    cd Prumo
    ```

2.  **Crie e Ative o Ambiente Virtual**
    Isso isola as dependências do projeto. Recomenda-se o uso do PowerShell no Windows.
    ```powershell
    # Crie o ambiente
    python -m venv .venv

    # Ative o ambiente
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Instale as Dependências**
    As dependências são gerenciadas pelo `pyproject.toml`. O comando a seguir instala tudo o que é necessário.
    ```bash
    pip install -e .
    ```

4.  **Configure as Variáveis de Ambiente**
    Crie um arquivo chamado `.env` na raiz do projeto. Ele **não** deve ser enviado para o Git. Copie o conteúdo abaixo e preencha com os dados corretos do seu ambiente.

    ```dotenv
    # .env

    # -- Conexão SQL Server (Executado e Planejado) --
    DB_SERVERNAME="spsvsql39"
    DB_DBNAME="FINANCA"
    DB_DRIVER="ODBC Driver 18 for SQL Server"

    # -- Filtros para a Query de Planejamento (PPA) --
    PPA_FILTRO="PPA 2026 - 2026/Jan"
    ANO_FILTRO=2026

    # -- Configurações de E-mail --
    MAIL_RECIPIENT="destinatario1@sebraesp.com.br;destinatario2@sebraesp.com.br"
    MAIL_SUBJECT_PREFIX="Prévia Orçamento"
    ```

## 📁 Estrutura dos Arquivos de Dados

Na raiz do projeto, deve existir uma pasta `forecast_data`. Ela contém os arquivos CSV que alimentam a lógica de previsão.

#### `de_para_planejamento.csv`
Este arquivo é **crucial** e funciona como uma ponte entre os dados do sistema de planejamento e os grupos de execução.
-   **Formato:** Deve ter 3 colunas, com o seguinte cabeçalho: `Natureza_Planejamento,Grupo_Execucao,Tipo_Fluxo`
-   **Exemplo:**
    ```csv
    Natureza_Planejamento,Grupo_Execucao,Tipo_Fluxo
    Serviços Especializados,SERVIÇOS PROFISSIONAIS E CONTRATADOS,Despesa
    Receita de Produtos,OUTRAS RECEITAS OPERACIONAIS,Receita
    ```

#### `previsao_receitas.csv` e `previsao_despesas.csv`
Estes arquivos servem para o *override* manual das previsões.
-   **Formato:** Devem ter 3 colunas, com o seguinte cabeçalho: `Grupo,Mes,Valor`
-   **Exemplo:**
    ```csv
    Grupo,Mes,Valor
    SERVIÇOS PROFISSIONAIS E CONTRATADOS,fev,5200000
    ```

## ▶️ Como Executar

Com o ambiente virtual ativado (`(.venv)`) e os arquivos `.env` e de dados configurados, execute o script principal a partir da raiz do projeto:

```bash
python -m orcamento.main
```
O script registrará todas as etapas do processo no console e, ao final, enviará o e-mail com os relatórios.

## 🔧 Manutenção

-   **Alterar Queries:** Edite os arquivos na pasta `src/orcamento/data_access/sql/`.
-   **Ajustar Lógica de Negócio:** Modifique as funções no arquivo `src/orcamento/processing/financial_analysis.py`.
-   **Mudar Layout do E-mail:** Edite o template em `src/orcamento/reporting/templates/email_template.html`.
-   **Mudar Cores:** Altere as variáveis no arquivo `src/orcamento/core/config.py` na classe `ColorSettings`.
