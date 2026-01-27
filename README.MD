# Projeto Prumo: Geração de Relatórios de Orçamento

## Descrição

O **Projeto Prumo** é um sistema automatizado para a geração de relatórios financeiros (receitas, despesas e superávit/déficit). A aplicação extrai dados de um banco de dados SQL Server, realiza o processamento e a análise com a biblioteca `pandas`, e envia um relatório consolidado e formatado por e-mail via Microsoft Outlook.

O projeto foi estruturado seguindo boas práticas de desenvolvimento de software, com uma arquitetura modular, configurações externalizadas e um fluxo de trabalho claro e manutenível.

## Arquitetura

O projeto é dividido nos seguintes módulos principais:

-   **`src/orcamento/core`**: Contém a lógica central da aplicação, como a gestão de configurações (a partir do arquivo `.env`) e a configuração de *logging*.
-   **`src/orcamento/data_access`**: Responsável por toda a interação com o banco de dados. Contém a lógica de conexão (`database.py`) e as consultas SQL em arquivos `.sql` dedicados.
-   **`src/orcamento/processing`**: Contém a lógica de negócio principal, onde os cálculos financeiros (ex: superávit, totais) são realizados.
-   **`src/orcamento/reporting`**: Responsável pela camada de apresentação. Formata os dados para exibição (`formatting.py`), renderiza templates HTML e envia os e-mails (`email_sender.py`).
-   **`main.py`**: O ponto de entrada que orquestra todo o fluxo, desde a extração de dados até o envio do relatório.

## Pré-requisitos

Antes de executar o projeto, garanta que os seguintes softwares estão instalados e configurados:

-   Python 3.9 ou superior.
-   Git.
-   Microsoft Outlook instalado e configurado na máquina de execução.
-   Acesso de rede ao banco de dados SQL Server de destino.
-   Driver ODBC para SQL Server instalado (ex: "ODBC Driver 18 for SQL Server").

## Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

1.  **Clone o Repositório**
    ```bash
    git clone https://github.com/ufcsebrae/Prumo.git
    cd Prumo
    ```

2.  **Crie e Ative o Ambiente Virtual**
    É uma boa prática isolar as dependências do projeto.
    ```powershell
    # Crie o ambiente
    python -m venv .venv

    # Ative o ambiente (usando PowerShell)
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Instale as Dependências**
    As dependências são gerenciadas pelo arquivo `pyproject.toml`. Use `pip` para instalá-las em modo editável.
    ```bash
    pip install -e .
    ```

4.  **Configure as Variáveis de Ambiente**
    Crie um arquivo chamado `.env` na raiz do projeto. Você pode copiar o exemplo abaixo e preencher com seus dados. **Este arquivo nunca deve ser enviado para o repositório Git.**

    ```dotenv
    # .env

    # Configurações do Banco de Dados
    DB_SERVERNAME="spsvsql39"
    DB_DBNAME="FINANCA"
    DB_DRIVER="ODBC Driver 18 for SQL Server"

    # Configurações de E-mail
    MAIL_RECIPIENT="usuario@sebraesp.com.br;destinatario2@sebraesp.com.br"
    MAIL_SUBJECT_PREFIX="Prévia Orçamento"
    ```

## Como Executar

Com o ambiente virtual ativado (`(.venv)`) e o arquivo `.env` configurado, execute o script principal a partir da raiz do projeto:

```bash
python -m orcamento.main
```

O script irá registrar todas as etapas do processo no console e, se bem-sucedido, enviará o e-mail com os relatórios.

## Manutenção

-   **Para alterar as consultas SQL**: Edite os arquivos em `src/orcamento/data_access/sql/`.
-   **Para alterar o template do e-mail**: Modifique o arquivo `src/orcamento/reporting/templates/email_template.html`.
-   **Para alterar a lógica de cálculo**: Ajuste as funções em `src/orcamento/processing/financial_analysis.py`.
-   **Para alterar a formatação dos números ou tabelas**: Modifique as funções em `src/orcamento/reporting/formatting.py`.
