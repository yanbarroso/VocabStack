"""
Testes para módulo de utilitários (ReaderFactory e readers)
Focado em leitura de diferentes formatos de arquivo
"""

import pytest
from pathlib import Path
from app.utils.readers import ReaderFactory


@pytest.mark.utils
class TestReaderFactoryInit:
    """Testes de inicialização da factory"""
    
    def test_factory_initialization(self):
        """Deve inicializar factory corretamente"""
        factory = ReaderFactory()
        assert factory is not None


@pytest.mark.utils
class TestReaderFactoryGetReader:
    """Testes para obtenção de leitor correto"""
    
    def test_txt_reader_selection(self):
        """Deve retornar TxtReader para arquivos .txt"""
        factory = ReaderFactory()
        reader = factory.get_reader("arquivo.txt")
        
        assert reader is not None
        assert reader.__class__.__name__ == "TxtReader"
    
    def test_epub_reader_selection(self):
        """Deve retornar EpubReader para arquivos .epub"""
        factory = ReaderFactory()
        reader = factory.get_reader("livro.epub")
        
        assert reader is not None
        assert reader.__class__.__name__ == "EpubReader"
    
    def test_pdf_reader_selection(self):
        """Deve retornar PdfReader para arquivos .pdf"""
        factory = ReaderFactory()
        reader = factory.get_reader("documento.pdf")
        
        assert reader is not None
        assert reader.__class__.__name__ == "PdfReader"
    
    def test_case_insensitive_extension(self):
        """Deve ser case-insensitive na extensão"""
        factory = ReaderFactory()
        
        reader_lower = factory.get_reader("arquivo.txt")
        reader_upper = factory.get_reader("arquivo.TXT")
        
        assert reader_lower.__class__.__name__ == reader_upper.__class__.__name__
    
    def test_unsupported_format_returns_none(self):
        """Deve retornar None para formato não suportado"""
        factory = ReaderFactory()
        
        with pytest.raises(ValueError):
            reader = factory.get_reader("arquivo.docx")


@pytest.mark.utils
class TestTxtReaderRead:
    """Testes para leitura de arquivos TXT"""
    
    def test_read_valid_txt_file(self, temp_txt_file):
        """Deve ler arquivo TXT válido"""
        factory = ReaderFactory()
        reader = factory.get_reader(str(temp_txt_file))
        
        content = reader.extract_text(str(temp_txt_file))
        
        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0
    
    def test_read_returns_string(self, temp_txt_file):
        """Retorno deve ser string"""
        factory = ReaderFactory()
        reader = factory.get_reader(str(temp_txt_file))
        
        content = reader.extract_text(str(temp_txt_file))
        
        assert isinstance(content, str)
    
    def test_read_preserves_content(self, temp_txt_file):
        """Deve preservar conteúdo do arquivo"""
        # Escrever conteúdo específico
        test_content = "teste de conteúdo específico com acentos"
        Path(temp_txt_file).write_text(test_content, encoding='utf-8')
        
        factory = ReaderFactory()
        reader = factory.get_reader(str(temp_txt_file))
        
        content = reader.extract_text(str(temp_txt_file))
        
        assert test_content in content
    
    def test_read_nonexistent_file(self):
        """Deve lançar erro ao ler arquivo inexistente"""
        factory = ReaderFactory()
        reader = factory.get_reader("inexistente.txt")
        
        with pytest.raises((FileNotFoundError, ValueError)):
            reader.extract_text("inexistente.txt")
    
    def test_read_empty_txt_file(self):
        """Deve lidar com arquivo TXT vazio"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            
            content = reader.extract_text(temp_path)
            
            assert content == ""
        finally:
            Path(temp_path).unlink()


@pytest.mark.utils
class TestTxtReaderHandling:
    """Testes para tratamento especial de formato TXT"""
    
    def test_handles_unicode(self, temp_txt_file):
        """Deve lidar com unicode corretamente"""
        unicode_content = "Héllo wørld çé été αβγδ 中文"
        Path(temp_txt_file).write_text(unicode_content, encoding='utf-8')
        
        factory = ReaderFactory()
        reader = factory.get_reader(str(temp_txt_file))
        
        content = reader.extract_text(str(temp_txt_file))
        
        assert unicode_content in content
    
    def test_handles_newlines(self):
        """Deve preservar quebras de linha"""
        import tempfile
        
        content_with_newlines = "linha 1\nlinha 2\nlinha 3"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content_with_newlines)
            temp_path = f.name
        
        try:
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            
            content = reader.read(temp_path)
            
            assert "\n" in content or content == content_with_newlines
        finally:
            Path(temp_path).unlink()
    
    def test_handles_special_characters(self, temp_txt_file):
        """Deve lidar com caracteres especiais"""
        special_content = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        Path(temp_txt_file).write_text(special_content, encoding='utf-8')
        
        factory = ReaderFactory()
        reader = factory.get_reader(str(temp_txt_file))
        
        content = reader.extract_text(str(temp_txt_file))
        
        assert special_content in content


@pytest.mark.utils
class TestReaderFactoryAvailableReaders:
    """Testes para verificar leitores disponíveis"""
    
    def test_has_txt_reader(self):
        """Factory deve ter TxtReader disponível"""
        factory = ReaderFactory()
        reader = factory.get_reader("file.txt")
        
        assert reader is not None
    
    def test_has_epub_reader(self):
        """Factory deve ter EpubReader disponível"""
        factory = ReaderFactory()
        reader = factory.get_reader("file.epub")
        
        assert reader is not None
    
    def test_has_pdf_reader(self):
        """Factory deve ter PdfReader disponível"""
        factory = ReaderFactory()
        reader = factory.get_reader("file.pdf")
        
        assert reader is not None


@pytest.mark.utils
class TestReaderExtensionParsing:
    """Testes para parse de extensão"""
    
    def test_extracts_extension_correctly(self):
        """Deve extrair extensão de caminho"""
        factory = ReaderFactory()
        
        # Deve funcionar com paths completos
        reader = factory.get_reader("/path/to/arquivo.txt")
        assert reader is not None
        assert reader.__class__.__name__ == "TxtReader"
    
    def test_handles_multiple_dots(self):
        """Deve lidar com nomes que têm múltiplos pontos"""
        factory = ReaderFactory()
        
        reader = factory.get_reader("arquivo.backup.txt")
        assert reader is not None
        assert reader.__class__.__name__ == "TxtReader"
    
    def test_handles_no_extension(self):
        """Deve retornar erro para arquivo sem extensão"""
        factory = ReaderFactory()
        
        with pytest.raises(ValueError):
            reader = factory.get_reader("arquivo_sem_extensao")


@pytest.mark.utils
@pytest.mark.integration
class TestReaderFileOperations:
    """Testes de operações de arquivo completas"""
    
    def test_read_write_read_cycle(self):
        """Deve ler arquivo após escrita"""
        import tempfile
        
        original_content = "conteúdo para teste de ciclo read-write-read"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(original_content)
            temp_path = f.name
        
        try:
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            
            # Primeira leitura
            content1 = reader.extract_text(temp_path)
            assert original_content in content1
            
            # Segunda leitura
            content2 = reader.extract_text(temp_path)
            assert content1 == content2
        finally:
            Path(temp_path).unlink()


@pytest.mark.utils
class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_invalid_path_handling(self):
        """Deve lidar com path inválido"""
        factory = ReaderFactory()
        reader = factory.get_reader("/invalid/path/arquivo.txt")
        
        with pytest.raises((FileNotFoundError, OSError, ValueError)):
            reader.extract_text("/invalid/path/arquivo.txt")
    
    def test_permission_denied_handling(self):
        """Deve lidar com arquivo sem permissão"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("content")
            temp_path = f.name
        
        try:
            # Remover permissão de leitura
            os.chmod(temp_path, 0o000)
            
            factory = ReaderFactory()
            reader = factory.get_reader(temp_path)
            
            with pytest.raises((PermissionError, OSError, ValueError)):
                reader.extract_text(temp_path)
        finally:
            # Restaurar permissão antes de deletar
            os.chmod(temp_path, 0o644)
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
