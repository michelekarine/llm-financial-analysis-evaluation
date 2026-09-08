# -*- coding: utf-8 -*-
import os

files_content = {
    "requirements.txt": """playwright>=1.40.0
beautifulsoup4>=4.12.2
pdfplumber>=0.10.3
pandas>=2.1.4
requests>=2.31.0
pytest>=7.4.3
python-dotenv>=1.0.0
""",
    ".gitignore": """venv/
.venv/
__pycache__/
*.py[cod]
*.sqlite3
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
.vscode/
.idea/
*.log
.pytest_cache/
.env
""",
    "src/__init__.py": "",
    "src/config.py": """from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = DATA_PROCESSED_DIR / "financial_data.db"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "itau": "https://www.itau.com.br/relacoes-com-investidores/resultados-e-relatorios/central-de-resultados/",
    "bradesco": "https://www.bradescori.com.br/informacoes-ao-mercado/central-de-resultados/",
    "santander": "https://www.santander.com.br/ri/resultados-e-relatorios/divulgacao-de-resultados/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
""",
    "src/scrapers/__init__.py": """from .base_scraper import BaseScraper
from .itau_scraper import ItauScraper
from .bradesco_scraper import BradescoScraper
from .santander_scraper import SantanderScraper

__all__ = ["BaseScraper", "ItauScraper", "BradescoScraper", "SantanderScraper"]
""",
    "src/scrapers/base_scraper.py": """from abc import ABC, abstractmethod
from pathlib import Path

class BaseScraper(ABC):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    @abstractmethod
    def run(self, output_dir: Path) -> dict:
        pass
""",
    "src/scrapers/itau_scraper.py": """from pathlib import Path
from playwright.sync_api import sync_playwright
from src.scrapers.base_scraper import BaseScraper
from src.config import HEADERS

class ItauScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__("Itau", url)

    def run(self, output_dir: Path) -> dict:
        downloaded_files = []
        print(f"[{self.name}] Iniciando raspagem dinâmica...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)

                links = page.query_selector_all("a[href*='.pdf']")
                for link in links:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip()
                    
                    if href and ("Analise" in text or "Demonstracoes" in text or "Resultado" in text or "BRGAAP" in href):
                        pdf_url = href if href.startswith("http") else f"https://www.itau.com.br{href}"
                        pdf_name = f"itau_{pdf_url.split('/')[-1]}"
                        dest_path = output_dir / pdf_name

                        response = page.request.get(pdf_url)
                        if response.status == 200:
                            dest_path.write_bytes(response.body())
                            downloaded_files.append(str(dest_path))
                            print(f"[{self.name}] Download concluído: {pdf_name}")
                            break
            except Exception as e:
                print(f"[{self.name}] Erro na raspagem: {e}")
            finally:
                browser.close()

        return {"bank": self.name, "files": downloaded_files}
""",
    "src/scrapers/bradesco_scraper.py": """from pathlib import Path
from playwright.sync_api import sync_playwright
from src.scrapers.base_scraper import BaseScraper
from src.config import HEADERS

class BradescoScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__("Bradesco", url)

    def run(self, output_dir: Path) -> dict:
        downloaded_files = []
        print(f"[{self.name}] Iniciando raspagem dinâmica...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                
                links = page.query_selector_all("a[href*='.pdf']")
                for link in links:
                    href = link.get_attribute("href")
                    if href and ("DG" in href or "relatorio" in href.lower() or "1t" in href.lower() or "4t" in href.lower()):
                        pdf_url = href if href.startswith("http") else f"https://www.bradescori.com.br{href}"
                        pdf_name = f"bradesco_{pdf_url.split('/')[-1]}"
                        dest_path = output_dir / pdf_name

                        res = page.request.get(pdf_url)
                        if res.status == 200:
                            dest_path.write_bytes(res.body())
                            downloaded_files.append(str(dest_path))
                            print(f"[{self.name}] Download concluído: {pdf_name}")
                            break
            except Exception as e:
                print(f"[{self.name}] Erro na raspagem: {e}")
            finally:
                browser.close()

        return {"bank": self.name, "files": downloaded_files}
""",
    "src/scrapers/santander_scraper.py": """from pathlib import Path
from playwright.sync_api import sync_playwright
from src.scrapers.base_scraper import BaseScraper
from src.config import HEADERS

class SantanderScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__("Santander", url)

    def run(self, output_dir: Path) -> dict:
        downloaded_files = []
        print(f"[{self.name}] Iniciando raspagem dinâmica...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)

                links = page.query_selector_all("a[href*='.pdf']")
                for link in links:
                    href = link.get_attribute("href")
                    if href and ("demdemonstracoes" in href.lower() or "relatorio" in href.lower() or "resultado" in href.lower()):
                        pdf_url = href if href.startswith("http") else f"https://www.santander.com.br{href}"
                        pdf_name = f"santander_{pdf_url.split('/')[-1]}"
                        dest_path = output_dir / pdf_name

                        res = page.request.get(pdf_url)
                        if res.status == 200:
                            dest_path.write_bytes(res.body())
                            downloaded_files.append(str(dest_path))
                            print(f"[{self.name}] Download concluído: {pdf_name}")
                            break
            except Exception as e:
                print(f"[{self.name}] Erro na raspagem: {e}")
            finally:
                browser.close()

        return {"bank": self.name, "files": downloaded_files}
""",
    "src/parsers/__init__.py": """from .pdf_parser import BankPDFParser

__all__ = ["BankPDFParser"]
""",
    "src/parsers/pdf_parser.py": """import pdfplumber
import re
from pathlib import Path

class BankPDFParser:
    @staticmethod
    def parse_itau_pdf(pdf_path: Path) -> dict:
        metrics = {
            "banco": "Itaú",
            "periodo": "1T26",
            "lucro_liquido_recorrente_mi": None,
            "roe_anualizado": None,
            "carteira_credito_bi": None,
            "margem_financeira_clientes_mi": None,
            "indice_eficiencia": None
        }

        if not pdf_path.exists():
            return metrics

        with pdfplumber.open(pdf_path) as pdf:
            for i in range(min(15, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""

                if not metrics["lucro_liquido_recorrente_mi"]:
                    match_lucro = re.search(r"(?:Resultado Recorrente Gerencial|Lucro Líquido Recorrente)\s*\|?\s*([\d\.]+)", text)
                    if match_lucro:
                        val = match_lucro.group(1).replace(".", "")
                        metrics["lucro_liquido_recorrente_mi"] = float(val)

                if not metrics["roe_anualizado"]:
                    match_roe = re.search(r"(?:Retorno Recorrente Gerencial|ROE|Retorno sobre o Patrimônio Líquido)\s*.*?([\d\,]+)\%", text)
                    if match_roe:
                        metrics["roe_anualizado"] = float(match_roe.group(1).replace(",", "."))

                if not metrics["carteira_credito_bi"]:
                    match_cart = re.search(r"Carteira de Crédito.*?(?:R\$\s*)?([\d\.\,]+)\s*(?:trilhão|bi|bilhões)?", text, re.IGNORECASE)
                    if match_cart:
                        val = match_cart.group(1).replace(".", "").replace(",", ".")
                        try:
                            metrics["carteira_credito_bi"] = float(val)
                        except ValueError:
                            pass

                if not metrics["margem_financeira_clientes_mi"]:
                    match_margem = re.search(r"Margem Financeira com Clientes\s*\|?\s*([\d\.]+)", text)
                    if match_margem:
                        val = match_margem.group(1).replace(".", "")
                        metrics["margem_financeira_clientes_mi"] = float(val)

                if not metrics["indice_eficiencia"]:
                    match_ie = re.search(r"Índice de Eficiência.*?([\d\,]+)\%", text)
                    if match_ie:
                        metrics["indice_eficiencia"] = float(match_ie.group(1).replace(",", "."))

        return metrics
""",
    "src/utils/__init__.py": """from .database import DatabaseHandler

__all__ = ["DatabaseHandler"]
""",
    "src/utils/database.py": """import sqlite3
import pandas as pd
from pathlib import Path

class DatabaseHandler:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(\"\"\"
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
        \"\"\")
        conn.commit()
        conn.close()

    def save_metrics(self, data: dict):
        if not data or not data.get("banco"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(\"\"\"
            INSERT INTO indicadores_financeiros (
                banco, periodo, lucro_liquido_recorrente_mi, roe_anualizado,
                carteira_credito_bi, margem_financeira_clientes_mi, indice_eficiencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
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
""",
    "tests/__init__.py": "",
    "tests/test_parsers.py": """import pytest
from pathlib import Path
from src.parsers.pdf_parser import BankPDFParser

def test_parse_itau_pdf_dummy(tmp_path):
    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_text("Dummy PDF Content")
    
    metrics = BankPDFParser.parse_itau_pdf(dummy_pdf)
    assert isinstance(metrics, dict)
    assert metrics["banco"] == "Itaú"
    assert "lucro_liquido_recorrente_mi" in metrics
""",
    "tests/test_scrapers.py": """from src.config import URLS
from src.scrapers.itau_scraper import ItauScraper

def test_itau_scraper_init():
    scraper = ItauScraper(URLS["itau"])
    assert scraper.name == "Itau"
    assert scraper.url == URLS["itau"]
""",
    "main.py": """import argparse
from pathlib import Path
from src.config import DATA_RAW_DIR, DB_PATH, URLS
from src.scrapers.itau_scraper import ItauScraper
from src.scrapers.bradesco_scraper import BradescoScraper
from src.scrapers.santander_scraper import SantanderScraper
from src.parsers.pdf_parser import BankPDFParser
from src.utils.database import DatabaseHandler

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Raspagem e Análise Financeira Bancária")
    parser.add_argument("--scrape", action="store_true", help="Executa os raspadores web")
    parser.add_argument("--parse-local", type=str, help="Caminho para PDF local existente para teste de parsing")
    args = parser.parse_args()

    db = DatabaseHandler(DB_PATH)
    db.init_db()

    if args.parse_local:
        pdf_file = Path(args.parse_local)
        print(f"--- Processando PDF Local: {pdf_file.name} ---")
        metrics = BankPDFParser.parse_itau_pdf(pdf_file)
        print("Métricas Extraídas:")
        print(metrics)
        db.save_metrics(metrics)
        print("Salvo no SQLite com sucesso!")
        return

    if args.scrape:
        print("--- Iniciando Coleta nos Sites de RI ---")
        scrapers = [
            ItauScraper(URLS["itau"]),
            BradescoScraper(URLS["bradesco"]),
            SantanderScraper(URLS["santander"])
        ]

        for scraper in scrapers:
            res = scraper.run(DATA_RAW_DIR)
            for filepath in res.get("files", []):
                p = Path(filepath)
                if "itau" in p.name.lower():
                    metrics = BankPDFParser.parse_itau_pdf(p)
                    db.save_metrics(metrics)

        print("\\n--- Resultados Salvos no Banco de Dados ---")
        df = db.fetch_all()
        print(df)

if __name__ == "__main__":
    main()
""",
    "data/raw/.gitkeep": "",
    "data/processed/.gitkeep": ""
}

def build_structure():
    print("🚀 Gerando estrutura completa do projeto...")
    for rel_path, content in files_content.items():
        full_path = os.path.abspath(rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        print(f"  ✓ Criado: {rel_path}")
    print("\n✅ Estrutura criada com sucesso!")

if __name__ == "__main__":
    build_structure()