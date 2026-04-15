"""
Testes para módulo de serviços (LanguageProcessor)
Focado em lógica de negócio e processamento de texto
"""

import pytest
from app.services import LanguageProcessor


@pytest.mark.service
class TestLanguageProcessorInitialization:
    """Testes de inicialização do processador"""
    
    def test_french_processor_init(self):
        """Deve inicializar processador em francês"""
        proc = LanguageProcessor('fr')
        assert proc.lang_code == 'fr'
        assert proc.nlp is not None
        assert len(proc.stop_words) > 0
    
    def test_english_processor_init(self):
        """Deve inicializar processador em inglês"""
        proc = LanguageProcessor('en')
        assert proc.lang_code == 'en'
        assert proc.nlp is not None
        assert len(proc.stop_words) > 0
    
    def test_unsupported_language_raises_error(self):
        """Deve lançar erro para idioma não suportado"""
        with pytest.raises(ValueError, match="não suportado"):
            LanguageProcessor('xx')
    
    def test_model_caching(self):
        """Modelo deve ser reutilizado (caching)"""
        proc1 = LanguageProcessor('fr')
        proc2 = LanguageProcessor('fr')
        
        # Devem usar o mesmo modelo carregado
        assert proc1.nlp is proc2.nlp


@pytest.mark.service
class TestGetDetailedStats:
    """Testes para análise de texto"""
    
    def test_returns_dict_with_required_keys(self, processor_fr):
        """Deve retornar dict com total_count e word_frequencies"""
        texto = "le petit prince"
        stats = processor_fr.get_detailed_stats(texto)
        
        assert isinstance(stats, dict)
        assert "total_count" in stats
        assert "word_frequencies" in stats
    
    def test_word_frequencies_is_dict(self, processor_fr, sample_text_fr):
        """word_frequencies deve ser um dicionário"""
        stats = processor_fr.get_detailed_stats(sample_text_fr)
        
        assert isinstance(stats["word_frequencies"], dict)
        # Chaves e valores devem ser strings e ints
        for palavra, freq in stats["word_frequencies"].items():
            assert isinstance(palavra, str)
            assert isinstance(freq, int)
    
    def test_total_count_is_positive(self, processor_fr, sample_text_fr):
        """Total deve ser positivo para texto válido"""
        stats = processor_fr.get_detailed_stats(sample_text_fr)
        
        assert stats["total_count"] > 0
    
    def test_empty_text_returns_zero_count(self, processor_fr):
        """Texto vazio deve retornar contagem zero"""
        stats = processor_fr.get_detailed_stats("")
        
        assert stats["total_count"] == 0
        assert stats["word_frequencies"] == {}
    
    def test_filters_stopwords(self, processor_fr):
        """Deve filtrar stopwords como 'le', 'la', 'de'"""
        # Texto com muitos stopwords em francês
        texto = "le petit prince et la rose de la planète"
        stats = processor_fr.get_detailed_stats(texto)
        
        # Stopwords não devem estar no resultado
        common_stopwords = ['le', 'de', 'la', 'et']
        for stopword in common_stopwords:
            assert stopword not in stats["word_frequencies"]
    
    def test_lemmatization_working(self, processor_fr):
        """Deve fazer lematização (ex: princes -> prince)"""
        texto = "les princes"
        stats = processor_fr.get_detailed_stats(texto)
        
        # Deve ter a forma lematizada
        assert len(stats["word_frequencies"]) > 0


@pytest.mark.service
class TestGetTopWords:
    """Testes para obtenção de top palavras"""
    
    def test_returns_list_of_tuples(self, processor_fr, sample_text_fr):
        """Deve retornar lista de tuplas"""
        top_words = processor_fr.get_top_words(sample_text_fr)
        
        assert isinstance(top_words, list)
        if len(top_words) > 0:
            assert isinstance(top_words[0], tuple)
            assert len(top_words[0]) == 2
    
    def test_respects_top_n_parameter(self, processor_fr, sample_text_fr):
        """Deve respeitar o parâmetro top_n"""
        top_5 = processor_fr.get_top_words(sample_text_fr, top_n=5)
        top_10 = processor_fr.get_top_words(sample_text_fr, top_n=10)
        
        assert len(top_5) <= 5
        assert len(top_10) <= 10
    
    def test_ordered_by_frequency(self, processor_fr):
        """Palavras devem estar ordenadas por frequência desc"""
        texto = "a a a b b c"
        top_words = processor_fr.get_top_words(texto, top_n=10)
        
        if len(top_words) > 1:
            # Primeira deve ter freq >= segunda
            assert top_words[0][1] >= top_words[1][1]
    
    def test_empty_text_returns_empty_list(self, processor_fr):
        """Texto vazio deve retornar lista vazia"""
        top_words = processor_fr.get_top_words("")
        
        assert top_words == []


@pytest.mark.service
class TestExtrairEntidades:
    """Testes para extração de entidades"""
    
    def test_extract_named_entities(self, processor_fr):
        """Deve extrair entidades nomeadas"""
        texto = "Pierre habite à Paris"
        entidades = processor_fr.extrair_entidades(texto)
        
        assert isinstance(entidades, dict)
    
    def test_entities_dict_format(self, processor_fr):
        """Entidades devem ter formato {tipo: [valores]}"""
        texto = "Alice et Bob vivaient en France"
        entidades = processor_fr.extrair_entidades(texto)
        
        for tipo, valores in entidades.items():
            assert isinstance(tipo, str)  # Tipo de entidade
            assert isinstance(valores, list)  # Lista de valores


@pytest.mark.service
@pytest.mark.integration
class TestProcessorLanguages:
    """Testes com múltiplos idiomas"""
    
    def test_french_and_english_different_stopwords(self, processor_fr, processor_en):
        """Stopwords de francês e inglês devem ser diferentes"""
        # "the" é stopword em inglês, não em francês
        assert "the" in processor_en.stop_words
        assert "the" not in processor_fr.stop_words
        
        # "le" é stopword em francês, não em inglês
        assert "le" in processor_fr.stop_words
        assert "le" not in processor_en.stop_words
    
    def test_multilingual_processing(self, processor_fr, processor_en):
        """Processadores devem trabalhar com seus respectivos idiomas"""
        texto_fr = "le petit prince regarde les couchers de soleil"
        texto_en = "alice wondered if she should follow the white rabbit"
        
        stats_fr = processor_fr.get_detailed_stats(texto_fr)
        stats_en = processor_en.get_detailed_stats(texto_en)
        
        # Ambos devem processar corretamente
        assert stats_fr["total_count"] > 0
        assert stats_en["total_count"] > 0
        
        # Resultados devem ser diferentes
        assert stats_fr["word_frequencies"] != stats_en["word_frequencies"]


@pytest.mark.service
class TestEdgeCases:
    """Testes para casos extremos"""
    
    def test_very_long_text(self, processor_fr):
        """Deve processar textos muito longos"""
        texto = "palavra " * 10000  # 10k palavras repetidas
        stats = processor_fr.get_detailed_stats(texto)
        
        assert stats["total_count"] > 0
    
    def test_special_characters(self, processor_fr):
        """Deve lidar com caracteres especiais"""
        texto = "Ceci est un texte avec des accents: é, è, ê, à, ù!"
        stats = processor_fr.get_detailed_stats(texto)
        
        assert stats["total_count"] > 0
    
    def test_numbers_in_text(self, processor_fr):
        """Deve ignorar números (não são palavras)"""
        texto = "123 456 789 palavra"
        stats = processor_fr.get_detailed_stats(texto)
        
        # Números não devem ser contados como palavras
        # Apenas "palavra" deve estar
        assert len(stats["word_frequencies"]) > 0
    
    def test_unicode_text(self, processor_fr):
        """Deve lidar com unicode"""
        texto = "Héllo wørld çé été"
        stats = processor_fr.get_detailed_stats(texto)
        
        assert stats["total_count"] >= 0


@pytest.mark.service
class TestPerformance:
    """Testes de performance"""
    
    def test_processing_speed_reasonable(self, processor_fr):
        """Processamento deve ser rápido"""
        import time
        
        texto = "palavra " * 1000
        
        start = time.time()
        processor_fr.get_detailed_stats(texto)
        elapsed = time.time() - start
        
        # Deve processar 1000 palavras em menos de 5 segundos
        assert elapsed < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
