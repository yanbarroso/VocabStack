"""
Models - Estruturas de dados e tipos
"""

from dataclasses import dataclass
from typing import Dict

__all__ = ["ProcessamentoResult", "WorkMetadata"]


@dataclass
class ProcessamentoResult:
    """Resultado do processamento de um arquivo"""
    titulo: str
    tipo: str
    idioma: str
    total_count: int
    word_frequencies: Dict[str, int]


@dataclass
class WorkMetadata:
    """Metadados de uma obra"""
    titulo: str
    total: int
    data: str
