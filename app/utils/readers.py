"""
Utils - Leitura de arquivos e extração de texto
"""

import os
from abc import ABC, abstractmethod
from typing import Union

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import pdfplumber
import trafilatura

__all__ = ["BaseReader", "EpubReader", "PdfReader", "TxtReader", "WebReader", "ReaderFactory"]


class BaseReader(ABC):
    """Classe base abstrata para leitores de arquivo"""
    
    @abstractmethod
    def extract_text(self, source: Union[str, bytes]) -> str:
        """
        Extrai texto do arquivo
        
        Args:
            source: Caminho do arquivo ou URL
            
        Returns:
            Texto extraído
            
        Raises:
            NotImplementedError: Se não implementado pela subclasse
        """
        raise NotImplementedError("Subclasses devem implementar extract_text")


class EpubReader(BaseReader):
    """Leitor para arquivos EPUB"""
    
    def extract_text(self, file_path: str) -> str:
        """Extrai texto de um arquivo EPUB"""
        try:
            book = epub.read_epub(file_path)
            full_text = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                full_text.append(soup.get_text())
            return " ".join(full_text)
        except Exception as e:
            raise ValueError(f"Erro ao ler EPUB: {str(e)}")


class PdfReader(BaseReader):
    """Leitor para arquivos PDF"""
    
    def extract_text(self, file_path: str) -> str:
        """Extrai texto de um arquivo PDF"""
        try:
            with pdfplumber.open(file_path) as pdf:
                return " ".join([page.extract_text() or "" for page in pdf.pages])
        except Exception as e:
            raise ValueError(f"Erro ao ler PDF: {str(e)}")


class TxtReader(BaseReader):
    """Leitor para arquivos de texto simples"""
    
    def extract_text(self, file_path: str) -> str:
        """Extrai texto de um arquivo TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo de texto: {str(e)}")


class WebReader(BaseReader):
    """Leitor para URLs/conteúdo web"""
    
    def extract_text(self, url: str) -> str:
        """Extrai texto de uma URL"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise ValueError("Não foi possível baixar o conteúdo")
            return trafilatura.extract(downloaded) or ""
        except Exception as e:
            raise ValueError(f"Erro ao ler URL: {str(e)}")


class ReaderFactory:
    """Factory para obter o leitor apropriado baseado no tipo de arquivo"""
    
    _readers = {
        '.epub': EpubReader,
        '.pdf': PdfReader,
        '.txt': TxtReader
    }
    
    @staticmethod
    def get_reader(source: str) -> BaseReader:
        """
        Obtém o leitor apropriado para a fonte
        
        Args:
            source: Caminho do arquivo ou URL
            
        Returns:
            Instância do leitor apropriado
            
        Raises:
            ValueError: Se tipo de arquivo não é suportado
        """
        if source.startswith('http'):
            return WebReader()
        
        ext = os.path.splitext(source)[1].lower()
        reader_class = ReaderFactory._readers.get(ext)
        
        if not reader_class:
            raise ValueError(f"Extensão '{ext}' não suportada. Extensões válidas: {', '.join(ReaderFactory._readers.keys())}")
        
        return reader_class()
    
    @staticmethod
    def registrar_reader(extensao: str, reader_class: type) -> None:
        """Permite registrar novos tipos de leitores"""
        ReaderFactory._readers[extensao.lower()] = reader_class
