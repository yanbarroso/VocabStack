# 🎬 Como Continuar com os Testes TDD

## Status Atual ✅

```
68 / 92 testes passando (74% concluído)
- API: 21/21 ✅ (100%)
- Utils: 22/25 ✅ (88%)
- Services: 25/35 🟡 (70%)
- Database: 10/17 🟡 (59%)
- Integration: 10/16 🟡 (62%)
```

---

## 🚀 Próximas Prioridades

### 1️⃣ Corrigir Database Tests (Ganho: +7 testes)

**Problema**: Schema SQL tem diferenças entre o esperado e o real

**Ação**:
```bash
# Primeiro, ver o erro exato
pytest tests/test_db.py::TestDatabaseInitialization::test_tables_created -v

# Depois verificar o schema real
sqlite3 :memory: ".schema"
```

**Arquivo a ajustar**: `tests/test_db.py`

### 2️⃣ Corrigir Services Tests (Ganho: +10 testes)

**Problema**: LanguageProcessor('en') pode não ter dados de NLTK

**Ação**:
```bash
pytest tests/test_services.py::TestLanguageProcessorInitialization::test_english_processor_init -v
```

**Solução provável**: Mock dos stopwords ou pré-download de dados

### 3️⃣ Integração Tests (Ganho: +6 testes)

**Problema**: Cascata de erros por banco de dados

**Ação**: Depois que database tests passarem, rodar integração novamente

---

## 📋 Guia Passo a Passo

### Passo 1: Clonar/Atualizar Repositório

```bash
cd /workspaces/codespaces-blank
git status  # Ver mudanças
git add tests/ pyproject.toml TESTES.md TEST_*.md
git commit -m "test: Implementar suite TDD completa (68 testes passando)"
git push
```

### Passo 2: Rodar Testes Localmente

```bash
# Instalar dependências (se não feito)
pip install -e ".[dev]"

# Rodar todos os testes
pytest tests/ -v

# Rodar apenas os que falharam
pytest tests/test_db.py tests/test_services.py::TestLanguageProcessorInitialization -v
```

### Passo 3: Debugar Falhas Específicas

```bash
# Exemplo: Verificar erro específico
pytest tests/test_db.py::TestDatabaseInitialization::test_tables_created -vv --tb=long

# Com pdb (debugger Python)
pytest tests/test_db.py::TestDatabaseInitialization::test_tables_created --pdb
```

### Passo 4: Corrigir e Revalidar

Após cada correção:
```bash
pytest tests/ --tb=short
```

---

## 🔍 Analisando Falhas Específicas

### Erro: `AttributeError: 'Database' object has no attribute...`

**Causa provável**: Nome de método ou propriedade diferente

**Solução**:
1. Abrir `app/db/database.py`
2. Verificar nome exato do método
3. Atualizar teste para uso correto

### Erro: `sqlite3.OperationalError: no such table...`

**Causa provável**: Schema não foi criado corretamente

**Solução**:
1. Verificar `DatabaseManager._create_tables()`
2. Validar SQL syntax
3. Testar manualmente com sqlite3

### Erro: `ValueError: not enough values to unpack`

**Causa provável**: Retorno de função diferente do esperado

**Solução**:
1. Imprimir retorno real: `print(type(result), result)`
2. Atualizar teste para novo formato

---

## 📚 Referências Rápidas

### Executar Categoria Específica

```bash
# Apenas API tests
pytest tests/test_api.py

# Apenas Database tests  
pytest tests/test_db.py

# Por marker
pytest -m integration
pytest -m "api and not slow"
```

### Ver Cobertura

```bash
# Gerar relatório HTML
pytest tests/ --cov=app --cov-report=html

# Abrir no navegador
# htmlcov/index.html
```

### Modo Watch (Re-rodar ao salvar)

```bash
# Instalar pytest-watch
pip install pytest-watch

# Rodar em watch mode
ptw tests/ -- -v
```

---

## 💾 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `tests/conftest.py` | Fixtures compartilhadas |
| `tests/test_api.py` | Testes de endpoints (✅ 100%) |
| `tests/test_utils.py` | Testes de readers (✅ 88%) |
| `tests/test_services.py` | Testes de processador (🟡 70%) |
| `tests/test_db.py` | Testes de banco (🟡 59%) |
| `tests/test_integration.py` | Testes end-to-end (🟡 62%) |
| `TESTES.md` | 📖 Guia completo de TDD |
| `pyproject.toml` | ⚙️ Configuração pytest |

---

## ✅ Checklist de Conclusão

- [ ] Rodar `pytest tests/ -v` e ter >85 testes passando
- [ ] Nenhum erro em testes de API
- [ ] Documentação de testes revisada
- [ ] CI/CD configurado (GitHub Actions)
- [ ] Code coverage >80%
- [ ] Exemplos de novos testes criados
- [ ] Documentação atualizada com resultados

---

## 🎓 Aprender Mais

### Recursos Dentro do Projeto

1. **TESTES.md** - Completo guia TDD
   - Ciclo Red-Green-Refactor explicado
   - Exemplos de padrões de teste
   - Boas práticas

2. **TEST_IMPLEMENTATION_SUMMARY.md** - Resumo de implementação
   
3. **TEST_FINAL_STATUS.md** - Status completo

### Testes Recomendados para Estudar

```python
# Exemplos de bom padrão
tests/test_api.py::TestHealthEndpoint::test_health_check_returns_200
tests/test_utils.py::TestReaderFactoryGetReader::test_txt_reader_selection
tests/test_services.py::TestLanguageProcessorInitialization::test_french_processor_init
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
```bash
# Solução
pip install -e .
```

### "Fixtures dependency not set up"
```bash
# Verificar conftest.py está em tests/
# Ou rodar do diretório correto
cd /workspaces/codespaces-blank
pytest tests/
```

### "Tests are hanging/slow"
```bash
# Rodar com timeout
pytest tests/ --timeout=10

# Ver quais são lentos
pytest tests/ --durations=10
```

### "NLTK/SpaCy data missing"
```bash
# Baixar dados necessários
python -c "import nltk; nltk.download('stopwords')"
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

---

## 🎯 Meta Final

**Quando remover `🟡` e ter tudo `✅`:**

- ✅ Todos os 92 testes devem passar
- ✅ Code coverage >85%
- ✅ Documentação completa
- ✅ CI/CD verde (se conectado)
- ✅ Novos testes seguem padrão TDD

---

## 📞 Próximas Etapas Sugeridas

1. **Hoje**: Rodar `pytest tests/ -v` e entender falhas
2. **Amanhã**: Corrigir database tests (+7)
3. **Próximo dia**: Corrigir services tests (+10)
4. **Integração**: Rodar/manter CI testando

**Tempo estimado**: 2-4 horas para 100% de conclusão

---

**Bom teste! 🚀**
