from abc import ABC, abstractmethod
from pathlib import Path

class BaseScraper(ABC):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    @abstractmethod
    def run(self, output_dir: Path) -> dict:
        pass
