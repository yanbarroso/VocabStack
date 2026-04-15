"""
API - Aplicação FastAPI principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.routes import router

# Criar aplicação FastAPI
app = FastAPI(
    title="VocabStack",
    description="Processador de Vocabulário e Análise Textual",
    version="1.0.0"
)

# Middleware CORS - Permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Incluir rotas da API
app.include_router(router)


@app.get("/")
async def serve_index():
    """Serve o frontend HTML"""
    if os.path.exists("index.html"):
        return FileResponse("index.html", media_type="text/html")
    return {"error": "Frontend não encontrado"}


@app.get("/health")
async def health():
    """Health check geral"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
