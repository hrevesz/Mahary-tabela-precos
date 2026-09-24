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

# Casa com: DD/MM/AA <preço/g com vírgula decimal> <preço/oz, que na
# fonte vem só como inteiro com ponto de milhar, sem decimal>.
ROW_PATTERN = re.compile(
    r"(\d{2}/\d{2}/\d{2})\s+([\d]{1,3}(?:\.\d{3})*,\d{2})\s+([\d]{1,3}(?:\.\d{3})*(?:,\d{2})?)"
)


def parse_brl(value: str) -> float:
    """Converte '712,10' (formato BR) para 712.10 (float)."""
    return float(value.replace(".", "").replace(",", "."))


def main() -> int:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }
    resp = requests.get(URL, headers=headers, timeout=20)

    print(f"[diagnóstico] status HTTP: {resp.status_code}", file=sys.stderr)
    print(f"[diagnóstico] tamanho da resposta: {len(resp.text)} chars", file=sys.stderr)

    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ")
    # Colapsa espaços múltiplos/quebras de linha em um só espaço, e troca
    # espaço não separável (comum em tabelas) por espaço normal.
    text_clean = re.sub(r"[\s\xa0]+", " ", text)
    matches = ROW_PATTERN.findall(text_clean)

    if not matches:
        # Amostra em volta da primeira data DD/MM/AA que aparecer no texto,
        # pra ver exatamente como o número está formatado ali do lado.
        sample_match = re.search(r"\d{2}/\d{2}/\d{2}.{0,80}", text_clean)
        sample = sample_match.group(0) if sample_match else text_clean[:300]
        print(
            "Nenhuma linha de cotação encontrada — o layout da página pode "
            "ter mudado, ou o conteúdo é montado via JavaScript (o requests "
            "não executa JS). Amostra do texto recebido perto de uma data:",
            file=sys.stderr,
        )
        print(f"[diagnóstico] amostra: {sample!r}", file=sys.stderr)
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
