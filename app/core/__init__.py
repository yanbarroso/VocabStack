"""
Core - Configurações centrais da aplicação
"""

from app.db.database import DatabaseManager
from app.services.processors import LanguageProcessor

# Idioma padrão da aplicação.
# Atualmente o projeto processa exclusivamente textos em francês.
# Para adicionar suporte a outros idiomas no futuro, altere este valor
# e certifique-se de instalar o modelo spaCy correspondente:
#   python -m spacy download fr_core_news_sm  (francês - atual)
#   python -m spacy download en_core_web_sm   (inglês)
#   python -m spacy download pt_core_news_sm  (português)
DEFAULT_LANG = "fr"

# Nome por extenso do idioma, usado ao salvar no banco de dados.
# Deve estar em sincronia com DEFAULT_LANG.
DEFAULT_LANG_NAME = "french"

# Inicializar instâncias globais
db = DatabaseManager()
processor = LanguageProcessor(DEFAULT_LANG)

__all__ = ["db", "processor", "DEFAULT_LANG", "DEFAULT_LANG_NAME"]
