## 📁 Estrutura do Projeto - VocabStack

```
vocabstack/
├── app/                          # Pacote principal da aplicação
│   ├── __init__.py              # Metadados da aplicação
│   ├── api/                     # Camada de API (FastAPI)
│   │   ├── __init__.py          # Cria instância FastAPI
│   │   └── routes.py            # Rotas e endpoints
│   ├── core/                    # Configurações centrais
│   │   └── __init__.py          # Instâncias globais (db, processor)
│   ├── db/                      # Camada de banco de dados
│   │   ├── __init__.py          # Exporta DatabaseManager
│   │   └── database.py          # Implementação SQLite
│   ├── models/                  # Modelos de dados
│   │   └── __init__.py          # Dataclasses (ProcessamentiResult, WorkMetadata)
│   ├── services/                # Lógica de negócio
│   │   ├── __init__.py          # Exporta LanguageProcessor
│   │   └── processors.py        # Processamento NLP
│   ├── utils/                   # Utilitários
│   │   ├── __init__.py          # Exporta readers
│   │   └── readers.py           # Leitura de arquivos (EPUB, PDF, TXT)
│   └── static/                  # Arquivos estáticos (futuramente)
├── tests/                       # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py             # Configurações de testes
│   ├── test_api.py             # Testes da API
│   └── test_services.py        # Testes de services
├── data/                        # Arquivos de dados
│   └── vocabstack.db           # Banco de dados SQLite
├── main_api.py                  # Ponto de entrada da API
├── index.html                   # Frontend
├── requirements.txt             # Dependências
└── README.md
```

## 🏗️ Arquitetura - Layers

### 1. **API Layer** (`app/api/`)
- Responsável por: Rotas HTTP, validação de requisições, respostas
- Depende de: Services, Models
- NÃO depende de: DB diretamente

```python
# ✅ BOM
leitor = ReaderFactory.get_reader(caminho)
stats = processor.get_detailed_stats(texto)

# ❌ RUIM
db.connect()  # API não fala com BD diretamente
```

### 2. **Services Layer** (`app/services/`)
- Responsável por: Lógica de negócio, processamento
- Exemplos: `LanguageProcessor`
- Reutilizável: Pode ser usado em CLI, API, Queue workers

### 3. **Utils Layer** (`app/utils/`)
- Responsável por: Ferramentas auxiliares, leitura de dados
- Exemplos: `ReaderFactory`, parsers
- Stateless e reutilizável

### 4. **Data Layer** (`app/db/`)
- Responsável por: Acesso ao banco de dados
- Interface: `DatabaseManager`
- Encapsula queries SQL

### 5. **Models Layer** (`app/models/`)
- Responsável por: Estruturas de dados
- Tipos: Dataclasses, enums
- Compartilhadas entre layers

### 6. **Core Layer** (`app/core/`)
- Responsável por: Configurações globais
- Singleton patterns: Instâncias globais reutilizáveis

## ✅ Benefícios desta Arquitetura

### Desacoplamento
```python
# Mudar DB sem afetar API
class PostgresManager(DatabaseManager):  # Herança
    pass

# Mudar processador sem afetar API
class SpacyEnglishProcessor(LanguageProcessor):
    pass
```

### Testabilidade
```python
# Mock services em testes
@pytest.fixture
def mock_processor():
    return MagicMock(spec=LanguageProcessor)

def test_upload(mock_processor):
    # Testa sem NLP real
    pass
```

### Modularidade
```python
# Use em CLI
from app.services import LanguageProcessor
from app.utils import ReaderFactory

# Reutilize em background jobs
from app.db import DatabaseManager
```

### Escalabilidade
```
# Adicione novos módulos sem quebrar existentes
app/
├── queue/          # Celery para jobs
├── cache/          # Redis cache
├── notifications/  # Email/Slack
```

## 🔄 Fluxo de Dados

```
Frontend (HTTP)
    ↓
API Routes (app/api/routes.py)
    ↓
Services (app/services/processors.py)
    ↓
Utils (app/utils/readers.py)
    ↓
Data Layer (app/db/database.py)
    ↓
SQLite (data/vocabstack.db)
```

## 📝 Adicionando Novos Recursos

### Novo Endpoint
```python
# 1. Criar em app/api/routes.py
@router.get("/novo-endpoint")
async def novo_endpoint():
    from app.core import db
    return db.fazer_algo()

# 2. Testar em tests/test_api.py
```

### Novo Leitor de Arquivo
```python
# 1. Criar em app/utils/readers.py
class DocxReader(BaseReader):
    def extract_text(self, file_path: str) -> str:
        # Implementação
        pass

# 2. Registrar
from app.utils import ReaderFactory
ReaderFactory.registrar_reader('.docx', DocxReader)

# 3. Testar
```

### Novo Processador
```python
# 1. Criar em app/services/processors.py
class EnglishProcessor(LanguageProcessor):
    def __init__(self):
        super().__init__('en')

# 2. Usar na API
processor_en = EnglishProcessor()
```

## 🧪 Executando Testes

```bash
# Instalar pytest
pip install pytest pytest-asyncio pytest-cov

# Rodar testes
pytest

# Com cobertura
pytest --cov=app

# Teste específico
pytest tests/test_api.py::test_upload
```

## 🚀 Iniciando a Aplicação

```bash
# Desenvolvimento
uvicorn app.api:app --reload

# Produção
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Dependências Entre Módulos

```
api/routes.py
├── → services/processors.py
├── → utils/readers.py
├── → db/database.py
└── → models/__init__.py

core/__init__.py
├── → db/database.py
└── → services/processors.py

db/database.py (independente)

utils/readers.py (independente)

services/processors.py (independente)
```

## ⚠️ Regras de Ouro

1. **Imports em uma direção**: Apenas de baixo para cima
   - ✅ `api` → `services` → `db`
   - ❌ `db` → `api` (circular)

2. **Cada camada faz uma coisa**: Single Responsibility
   - API: receber requisições
   - Services: lógica
   - Utils: helpers
   - DB: persistência

3. **Testes para cada camada**:
   - Unit (services)
   - Integration (api + services)
   - E2E (completo)

## 🔐 Segurança

- ✅ Validação de entrada na API
- ✅ Tratamento de exceções
- ✅ Type hints para segurança de tipo
- ✅ Logs de erro
- ✅ Isolamento de dados temporários

---

**Versão**: 1.0.0  
**Última atualização**: 2026-04-15
