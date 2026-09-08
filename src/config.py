from pathlib import Path

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
