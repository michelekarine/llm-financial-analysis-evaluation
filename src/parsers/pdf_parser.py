import pdfplumber
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
