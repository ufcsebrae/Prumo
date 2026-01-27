_____  _____  _    _  __  __   ____  
 |  __ \|  __ \| |  | ||  \/  | / __ \ 
 | |__) | |__) | |  | || \  / || |  | |
 |  ___/|  _  /| |  | || |\/| || |  | |
 | |    | | \ \| |__| || |  | || |__| |
 |_|    |_|  \_\\____/ |_|  |_| \____/ 
                                       
     ALINHAMENTO E ANÁLISE ORÇAMENTÁRIA


# PRUMO - Sistema de Relatórios de Orçamento

Este projeto automatiza a geração e o envio de relatórios financeiros (receitas, despesas e superávit/déficit). O sistema extrai dados de um banco de dados SQL Server, processa-os com `pandas` e envia um relatório consolidado por e-mail via Microsoft Outlook.

O código segue boas práticas de desenvolvimento, com uma arquitetura modular, configurações externalizadas e um fluxo de trabalho claro.

## Arquitetura

O projeto é dividido nos seguintes módulos principais:

-   **`src/orcamento/core`**: Contém a lógica central da aplicação, como a gestão de configurações (`.env`) e a configuração de logging.
-   **`src/orcamento/data_access`**: Responsável por toda a interação com o banco de dados. Contém a lógica de conexão (`database.py`) e as consultas SQL (`sql/`).
-   **`src/orcamento/processing`**: Contém a lógica de negócio principal, onde os cálculos financeiros (ex: superávit) são realizados.
-   **`src/orcamento/reporting`**: Responsável pela camada de apresentação. Formata os dados para exibição (`formatting.py`), renderiza templates HTML e envia os e-mails (`email_sender.py`).
-   **`main.py`**: O ponto de entrada que orquestra todo o fluxo, desde a extração de dados até o envio do relatório.

## Instalação

### 1. Pré-requisitos

-   Python 3.9 ou superior.
-   Microsoft Outlook instalado e configurado na máquina de execução.
-   Acesso de rede ao banco de dados SQL Server de destino.
-   Driver ODBC para SQL Server instalado (ex: "ODBC Driver 18 for SQL Server").

### 2. Crie um Ambiente Virtual

É uma boa prática isolar as dependências do projeto.

```bash
# Crie o ambiente
python -m venv venv

# Ative o ambiente
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instale as Dependências

As dependências são gerenciadas pelo arquivo `pyproject.toml`. Use `pip` para instalá-las.

```bash
pip install -e .
```

O comando `-e .` instala o projeto em modo "editável", o que é ótimo para desenvolvimento.

### 4. Configure o Ambiente

1.  Renomeie o arquivo `env.example` (se houver) para `.env` na raiz do projeto.
2.  Abra o arquivo `.env` e preencha as variáveis com os dados corretos para o seu ambiente:

    ```dotenv
    DB_SERVERNAME="seu-servidor-sql"
    DB_DBNAME="seu-banco-de-dados"
    DB_DRIVER="ODBC Driver 18 for SQL Server"
    MAIL_RECIPIENT="destinatario@exemplo.com.br"
    MAIL_SUBJECT_PREFIX="Seu Prefixo de Assunto"
    ```

## Como Executar

Com o ambiente virtual ativado e o arquivo `.env` configurado, execute o script principal:

```bash
python src/orcamento/main.py
```

O script irá executar todo o processo e, se bem-sucedido, enviará o e-mail e registrará as etapas no console.

## Manutenção

-   **Para alterar as consultas SQL**: Edite os arquivos em `src/orcamento/data_access/sql/`. Mantenha as queries retornando dados brutos.
-   **Para alterar o template do e-mail**: Modifique o arquivo `src/orcamento/reporting/templates/email_template.html`.
-   **Para alterar a lógica de cálculo**: Ajuste as funções em `src/orcamento/processing/financial_analysis.py`.
-   **Para alterar a formatação dos números ou tabelas**: Modifique as funções em `src/orcamento/reporting/formatting.py`.
