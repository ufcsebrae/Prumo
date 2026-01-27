import logging
import sys

def setup_logging() -> None:
    """Configura o sistema de logging para a aplicação."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
            # Para salvar logs em arquivo, descomente a linha abaixo:
            # logging.FileHandler("relatorio_financeiro.log")
        ]
    )
    # Reduz o ruído de bibliotecas muito verbosas, se necessário
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
