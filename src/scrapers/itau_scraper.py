from pathlib import Path
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
