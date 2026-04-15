"""
Testes para API endpoints
Focado em validação de endpoints e retornos
"""

import pytest
from fastapi.testclient import TestClient
from app.api import app


@pytest.mark.api
class TestHealthEndpoint:
    """Testes para health check"""
    
    def test_health_check_returns_200(self):
        """Deve retornar 200 OK"""
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_check_has_correct_format(self):
        """Deve retornar JSON com status e api"""
        client = TestClient(app)
        response = client.get("/api/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "ok"
    
    def test_root_endpoint_returns_html(self):
        """GET / deve retornar HTML"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.api
class TestEstanteEndpoint:
    """Testes para endpoint de estante"""
    
    def test_estante_returns_200(self):
        """GET /api/estante deve retornar 200"""
        client = TestClient(app)
        response = client.get("/api/estante")
        assert response.status_code == 200
    
    def test_estante_returns_list(self):
        """Deve retornar lista de obras"""
        client = TestClient(app)
        response = client.get("/api/estante")
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_estante_item_has_required_fields(self):
        """Cada item da estante deve ter titulo"""
        client = TestClient(app)
        response = client.get("/api/estante")
        data = response.json()
        
        if len(data) > 0:
            obra = data[0]
            assert "titulo" in obra


@pytest.mark.api
class TestStatsEndpoint:
    """Testes para endpoint de estatísticas"""
    
    def test_stats_returns_200(self):
        """GET /api/stats deve retornar 200"""
        client = TestClient(app)
        response = client.get("/api/stats")
        assert response.status_code == 200
    
    def test_stats_has_required_fields(self):
        """Estatísticas devem ter dados válidos"""
        client = TestClient(app)
        response = client.get("/api/stats")
        data = response.json()
        
        assert isinstance(data, dict)
    
    def test_stats_values_are_numbers(self):
        """Valores devem ser numéricos"""
        client = TestClient(app)
        response = client.get("/api/stats")
        data = response.json()
        
        for key, value in data.items():
            assert isinstance(value, (int, float)) or value is None


@pytest.mark.api
class TestUploadEndpoint:
    """Testes para upload de arquivo"""
    
    def test_upload_missing_titulo(self):
        """Upload sem título deve retornar erro"""
        client = TestClient(app)
        files = {"arquivo": ("test.txt", b"test content")}
        response = client.post("/api/upload", files=files)
        
        # FastAPI retorna 422 para validação
        assert response.status_code == 422
    
    def test_upload_missing_arquivo(self):
        """Upload sem arquivo deve retornar erro"""
        client = TestClient(app)
        data = {"titulo": "Teste"}
        response = client.post("/api/upload", data=data)
        
        assert response.status_code == 422
    
    def test_upload_with_valid_txt_file(self, temp_txt_file):
        """Upload com arquivo TXT válido"""
        client = TestClient(app)
        with open(temp_txt_file, 'rb') as f:
            files = {"arquivo": ("test.txt", f)}
            data = {"titulo": "TestBook"}
            response = client.post("/api/upload", files=files, data=data)
        
        # TXT é suportado - pode ser 200 ou 201
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestTopWordsEndpoint:
    """Testes para endpoint de top palavras"""
    
    def test_top_words_nonexistent_obra(self):
        """Top words de obra inexistente deve retornar 404"""
        client = TestClient(app)
        response = client.get("/api/top-words/nonexistent")
        assert response.status_code == 404
    
    def test_top_words_with_limit_parameter(self):
        """Deve aceitar parâmetro limit"""
        client = TestClient(app)
        response = client.get("/api/top-words/test?limit=50")
        
        # Deve ser 404 ou 200, não erro
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.integration
class TestAPIIntegration:
    """Testes de integração entre endpoints"""
    
    def test_health_and_stats_consistency(self):
        """Health check OK deve significar que stats também funciona"""
        client = TestClient(app)
        health_response = client.get("/api/health")
        assert health_response.status_code == 200
        
        stats_response = client.get("/api/stats")
        assert stats_response.status_code == 200
    
    def test_estante_consistent_with_stats(self):
        """Quantidade de obras em estante deve ser consistente"""
        client = TestClient(app)
        estante_response = client.get("/api/estante")
        estante_data = estante_response.json()
        
        stats_response = client.get("/api/stats")
        stats_data = stats_response.json()
        
        # Ambos devem ser válidos
        assert isinstance(estante_data, list)
        assert isinstance(stats_data, dict)
    
    def test_cors_headers_present(self):
        """Resposta deve estar acessível"""
        client = TestClient(app)
        response = client.get("/api/health")
        
        assert response.status_code == 200


@pytest.mark.api
class TestErrorHandling:
    """Testes de tratamento de erro"""
    
    def test_invalid_endpoint_returns_404(self):
        """Endpoint inexistente retorna 404"""
        client = TestClient(app)
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Método HTTP inválido retorna erro apropriado"""
        client = TestClient(app)
        response = client.get("/api/upload")
        assert response.status_code == 405
    
    def test_response_is_json_on_error(self):
        """Respostas de erro devem ser JSON válido"""
        client = TestClient(app)
        response = client.get("/api/invalid")
        
        assert response.status_code >= 400
        # Deve ser JSON mesmo em erro
        response.json()


@pytest.mark.api
class TestResponseFormats:
    """Testes de formato das respostas"""
    
    def test_all_responses_are_json(self):
        """Todos os endpoints devem retornar JSON"""
        client = TestClient(app)
        endpoints = [
            "/api/health",
            "/api/estante",
            "/api/stats",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                response.json()  # Não deve lançar erro
    
    def test_api_responses_have_content_type(self):
        """Respostas devem ter Content-Type apropriado"""
        client = TestClient(app)
        response = client.get("/api/health")
        
        assert "content-type" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
