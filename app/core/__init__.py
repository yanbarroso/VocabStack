"""
Core - Configurações centrais da aplicação
"""

from app.db.database import DatabaseManager
from app.services.processors import LanguageProcessor

# Inicializar instâncias globais
db = DatabaseManager()
processor = LanguageProcessor("fr")

__all__ = ["db", "processor"]
