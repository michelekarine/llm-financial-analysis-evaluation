import sqlite3
import pandas as pd
from pathlib import Path

class DatabaseHandler:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicadores_financeiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco TEXT,
                periodo TEXT,
                lucro_liquido_recorrente_mi REAL,
                roe_anualizado REAL,
                carteira_credito_bi REAL,
                margem_financeira_clientes_mi REAL,
                indice_eficiencia REAL,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_metrics(self, data: dict):
        if not data or not data.get("banco"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO indicadores_financeiros (
                banco, periodo, lucro_liquido_recorrente_mi, roe_anualizado,
                carteira_credito_bi, margem_financeira_clientes_mi, indice_eficiencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("banco"),
            data.get("periodo"),
            data.get("lucro_liquido_recorrente_mi"),
            data.get("roe_anualizado"),
            data.get("carteira_credito_bi"),
            data.get("margem_financeira_clientes_mi"),
            data.get("indice_eficiencia")
        ))
        conn.commit()
        conn.close()

    def fetch_all(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM indicadores_financeiros", conn)
        conn.close()
        return df
