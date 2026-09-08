from src.config import URLS
from src.scrapers.itau_scraper import ItauScraper

def test_itau_scraper_init():
    scraper = ItauScraper(URLS["itau"])
    assert scraper.name == "Itau"
    assert scraper.url == URLS["itau"]
