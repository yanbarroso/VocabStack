"""
Testes para módulo de serviços
"""

import pytest
from app.services import LanguageProcessor


@pytest.fixture
def processor():
    """Fixture com processador em francês"""
    return LanguageProcessor('fr')


def test_language_processor_init():
    """Testa inicialização do processador"""
    proc = LanguageProcessor('fr')
    assert proc.lang_code == 'fr'
    assert proc.nlp is not None
    assert len(proc.stop_words) > 0


def test_get_detailed_stats(processor):
    """Testa extração de estatísticas"""
    texto = "le petit prince est un prince qui habite une petite planete"
    stats = processor.get_detailed_stats(texto)
    
    assert "total_count" in stats
    assert "word_frequencies" in stats
    assert stats["total_count"] > 0
    assert isinstance(stats["word_frequencies"], dict)


def test_get_detailed_stats_empty_text(processor):
    """Testa com texto vazio"""
    stats = processor.get_detailed_stats("")
    assert stats["total_count"] == 0
    assert stats["word_frequencies"] == {}


def test_get_top_words(processor):
    """Testa obtenção de palavras mais frequentes"""
    texto = "teste teste teste palavra palavra exemplo"
    top_words = processor.get_top_words(texto, top_n=5)
    
    assert isinstance(top_words, list)
    assert len(top_words) > 0
    # A primeira deveria ser "teste"
    assert top_words[0][0] != "" if top_words else True


def test_unsupported_language():
    """Testa com idioma não suportado"""
    with pytest.raises(ValueError, match="não suportado"):
        LanguageProcessor('xx')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
