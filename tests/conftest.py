"""
Configuração pytest - Fixtures compartilhadas entre testes
"""

import pytest
import tempfile
import os

from app.api import app
from app.db import DatabaseManager
from app.services import LanguageProcessor


# ============================================================================
# OVERRIDE DE DEPENDÊNCIAS — isola testes do banco real
# ============================================================================

@pytest.fixture(autouse=True)
def _usar_banco_em_memoria(monkeypatch):
    """
    Substitui a instância global `db` em app.core e app.api.routes por um
    DatabaseManager em memória antes de cada teste, garantindo isolamento
    total do banco de dados de produção (data/vocabstack.db).
    """
    db_teste = DatabaseManager(':memory:')

    import app.core as core_module
    import app.api.routes as routes_module

    monkeypatch.setattr(core_module, 'db', db_teste)
    monkeypatch.setattr(routes_module, 'db', db_teste)

    yield db_teste


# ============================================================================
# FIXTURES DE BANCO DE DADOS
# ============================================================================

@pytest.fixture
def temp_db():
    """Banco de dados temporário em memória para testes unitários de DB."""
    return DatabaseManager(':memory:')


@pytest.fixture
def db_with_sample_data(temp_db):
    """BD em memória pré-populado com dados de exemplo."""
    temp_db.salvar_processamento(
        titulo="Le Petit Prince",
        tipo="EPUB",
        idioma="french",
        total=14393,
        freq_dict={"prince": 157, "petit": 98, "homme": 45},
    )
    temp_db.salvar_processamento(
        titulo="Alice in Wonderland",
        tipo="TXT",
        idioma="english",
        total=26920,
        freq_dict={"alice": 386, "said": 412, "wondered": 12},
    )
    return temp_db


# ============================================================================
# FIXTURES DE SERVICES
# ============================================================================

@pytest.fixture
def processor_fr():
    """Processador NLP em francês."""
    return LanguageProcessor('fr')


@pytest.fixture
def processor_en():
    """Processador NLP em inglês."""
    return LanguageProcessor('en')


# ============================================================================
# FIXTURES DE TEXTO
# ============================================================================

@pytest.fixture
def sample_text_fr():
    """Texto de exemplo em francês."""
    return (
        "Le petit prince est un prince qui habite une très petite planète. "
        "Il aime regarder les couchers de soleil. "
        "Un jour, il quitte sa planète pour voyager dans l'univers."
    )


@pytest.fixture
def sample_text_en():
    """Texto de exemplo em inglês."""
    return (
        "Once upon a time there was a girl named Alice. "
        "Alice was sitting by the riverbank with her sister. "
        "She felt very sleepy and wondered if she should follow the white rabbit."
    )


@pytest.fixture
def empty_text():
    """Texto vazio."""
    return ""


# ============================================================================
# FIXTURES DE ARQUIVOS
# ============================================================================

@pytest.fixture
def temp_txt_file():
    """Arquivo TXT temporário com conteúdo válido."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("This is a test file with some content.\n")
        f.write("It has multiple lines.\n")
        f.write("And it should be readable.\n")
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def temp_invalid_file():
    """Arquivo com extensão não suportada."""
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


# ============================================================================
# CONSTANTES DE PARAMETRIZAÇÃO
# ============================================================================

SUPPORTED_FORMATS = ['.txt']
UNSUPPORTED_FORMATS = ['.xyz', '.abc', '.doc']
VALID_LANGUAGES = ['fr', 'en']
INVALID_LANGUAGES = ['xx', 'zz', '123']


# ============================================================================
# MARCADORES CUSTOMIZADOS
# ============================================================================

def pytest_configure(config):
    """Registrar marcadores customizados."""
    markers = [
        "api: marca testes de API endpoints",
        "service: marca testes de services",
        "database: marca testes de banco de dados",
        "utils: marca testes de utilitários",
        "integration: marca testes de integração",
        "slow: marca testes lentos",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
