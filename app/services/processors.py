"""
Services - Lógica de negócio e processamento
"""

from collections import Counter
from typing import Dict, List
import spacy
from nltk.corpus import stopwords
import nltk

# Download silencioso de stopwords
nltk.download('stopwords', quiet=True)

__all__ = ["LanguageProcessor"]


class LanguageProcessor:
    """Processador de linguagem natural para análise textual"""
    
    _models = {}  # Cache de modelos carregados
    
    LANG_MODELS = {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm',
        'pt': 'pt_core_news_sm'
    }
    
    STOPWORDS_MAP = {
        'fr': 'french',
        'en': 'english',
        'pt': 'portuguese'
    }

    def __init__(self, lang_code: str = 'fr'):
        """
        Inicializa o processador de linguagem
        
        Args:
            lang_code: Código do idioma (fr, en, pt)
            
        Raises:
            ValueError: Se idioma não é suportado
        """
        if lang_code not in self.LANG_MODELS:
            raise ValueError(f"Idioma '{lang_code}' não suportado. Idiomas disponíveis: {list(self.LANG_MODELS.keys())}")
        
        self.lang_code = lang_code
        self.nlp = self._get_model(lang_code)
        self.stop_words = set(stopwords.words(self.STOPWORDS_MAP[lang_code]))

    @classmethod
    def _get_model(cls, lang_code: str):
        """
        Obtém modelo spacy (com cache)
        
        Args:
            lang_code: Código do idioma
            
        Returns:
            Modelo spacy carregado
        """
        model_name = cls.LANG_MODELS.get(lang_code)
        if model_name not in cls._models:
            print(f"📥 Carregando modelo NLP: {model_name}...")
            try:
                cls._models[model_name] = spacy.load(model_name)
            except OSError:
                raise RuntimeError(f"Modelo '{model_name}' não encontrado. Execute: python -m spacy download {model_name}")
        return cls._models[model_name]

    def get_detailed_stats(self, text: str) -> Dict:
        """
        Analisa texto e retorna estatísticas detalhadas
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dicionário com:
                - total_count: Total de palavras
                - word_frequencies: Counter com frequência de cada palavra
        """
        if not text or not isinstance(text, str):
            return {"total_count": 0, "word_frequencies": {}}
        
        doc = self.nlp(text.lower())
        
        # Filtrar lemas: remover stopwords, palavras não alfabéticas e com 1 caractere
        lemas_filtrados = [
            token.lemma_ for token in doc 
            if (token.lemma_ not in self.stop_words and 
                token.is_alpha and 
                len(token.text) > 1)
        ]
        
        return {
            "total_count": len([t for t in doc if t.is_alpha]),
            "word_frequencies": dict(Counter(lemas_filtrados))
        }

    def get_top_words(self, text: str, top_n: int = 100) -> List[tuple]:
        """
        Obtém as N palavras mais frequentes
        
        Args:
            text: Texto a ser analisado
            top_n: Número de palavras a retornar
            
        Returns:
            Lista de tuplas (palavra, frequência) ordenadas por frequência
        """
        stats = self.get_detailed_stats(text)
        freq_counter = Counter(stats["word_frequencies"])
        return freq_counter.most_common(top_n)

    def extrair_entidades(self, text: str) -> Dict[str, List[str]]:
        """
        Extrai entidades nomeadas do texto
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dicionário mapeando tipo de entidade para lista de valores
        """
        doc = self.nlp(text)
        entidades = {}
        for ent in doc.ents:
            if ent.label_ not in entidades:
                entidades[ent.label_] = []
            entidades[ent.label_].append(ent.text)
        return entidades
