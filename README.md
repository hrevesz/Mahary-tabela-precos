# Mahary — Tabela de Preços Diária

App estático (HTML) que gera as tabelas de preço do dia a partir da
cotação do ouro, para exportar como imagem e enviar por WhatsApp.

## Estrutura
- `index.html` — o app (entra aqui o HTML existente do mahary-tabelas-precos.html)
- `cotacao.json` — cotação do dia, atualizada automaticamente
- `scripts/fetch_gold_price.py` — busca a cotação na bullion-rates.com
- `.github/workflows/atualizar-cotacao.yml` — roda o script todo dia útil às 08h (Brasília) e commita `cotacao.json`

## Setup (uma vez)
1. Criar este repositório no GitHub (público ou privado, tanto faz para Pages).
2. Subir estes arquivos + o `index.html` do app.
3. Settings → Actions → General → Workflow permissions → marcar **Read and write permissions** (senão o Action não consegue commitar).
4. Settings → Pages → Source: Deploy from branch → `main` / `(root)`.
5. (Opcional) Settings → Pages → Custom domain → `tabela.mahary.com.br`,
   e criar um registro CNAME no DNS do domínio apontando para
   `SEU-USUARIO.github.io`.
6. Testar a Action manualmente: aba Actions → "Atualizar cotação do ouro" → Run workflow.

## Atualização manual
Se quiser forçar a cotação sem esperar o horário, é só rodar o
workflow manualmente (passo 6 acima) ou rodar localmente:
```
pip install requests beautifulsoup4
python scripts/fetch_gold_price.py
```
