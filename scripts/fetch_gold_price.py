#!/usr/bin/env python3
"""
Busca a cotação mais recente do ouro em BRL na bullion-rates.com
e grava em cotacao.json na raiz do repo, para o app de tabela de
preços ler direto (fetch) no carregamento da página.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://pt.bullion-rates.com/gold/BRL-history.htm"
OUT_FILE = Path(__file__).resolve().parent.parent / "cotacao.json"

# Casa com: DD/MM/AA <preço/g> <preço/oz> — funciona tanto em tabela HTML
# normal (get_text) quanto se o layout usar separadores tipo "|".
ROW_PATTERN = re.compile(
    r"(\d{2}/\d{2}/\d{2})[\s|]+([\d]{1,3}(?:\.\d{3})*,\d{2})[\s|]+([\d]{1,3}(?:\.\d{3})*,\d{2})"
)


def parse_brl(value: str) -> float:
    """Converte '712,10' (formato BR) para 712.10 (float)."""
    return float(value.replace(".", "").replace(",", "."))


def main() -> int:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MaharyPriceBot/1.0)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ")
    matches = ROW_PATTERN.findall(text)

    if not matches:
        print(
            "Nenhuma linha de cotação encontrada — o layout da página pode "
            "ter mudado. Ajuste o ROW_PATTERN em fetch_gold_price.py.",
            file=sys.stderr,
        )
        return 1

    # A última ocorrência no texto é a data mais recente da tabela.
    date_str, price_gram_str, price_oz_str = matches[-1]
    price_gram = parse_brl(price_gram_str)
    price_oz = parse_brl(price_oz_str)

    data = {
        "data_cotacao": date_str,  # data da cotação (formato DD/MM/AA, como na fonte)
        "preco_grama_brl": price_gram,
        "preco_onca_brl": price_oz,
        "fonte": URL,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }

    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Cotação atualizada: {date_str} -> R$ {price_gram}/g (fonte: {URL})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
