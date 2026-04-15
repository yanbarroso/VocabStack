"""
Configuração pytest - Fixtures compartilhadas entre testes
"""

import pytest
import tempfile
import os
from pathlib import Path

from app.api import app
from app.db import DatabaseManager
from app.services import LanguageProcessor
from app.utils import ReaderFactory


# ============================================================================
# FIXTURES DE BANCO DE DADOS
# ============================================================================

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário em memória para testes"""
    db = DatabaseManager(':memory:')
    yield db
    # Cleanup automático (memória é liberada)


@pytest.fixture
def db_with_sample_data(temp_db):
    """BD com dados de exemplo"""
    # Inserir dados de exemplo
    temp_db.salvar_processamento(
        titulo="Le Petit Prince",
        tipo="EPUB",
        idioma="fr",
        total=14393,
        freq_dict={"prince": 157, "petit": 98, "homme": 45}
    )
    
    temp_db.salvar_processamento(
        titulo="Alice in Wonderland",
        tipo="TXT",
        idioma="en",
        total=26920,
        freq_dict={"alice": 386, "said": 412, "wondered": 12}
    )
    
    return temp_db


# ============================================================================
# FIXTURES DE SERVICES
# ============================================================================

@pytest.fixture
def processor_fr():
    """Processador em francês"""
    return LanguageProcessor('fr')


@pytest.fixture
def processor_en():
    """Processador em inglês"""
    return LanguageProcessor('en')


# ============================================================================
# FIXTURES DE TEXTO
# ============================================================================

@pytest.fixture
def sample_text_fr():
    """Texto de exemplo em francês"""
    return """
    Le petit prince est un prince qui habite une très petite planète. 
    Il aime regarder les couchers de soleil. 
    Un jour, il quitte sa planète pour voyager dans l'univers.
    """


@pytest.fixture
def sample_text_en():
    """Texto de exemplo em inglês"""
    return """
    Once upon a time there was a girl named Alice.
    Alice was sitting by the riverbank with her sister.
    She felt very sleepy and wondered if she should follow the white rabbit.
    """


@pytest.fixture
def empty_text():
    """Texto vazio"""
    return ""


# ============================================================================
# FIXTURES DE ARQUIVOS
# ============================================================================

@pytest.fixture
def temp_txt_file():
    """Cria arquivo TXT temporário"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("This is a test file with some content.\n")
        f.write("It has multiple lines.\n")
        f.write("And it should be readable.\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_invalid_file():
    """Cria arquivo com extensão não suportada"""
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


# ============================================================================
# MARCADORES CUSTOMIZADOS
# ============================================================================

def pytest_configure(config):
    """Registrar marcadores customizados"""
    config.addinivalue_line(
        "markers", "api: marca testes de API endpoints"
    )
    config.addinivalue_line(
        "markers", "service: marca testes de services"
    )
    config.addinivalue_line(
        "markers", "database: marca testes de banco de dados"
    )
    config.addinivalue_line(
        "markers", "utils: marca testes de utilitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )


# ============================================================================
# PARAMETRIZAÇÕES COMUNS
# ============================================================================

SUPPORTED_FORMATS = ['.txt']  # Por enquanto só TXT fácil de testar
UNSUPPORTED_FORMATS = ['.xyz', '.abc', '.doc']
VALID_LANGUAGES = ['fr', 'en']
INVALID_LANGUAGES = ['xx', 'zz', '123']
