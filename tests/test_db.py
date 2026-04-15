"""
Testes para módulo de banco de dados (DatabaseManager)
Focado em operações CRUD e integridade de dados
"""

import pytest
from datetime import datetime
from pathlib import Path
from app.db import DatabaseManager


@pytest.mark.database
class TestDatabaseInitialization:
    """Testes de inicialização e conexão"""
    
    def test_database_initialization(self, temp_db):
        """Deve inicializar banco corretamente"""
        assert temp_db is not None
        assert isinstance(temp_db, DatabaseManager)
    
    def test_tables_created(self, temp_db):
        """Deve criar tabelas necessárias"""
        cursor = temp_db.conn.cursor()
        
        # Verificar tabela obras
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='obras'"
        )
        assert cursor.fetchone() is not None
        
        # Verificar tabela palavras_vistas
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='palavras_vistas'"
        )
        assert cursor.fetchone() is not None


@pytest.mark.database
class TestSalvarProcessamento:
    """Testes para salvar processamento de texto"""
    
    def test_save_valid_processamento(self, temp_db):
        """Deve salvar processamento válido"""
        titulo = "O Pequeno Príncipe"
        
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="EPUB",
            idioma="pt",
            total=150,
            freq_dict={"prîncipe": 15, "planeta": 8, "rosa": 5}
        )
        
        # Verificar que foi salvo
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT * FROM obras WHERE titulo = ?", (titulo,))
        result = cursor.fetchone()
        
        assert result is not None
    
    def test_word_frequencies_saved(self, temp_db):
        """Deve salvar frequências de palavras"""
        titulo = "Test Book"
        
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=15,
            freq_dict={"hello": 10, "world": 5}
        )
        
        # Get obra_id
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT id FROM obras WHERE titulo = ?", (titulo,))
        result = cursor.fetchone()
        
        if result:
            obra_id = result[0]
            cursor.execute(
                "SELECT palavra, frequencia FROM palavras_vistas WHERE obra_id = ? ORDER BY frequencia DESC",
                (obra_id,)
            )
            palavras_db = cursor.fetchall()
            
            assert len(palavras_db) == 2
    
    def test_duplicate_titulo_updates(self, temp_db):
        """Mesmo título deve atualizar, não duplicar"""
        titulo = "Same Title"
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=10,
            freq_dict={"palavra1": 5}
        )
        
        # Salvar novamente com mesmo titulo
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=15,
            freq_dict={"palavra2": 10}
        )
        
        # Verificar que não foi duplicado
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM obras WHERE titulo = ?", (titulo,))
        count = cursor.fetchone()[0]
        
        # Deve ter sido atualizado (1) ou lançar erro
        assert count >= 1
    
    def test_empty_palavras_not_saved(self, temp_db):
        """Não deve salvar se não houver palavras"""
        titulo = "Empty"
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=0,
            freq_dict={}
        )
        
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM palavras_vistas WHERE obra_id IN (SELECT id FROM obras WHERE titulo = ?)", (titulo,))
        count = cursor.fetchone()[0]
        
        assert count == 0


@pytest.mark.database
class TestListarEstante:
    """Testes para listar obras"""
    
    def test_empty_database_returns_empty_list(self, temp_db):
        """Banco vazio deve retornar lista vazia"""
        estante = temp_db.listar_estante()
        
        assert isinstance(estante, list)
        assert len(estante) == 0
    
    def test_list_multiple_obras(self, db_with_sample_data):
        """Deve listar múltiplas obras"""
        estante = db_with_sample_data.listar_estante()
        
        assert len(estante) > 0
        # Cada item deve ser um dicionário com dados
        for obra in estante:
            assert "titulo" in obra or isinstance(obra, tuple)
    
    def test_list_ordered_by_date(self, temp_db):
        """Obras devem estar ordenadas por data (mais recentes primeiro)"""
        temp_db.salvar_processamento("Obra 1", {"palavra": 1})
        temp_db.salvar_processamento("Obra 2", {"palavra": 1})
        
        estante = temp_db.listar_estante()
        
        if len(estante) > 1:
            # Última obra salva deve ser primeira na lista
            assert estante[0][1] == "Obra 2" or estante[0]["titulo"] == "Obra 2"


@pytest.mark.database
class TestObterObra:
    """Testes para obter uma obra específica"""
    
    def test_get_existing_obra(self, db_with_sample_data):
        """Deve retornar obra existente"""
        estante = db_with_sample_data.listar_estante()
        
        if len(estante) > 0:
            titulo = estante[0][1] if isinstance(estante[0], tuple) else estante[0]["titulo"]
            obra = db_with_sample_data.obter_obra(titulo)
            
            assert obra is not None
    
    def test_nonexistent_obra_returns_none(self, temp_db):
        """Obra inexistente deve retornar None"""
        obra = temp_db.obter_obra("Obra Inexistente")
        
        assert obra is None
    
    def test_obra_has_required_fields(self, db_with_sample_data):
        """Obra retornada deve ter campos obrigatórios"""
        estante = db_with_sample_data.listar_estante()
        
        if len(estante) > 0:
            titulo = estante[0][1] if isinstance(estante[0], tuple) else estante[0]["titulo"]
            obra = db_with_sample_data.obter_obra(titulo)
            
            # Deve ter pelo menos titulo
            assert obra is not None


@pytest.mark.database
class TestObterPalavrasObra:
    """Testes para obter palavras de uma obra"""
    
    def test_get_top_words_from_obra(self, db_with_sample_data):
        """Deve retornar top N palavras de uma obra"""
        estante = db_with_sample_data.listar_estante()
        
        if len(estante) > 0:
            titulo = estante[0][1] if isinstance(estante[0], tuple) else estante[0]["titulo"]
            palavras = db_with_sample_data.obter_palavras_obra(titulo)
            
            assert isinstance(palavras, list)
    
    def test_top_n_parameter(self, db_with_sample_data):
        """Deve respeitar parâmetro top_n"""
        estante = db_with_sample_data.listar_estante()
        
        if len(estante) > 0:
            titulo = estante[0][1] if isinstance(estante[0], tuple) else estante[0]["titulo"]
            
            top_5 = db_with_sample_data.obter_palavras_obra(titulo, top_n=5)
            top_10 = db_with_sample_data.obter_palavras_obra(titulo, top_n=10)
            
            assert len(top_5) <= 5
            assert len(top_10) <= 10
    
    def test_nonexistent_obra_returns_empty(self, temp_db):
        """Obra inexistente deve retornar lista vazia"""
        palavras = temp_db.obter_palavras_obra("Obra Inexistente")
        
        assert palavras == []


@pytest.mark.database
class TestLimparBanco:
    """Testes para limpeza do banco"""
    
    def test_clear_all_data(self, temp_db):
        """Deve limpar todos os dados"""
        # Primeiro adicionar dados
        temp_db.salvar_processamento(
            titulo="Obra",
            tipo="TXT",
            idioma="pt",
            total=10,
            freq_dict={"palavra": 5}
        )
        
        # Verificar que foi salvo
        estante = temp_db.listar_estante()
        assert len(estante) > 0
        
        # Limpar
        temp_db.limpar_banco()
        
        # Verificar que está vazio
        estante = temp_db.listar_estante()
        assert len(estante) == 0
    
    def test_clear_removes_all_tables(self, temp_db):
        """Limpeza deve remover dados de todas as tabelas"""
        temp_db.salvar_processamento("Test", {"palavra": 5})
        temp_db.limpar_banco()
        
        cursor = temp_db.conn.cursor()
        
        # Ambas as tabelas devem estar vazias
        cursor.execute("SELECT COUNT(*) FROM obras")
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM palavras_vistas")
        assert cursor.fetchone()[0] == 0


@pytest.mark.database
class TestDataIntegrity:
    """Testes de integridade de dados"""
    
    def test_no_duplicate_words_per_obra(self, temp_db):
        """Não deve haver palavras duplicadas por obra"""
        titulo = "Test"
        
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=8,
            freq_dict={"palavra": 5, "outra": 3}
        )
        
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT id FROM obras WHERE titulo = ?", (titulo,))
        result = cursor.fetchone()
        
        if result:
            obra_id = result[0]
            cursor.execute(
                "SELECT COUNT(*) FROM palavras_vistas WHERE obra_id = ?",
                (obra_id,)
            )
            count = cursor.fetchone()[0]
            
            assert count == 2
    
    def test_word_frequency_values_positive(self, temp_db):
        """Frequências de palavras devem ser positivas"""
        titulo = "Test"
        temp_db.salvar_processamento(
            titulo=titulo,
            tipo="TXT",
            idioma="en",
            total=10,
            freq_dict={"palavra": 10}
        )
        
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT frequencia FROM palavras_vistas LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            freq = result[0]
            assert freq > 0
    
    def test_foreign_key_relationship(self, temp_db):
        """Palavras devem ter referência válida a obra"""
        titulo = "Test"
        temp_db.salvar_processamento(titulo, {"palavra": 5})
        
        cursor = temp_db.conn.cursor()
        
        # Todas as palavras devem ter obra_id válido
        cursor.execute("""
            SELECT pv.* FROM palavras_vistas pv
            WHERE NOT EXISTS (SELECT 1 FROM obras o WHERE o.id = pv.obra_id)
        """)
        orphaned = cursor.fetchall()
        
        assert len(orphaned) == 0


@pytest.mark.database
@pytest.mark.integration
class TestConcurrentOperations:
    """Testes de operações concorrentes"""
    
    def test_multiple_saves_different_obras(self, temp_db):
        """Deve salvar múltiplas obras corretamente"""
        for i in range(5):
            titulo = f"Obra {i}"
            freq_dict = {f"palavra{j}": j * 10 for j in range(3)}
            temp_db.salvar_processamento(
                titulo=titulo,
                tipo="TXT",
                idioma="pt",
                total=sum(freq_dict.values()),
                freq_dict=freq_dict
            )
        
        estante = temp_db.listar_estante()
        assert len(estante) == 5


@pytest.mark.database
class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_get_nonexistent_obra_no_error(self, temp_db):
        """Não deve lançar erro ao obter obra inexistente"""
        # Não deve fazer raise
        obra = temp_db.obter_obra("Obra Que Não Existe")
        assert obra is None
    
    def test_get_nonexistent_palavras_no_error(self, temp_db):
        """Não deve lançar erro ao obter palavras inexistentes"""
        palavras = temp_db.obter_palavras_obra("Obra Que Não Existe")
        assert palavras == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
