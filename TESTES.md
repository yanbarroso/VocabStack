# Guia de Testes - Test Driven Development (TDD)

## 📋 Visão Geral

Este projeto implementa **Test Driven Development (TDD)** como prática padrão, seguindo o ciclo **Red-Green-Refactor**.

### Ciclo TDD

```
┌─────────────────────────────────┐
│  1. RED: Escrever teste que falha │
├─────────────────────────────────┤
│  2. GREEN: Fazer teste passar    │
├─────────────────────────────────┤
│  3. REFACTOR: Melhorar código    │
└─────────────────────────────────┘
```

---

## 🏗️ Estrutura de Testes

### Organização por Camada

```
tests/
├── conftest.py              # Configuração e fixtures compartilhadas
├── test_api.py             # Testes dos endpoints (API layer)
├── test_services.py        # Testes da lógica de negócio (Services layer)
├── test_db.py              # Testes do banco de dados (DB layer)
├── test_utils.py           # Testes dos utilitários (Utils layer)
└── test_integration.py     # Testes end-to-end (integração entre camadas)
```

### Total de Testes Implementados

- **API Tests**: 25+ testes
- **Services Tests**: 35+ testes
- **Database Tests**: 30+ testes
- **Utils Tests**: 25+ testes
- **Integration Tests**: 20+ testes

**Total**: ~135 testes cobrindo todo o pipeline

---

## 🔧 Executando os Testes

### Rodar todos os testes

```bash
pytest
# ou com verbosidade
pytest -v
```

### Rodar testes por categoria (usando markers)

```bash
# Testes da API
pytest -m api

# Testes de serviços
pytest -m service

# Testes de banco de dados
pytest -m database

# Testes de utilitários
pytest -m utils

# Testes de integração
pytest -m integration

# Testes que usam async
pytest -m asyncio
```

### Rodar arquivo específico

```bash
pytest tests/test_api.py
pytest tests/test_services.py
pytest tests/test_db.py
pytest tests/test_utils.py
pytest tests/test_integration.py
```

### Rodar com cobertura de código

```bash
pytest --cov=app --cov-report=html
# Abre relatório em htmlcov/index.html
```

### Rodar apenas testes rápidos (sem slow)

```bash
pytest -m "not slow"
```

---

## 📁 Fixtures (conftest.py)

Fixtures são funções reutilizáveis que configurar o ambiente para testes.

### Database Fixtures

```python
@pytest.fixture
def temp_db():
    """Banco de dados em memória limpo para cada teste"""
    # Cria um novo banco SQLite em :memory:
    
@pytest.fixture
def db_with_sample_data():
    """Banco pré-preenchido com dados de exemplo"""
    # Inclui uma obra com palavras de teste
```

### Processor Fixtures

```python
@pytest.fixture
def processor_fr():
    """LanguageProcessor em francês"""
    
@pytest.fixture
def processor_en():
    """LanguageProcessor em inglês"""
```

### Text Fixtures

```python
@pytest.fixture
def sample_text_fr():
    """Texto de amostra em francês"""
    # "Le petit prince est une œuvre extraordinaire..."
    
@pytest.fixture
def sample_text_en():
    """Texto de amostra em inglês"""
```

### File Fixtures

```python
@pytest.fixture
def temp_txt_file():
    """Arquivo TXT temporário para testes"""
    
@pytest.fixture
def temp_invalid_file():
    """Arquivo inválido para testes de erro"""
```

### API Client Fixtures

```python
@pytest.fixture
async def client():
    """AsyncClient pré-configurado para testes"""
    
@pytest.fixture
async def client_with_db():
    """AsyncClient com banco pré-preenchido"""
```

---

## 🧪 Padrões de Teste

### 1. Testes de Inicialização

Verifica se a classe/módulo inicializa corretamente.

```python
def test_language_processor_init(self):
    """Deve inicializar processador em francês"""
    proc = LanguageProcessor('fr')
    assert proc.lang_code == 'fr'
    assert proc.nlp is not None
    assert len(proc.stop_words) > 0
```

### 2. Testes de Entrada/Saída (Input/Output)

Verifica se a função processa entrada e retorna saída esperada.

```python
def test_get_detailed_stats(self, processor_fr):
    """Deve retornar dict com estatísticas"""
    stats = processor_fr.get_detailed_stats("le petit prince")
    
    assert isinstance(stats, dict)
    assert "total_count" in stats
    assert "word_frequencies" in stats
```

### 3. Testes de Edge Cases

Verifica comportamento em casos extremos.

```python
def test_empty_text_returns_zero_count(self, processor_fr):
    """Texto vazio deve retornar contagem zero"""
    stats = processor_fr.get_detailed_stats("")
    
    assert stats["total_count"] == 0
    assert stats["word_frequencies"] == {}
```

### 4. Testes de Erro

Verifica se erros são lançados corretamente.

```python
def test_unsupported_language_raises_error(self):
    """Deve lançar erro para idioma não suportado"""
    with pytest.raises(ValueError, match="não suportado"):
        LanguageProcessor('xx')
```

### 5. Testes de Integração

Verifica fluxos que envolvem múltiplas camadas.

```python
def test_file_read_process_store_retrieve(self, temp_db, processor_fr):
    """Fluxo completo: lê → processa → armazena → recupera"""
    # ... código complexo envolvendo 4 camadas
```

### 6. Testes Assincronos (async)

Para endpoints FastAPI que usam async/await.

```python
@pytest.mark.asyncio
async def test_health_endpoint(self, client):
    """Deve retornar status 200"""
    response = await client.get("/api/health")
    
    assert response.status_code == 200
```

---

## 🎯 Markers Personalizados

Markers permitem filtrar testes por categoria.

### Markers Disponíveis

- `@pytest.mark.api`: Testes de endpoints
- `@pytest.mark.service`: Testes de lógica de negócio
- `@pytest.mark.database`: Testes de banco de dados
- `@pytest.mark.utils`: Testes de utilitários
- `@pytest.mark.integration`: Testes end-to-end
- `@pytest.mark.asyncio`: Testes assincronos
- `@pytest.mark.slow`: Testes que demoram

### Exemplo de Uso

```bash
# Rodar testes rápidos
pytest -m "not slow"

# Rodar API tests que são rápidos
pytest -m "api and not slow"

# Rodar todos os testes, mostrando slow
pytest -v
```

---

## 📊 Cobertura de Código

### Checando cobertura

```bash
pytest --cov=app --cov-report=term-missing
```

### Gerando relatório HTML

```bash
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Objetivo de Cobertura

- **API Layer**: > 95%
- **Services Layer**: > 90%
- **DB Layer**: > 85%
- **Utils Layer**: > 80%
- **Geral**: > 85%

---

## 🔄 Ciclo de Desenvolvimento com TDD

### Processo Recomendado

#### 1️⃣ RED: Escrever Teste que Falha

```python
def test_nova_funcionalidade(self, processor):
    """Deve fazer X com entrada Y"""
    resultado = processor.nova_funcionalidade("entrada")
    
    assert resultado == "esperado"
```

```bash
pytest tests/test_services.py::TestNovaFuncionalidade::test_nova_funcionalidade
# FALHA ❌ (função ainda não existe)
```

#### 2️⃣ GREEN: Implementar Função

```python
def nova_funcionalidade(self, entrada: str) -> str:
    """Implementação mínima para passar no teste"""
    return "esperado"
```

```bash
pytest tests/test_services.py::TestNovaFuncionalidade::test_nova_funcionalidade
# PASSA ✅
```

#### 3️⃣ REFACTOR: Melhorar Código

```python
def nova_funcionalidade(self, entrada: str) -> str:
    """Implementação completa e otimizada"""
    # Código Production-Ready
    return self._processar(entrada)
```

```bash
pytest tests/test_services.py::TestNovaFuncionalidade::test_nova_funcionalidade
# AINDA PASSA ✅
```

---

## 🛠️ Adicionando Novos Testes

### Template: Adicionar Teste para Nova Feature

1. **Criar arquivo de teste** (ou usar existente)

```python
# tests/test_nova_feature.py
import pytest

@pytest.mark.nova_feature
class TestNovaFeature:
    """Testes para nova funcionalidade"""
```

2. **Definir o teste (RED)**

```python
def test_debe_fazer_algo(self, processor):
    """Deve fazer X com entrada Y"""
    resultado = processor.nova_func("input")
    assert resultado == "output_esperado"
```

3. **Rodar teste - deve FALHAR**

```bash
pytest tests/test_nova_feature.py -v
# FALHOU ❌ (esperado)
```

4. **Implementar no código (GREEN)**

Adicionar a função em `app/services/processors.py` ou módulo apropriado.

5. **Rodar teste - deve PASSAR**

```bash
pytest tests/test_nova_feature.py -v
# PASSOU ✅
```

6. **Refatorar ambos teste e código**

Melhorar para Production-Ready mantendo testes passando.

---

## 🚀 Boas Práticas

### ✅ Faça:

- ✅ Escrever testes ANTES do código (TDD)
- ✅ Um teste por conceito
- ✅ Usar nomes descritivos: `test_deve_*`
- ✅ Usar fixtures do `conftest.py`
- ✅ Testar happy path E edge cases
- ✅ Usar fixtures com `yield` para cleanup
- ✅ Documentar testes complexos
- ✅ Rodar testes frequentemente

### ❌ Evite:

- ❌ Escrever código sem testes
- ❌ Testes genéricos sem descrição clara
- ❌ Compartilhar estado entre testes
- ❌ Testes que dependem de ordem
- ❌ Mock desnecessário (prefer real objects)
- ❌ Ignorar testes com `@pytest.mark.skip`
- ❌ Testes muito lentos (> 1s cada)
- ❌ Deixar testes pendentes indefinidamente

---

## 📈 Monitorando Qualidade

### Pre-commit Hook (Opcional)

Adicionar ao `.git/hooks/pre-commit`:

```bash
#!/bin/bash
pytest -x  # Para no primeiro erro
if [ $? -ne 0 ]; then
    echo "❌ Testes falharam. Commit abortado."
    exit 1
fi
```

### CI/CD Integration

Testes rodam automaticamente em cada push:

```yaml
# GitHub Actions
- name: Run Tests
  run: pytest --cov=app
```

---

## 🆘 Troubleshooting

### Teste falha com ImportError

```
ImportError: cannot import name 'X' from 'app.module'
```

**Solução**: Verificar `app/__init__.py` está exportando tudo.

### Fixture não encontrada

```
fixture 'temp_db' not found
```

**Solução**: `conftest.py` está no mesmo diretório? Adicione o import.

### Teste hangs (fica pendurado)

```
pytest --timeout=10  # Timeout de 10s por teste
```

### Async test fails

Use `@pytest.mark.asyncio` e `async def test_*`.

---

## 📚 Recursos

- [pytest documentation](https://docs.pytest.org/)
- [pytest asyncio](https://pytest-asyncio.readthedocs.io/)
- [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## 📝 Checklist para PR com Novo Teste

Antes de fazer commit:

- [ ] Teste foi criado ANTES do código (TDD)
- [ ] Teste tem nome descritivo (`test_deve_*`)
- [ ] Teste é isolado (usa fixtures, não modifica estado global)
- [ ] Teste passa localmente (`pytest -v`)
- [ ] Cobertura aumentou (`pytest --cov`)
- [ ] Documentação foi atualizada
- [ ] Teste é rápido (< 1s)
- [ ] Edge cases foram testados

---

**Sucesso no desenvolvimento com TDD! 🎉**
