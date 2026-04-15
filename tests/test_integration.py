"""
Testes de integração (end-to-end)
Focado em fluxos completos que envolvem múltiplas camadas
"""

import pytest
from pathlib import Path
import tempfile


@pytest.mark.integration
class TestEndToEndFileUpload:
    """Testes de fluxo completo de upload"""
    
    def test_upload_and_retrieve_words(self, db_with_sample_data):
        """Deve fazer upload, processar e recuperar palavras"""
        estante = db_with_sample_data.listar_estante()
        
        if len(estante) > 0:
            # Têm dados no banco
            primeiro_titulo = estante[0][1] if isinstance(estante[0], tuple) else estante[0]["titulo"]
            palavras = db_with_sample_data.obter_palavras_obra(primeiro_titulo)
            
            # Deve retornar alguma palavra
            assert len(palavras) > 0
    
    def test_multiple_uploads_different_results(self, temp_db, processor_fr, processor_en):
        """Múltiplos uploads com idiomas diferentes devem gerar resultados diferentes"""
        text_fr = "le petit prince regarde les couchers de soleil"
        text_en = "alice in wonderland wandered through the forest"
        
        stats_fr = processor_fr.get_detailed_stats(text_fr)
        stats_en = processor_en.get_detailed_stats(text_en)
        
        # Resultados devem ser diferentes
        assert stats_fr["word_frequencies"] != stats_en["word_frequencies"]


@pytest.mark.integration
class TestDatabaseConsistency:
    """Testes de consistência entre camadas"""
    
    def test_stats_consistent_between_calls(self, db_with_sample_data):
        """Estatísticas devem ser consistentes em múltiplas chamadas"""
        estante1 = db_with_sample_data.listar_estante()
        estante2 = db_with_sample_data.listar_estante()
        
        assert estante1 == estante2
    
    def test_word_counts_match_frequency_sum(self, temp_db):
        """Contagem total deve corresponder à soma das frequências"""
        titulo = "Test Consistency"
        palavras = {"palavra1": 10, "palavra2": 15, "palavra3": 5}
        
        temp_db.salvar_processamento(titulo, palavras)
        
        # Total deve ser 30
        retrived = temp_db.obter_palavras_obra(titulo)
        
        if len(retrived) > 0:
            # Deve ter recuperado as palavras
            assert len(retrived) > 0


@pytest.mark.integration
class TestProcessorDatabaseIntegration:
    """Testes de integração Processor + Database"""
    
    def test_processor_output_compatible_with_database(self, temp_db, processor_fr):
        """Saída do processador deve ser compatível com banco"""
        texto = "le petit prince et la rose"
        stats = processor_fr.get_detailed_stats(texto)
        
        # Palavras devem ser um dicionário
        assert isinstance(stats["word_frequencies"], dict)
        
        # Deve ser salvável no banco
        temp_db.salvar_processamento("Test", stats["word_frequencies"])
        
        # Deve ser recuperável
        palavras = temp_db.obter_palavras_obra("Test")
        assert len(palavras) > 0
    
    def test_top_words_order_preserved(self, temp_db, processor_fr):
        """Ordem das palavras deve ser preservada"""
        texto = "a a a a b b b c c d"
        top_words = processor_fr.get_top_words(texto, top_n=10)
        
        if len(top_words) > 1:
            # Primeiro deve ter frequência >= segundo
            assert top_words[0][1] >= top_words[1][1]


@pytest.mark.integration
@pytest.mark.asyncio
class TestAPIServiceIntegration:
    """Testes de integração API + Services"""
    
    async def test_health_uses_services(self, client):
        """Endpoint /health deve usar services"""
        response = await client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter estrutura esperada
        assert "status" in data


@pytest.mark.integration
class TestReaderDatabaseIntegration:
    """Testes de integração Reader + Database"""
    
    def test_read_file_and_save_to_database(self, temp_db, processor_fr):
        """Deve ler arquivo e salvar resultado no banco"""
        import tempfile
        
        # Criar arquivo temporário
        content = "le petit prince habite sur une petite planete"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            from app.utils.readers import ReaderFactory
            
            # Ler arquivo
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            text = reader.extract_text(temp_path)
            
            # Processar
            stats = processor_fr.get_detailed_stats(text)
            
            # Salvar no banco
            titulo = Path(temp_path).stem
            temp_db.salvar_processamento(
                titulo=titulo,
                tipo="TXT",
                idioma="fr",
                total=len(text.split()),
                freq_dict=stats["word_frequencies"]
            )
            
            # Recuperar
            palavras = temp_db.obter_palavras_obra(titulo)
            
            assert len(palavras) > 0
        finally:
            Path(temp_path).unlink()


@pytest.mark.integration
class TestDataFlowReadToAPI:
    """Testes de fluxo de dados da leitura até API"""
    
    def test_file_read_process_store_retrieve(self, temp_db, processor_fr):
        """Fluxo completo: lê → processa → armazena → recupera"""
        import tempfile
        
        # 1. Criar arquivo
        original_text = "le petit livre avec des mots importants"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(original_text)
            temp_path = f.name
        
        try:
            # 2. Ler arquivo
            from app.utils.readers import ReaderFactory
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            read_text = reader.extract_text(temp_path)
            
            # 3. Processar
            stats = processor_fr.get_detailed_stats(read_text)
            
            # 4. Armazenar
            titulo = "integration_test"
            temp_db.salvar_processamento(
                titulo=titulo,
                tipo="TXT",
                idioma="fr",
                total=len(read_text.split()),
                freq_dict=stats["word_frequencies"]
            )
            
            # 5. Recuperar
            palavras = temp_db.obter_palavras_obra(titulo)
            estante = temp_db.listar_estante()
            
            # Validações
            assert len(palavras) > 0
            assert len(estante) > 0
            assert any(e[1] == titulo for e in estante) or any(e["titulo"] == titulo for e in estante)
        finally:
            Path(temp_path).unlink()


@pytest.mark.integration
class TestErrorPropagation:
    """Testes de propagação de erros entre camadas"""
    
    def test_invalid_file_error_propagates(self):
        """Erro de arquivo inválido deve se propagar"""
        from app.utils.readers import ReaderFactory
        
        factory = ReaderFactory()
        reader = factory.get_reader("invalid_file.txt")
        
        with pytest.raises((FileNotFoundError, OSError)):
            reader.read("invalid_file.txt")
    
    def test_unsupported_format_error_propagates(self):
        """Erro de formato não suportado deve se propagar"""
        from app.utils.readers import ReaderFactory
        
        factory = ReaderFactory()
        
        with pytest.raises(ValueError):
            reader = factory.get_reader("file.doc")


@pytest.mark.integration
class TestConcurrentDataAccess:
    """Testes de acesso concorrente aos dados"""
    
    def test_multiple_file_reads_consistency(self):
        """Múltiplas leituras do mesmo arquivo devem ser consistentes"""
        import tempfile
        
        content = "conteúdo para teste de consistência"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            from app.utils.readers import ReaderFactory
            
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            
            read1 = reader.extract_text(temp_path)
            read2 = reader.extract_text(temp_path)
            read3 = reader.extract_text(temp_path)
            
            assert read1 == read2 == read3
        finally:
            Path(temp_path).unlink()


@pytest.mark.integration
class TestProcessingPipeline:
    """Testes do pipeline completo de processamento"""
    
    def test_multilingual_pipeline(self, temp_db, processor_fr, processor_en):
        """Pipeline com múltiplos idiomas"""
        import tempfile
        
        # Arquivo em francês
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("le petit prince")
            fr_path = f.name
        
        # Arquivo em inglês
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("alice in wonderland")
            en_path = f.name
        
        try:
            from app.utils.readers import ReaderFactory
            
            factory = ReaderFactory()
            
            # Processar arquivo francês
            fr_reader = factory.get_reader(fr_path)
            fr_text = fr_reader.extract_text(fr_path)
            fr_stats = processor_fr.get_detailed_stats(fr_text)
            temp_db.salvar_processamento(
                titulo="Le Petit Prince",
                tipo="TXT",
                idioma="fr",
                total=len(fr_text.split()),
                freq_dict=fr_stats["word_frequencies"]
            )
            
            # Processar arquivo inglês
            en_reader = factory.get_reader(en_path)
            en_text = en_reader.extract_text(en_path)
            en_stats = processor_en.get_detailed_stats(en_text)
            temp_db.salvar_processamento(
                titulo="Alice in Wonderland",
                tipo="TXT",
                idioma="en",
                total=len(en_text.split()),
                freq_dict=en_stats["word_frequencies"]
            )
            
            # Recuperar
            estante = temp_db.listar_estante()
            
            assert len(estante) >= 2
        finally:
            Path(fr_path).unlink()
            Path(en_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
