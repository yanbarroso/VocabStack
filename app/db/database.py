"""
Database - Camada de acesso a dados
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple

__all__ = ["DatabaseManager"]


class DatabaseManager:
    """Gerenciador centralizado do banco de dados SQLite"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa o DatabaseManager
        
        Args:
            db_path: Caminho do arquivo DB. Se None, usa variável de ambiente ou padrão.
        """
        if db_path is None:
            db_path = os.getenv("DATABASE_URL", "data/vocabstack.db")
        
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_name = db_path
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Abre uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_name)

    def _create_tables(self) -> None:
        """Cria as tabelas necessárias se não existirem"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS obras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL UNIQUE,
                    tipo TEXT NOT NULL,
                    idioma TEXT NOT NULL,
                    total_palavras INTEGER NOT NULL,
                    data_leitura TIMESTAMP NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS palavras_vistas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    obra_id INTEGER NOT NULL,
                    palavra TEXT NOT NULL,
                    frequencia INTEGER NOT NULL,
                    FOREIGN KEY (obra_id) REFERENCES obras (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def salvar_processamento(
        self, 
        titulo: str, 
        tipo: str, 
        idioma: str, 
        total: int, 
        freq_dict: Dict[str, int]
    ) -> int:
        """
        Salva um novo processamento no banco de dados
        
        Args:
            titulo: Título da obra
            tipo: Tipo de arquivo (PDF, EPUB, etc)
            idioma: Idioma detectado
            total: Total de palavras
            freq_dict: Dicionário com frequências das palavras
            
        Returns:
            ID da obra inserida
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO obras (titulo, tipo, idioma, total_palavras, data_leitura) VALUES (?, ?, ?, ?, ?)",
                    (titulo, tipo, idioma, total, datetime.now())
                )
                obra_id = cursor.lastrowid
                
                # Inserir frequências das palavras
                dados = [(obra_id, palavra, freq) for palavra, freq in freq_dict.items()]
                cursor.executemany(
                    "INSERT INTO palavras_vistas (obra_id, palavra, frequencia) VALUES (?, ?, ?)", 
                    dados
                )
                conn.commit()
                return obra_id
            except sqlite3.IntegrityError:
                raise ValueError(f"Obra '{titulo}' já existe no banco de dados")

    def listar_estante(self) -> List[Tuple[str, int, str]]:
        """
        Lista todas as obras processadas
        
        Returns:
            Lista de tuplas (titulo, total_palavras, data_leitura)
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT titulo, total_palavras, data_leitura FROM obras ORDER BY data_leitura DESC"
            )
            return cursor.fetchall()

    def obter_obra(self, titulo: str) -> Dict:
        """Obtém detalhes de uma obra específica"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, titulo, tipo, idioma, total_palavras, data_leitura FROM obras WHERE titulo = ?",
                (titulo,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "titulo": row[1],
                    "tipo": row[2],
                    "idioma": row[3],
                    "total_palavras": row[4],
                    "data_leitura": row[5]
                }
            return None

    def obter_palavras_obra(self, obra_id: int, limite: int = 100) -> List[Dict]:
        """Obtém as palavras mais frequentes de uma obra"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT palavra, frequencia FROM palavras_vistas WHERE obra_id = ? ORDER BY frequencia DESC LIMIT ?",
                (obra_id, limite)
            )
            return [{"palavra": row[0], "frequencia": row[1]} for row in cursor.fetchall()]

    def limpar_banco(self) -> None:
        """Limpa todas as tabelas (apenas para testes/desenvolvimento)"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM palavras_vistas")
            conn.execute("DELETE FROM obras")
            conn.commit()
