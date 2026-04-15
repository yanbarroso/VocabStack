"""
API Routes - Endpoints da aplicação
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
from typing import List, Dict

from app.core import db, processor, DEFAULT_LANG_NAME
from app.models import ProcessamentoResult, WorkMetadata
from app.utils import ReaderFactory

router = APIRouter(prefix="/api", tags=["obras"])

# Limite máximo de tamanho de arquivo: 50 MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Extensões permitidas e seus MIME types correspondentes
ALLOWED_EXTENSIONS = {".epub", ".pdf", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/epub+zip",
    "application/pdf",
    "text/plain",
    # Alguns sistemas enviam MIME genérico para epub/pdf
    "application/octet-stream",
}


def _validar_arquivo(arquivo: UploadFile) -> None:
    """
    Valida extensão e MIME type do arquivo enviado.

    Raises:
        HTTPException 400: se extensão ou MIME type não forem permitidos
        HTTPException 413: se o arquivo exceder MAX_FILE_SIZE
    """
    ext = os.path.splitext(arquivo.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensão '{ext}' não suportada. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    if arquivo.content_type and arquivo.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo '{arquivo.content_type}' não permitido.",
        )


@router.post("/upload", response_model=Dict)
async def upload_obra(titulo: str = Form(...), arquivo: UploadFile = File(...)):
    """
    Faz upload de uma obra e a processa.

    Args:
        titulo: Título da obra
        arquivo: Arquivo a processar (EPUB, PDF, TXT) — máximo 50 MB

    Returns:
        Status do processamento
    """
    _validar_arquivo(arquivo)

    temp_path = f"data/temp_{arquivo.filename}"

    try:
        # Salvar arquivo temporário verificando tamanho durante a escrita
        tamanho = 0
        with open(temp_path, "wb") as buffer:
            while chunk := await arquivo.read(1024 * 1024):  # lê 1 MB por vez
                tamanho += len(chunk)
                if tamanho > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Arquivo excede o limite de {MAX_FILE_SIZE // (1024 * 1024)} MB.",
                    )
                buffer.write(chunk)

        # Ler e processar arquivo
        leitor = ReaderFactory.get_reader(temp_path)
        texto = leitor.extract_text(temp_path)
        stats = processor.get_detailed_stats(texto)

        # Salvar no banco de dados
        tipo = os.path.splitext(arquivo.filename)[1][1:].upper()
        db.salvar_processamento(
            titulo=titulo,
            tipo=tipo,
            idioma=DEFAULT_LANG_NAME,
            total=stats["total_count"],
            freq_dict=stats["word_frequencies"],
        )

        return {"status": "success", "titulo": titulo, "total_palavras": stats["total_count"]}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/estante", response_model=List[Dict])
async def get_estante():
    """
    Lista todas as obras processadas.

    Returns:
        Lista de obras com título, total de palavras e data
    """
    try:
        obras = db.listar_estante()
        return [
            {"titulo": obra[0], "total": obra[1], "data": obra[2]}
            for obra in obras
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar estante: {str(e)}")


@router.get("/top-words/{titulo}")
async def get_top_words(titulo: str, limit: int = 100):
    """
    Obtém as palavras mais frequentes de uma obra.

    Args:
        titulo: Título da obra
        limit: Número de palavras a retornar (padrão: 100)

    Returns:
        Lista de palavras mais frequentes
    """
    obra = db.obter_obra(titulo)
    if not obra:
        raise HTTPException(status_code=404, detail=f"Obra '{titulo}' não encontrada")

    palavras = db.obter_palavras_obra(obra["id"], limit)
    return {"titulo": titulo, "palavras": palavras}


@router.get("/stats")
async def get_global_stats():
    """
    Obtém estatísticas globais de todas as obras.

    Returns:
        Estatísticas agregadas
    """
    try:
        obras = db.listar_estante()
        total_obras = len(obras)
        total_palavras = sum(obra[1] for obra in obras)

        return {
            "total_obras": total_obras,
            "total_palavras": total_palavras,
            "media_palavras_por_obra": total_palavras / total_obras if total_obras > 0 else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "ok", "api": "VocabStack v1.0"}
