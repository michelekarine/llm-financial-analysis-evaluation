import argparse
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

        print("\n--- Resultados Salvos no Banco de Dados ---")
        df = db.fetch_all()
        print(df)

if __name__ == "__main__":
    main()
