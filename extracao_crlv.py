# extracao_crlv.py

import os
import re
import glob
import pdfplumber
import pandas as pd

# Pasta com os PDFs (ajuste se necessário)
PASTA = "/content"

# ---- Helpers ---------------------------------------------------------------

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().upper()

def _proxima_linha_valida(linhas_norm, linhas_orig, start_idx, max_lookahead=8):
    """Volta a linha ORIGINAL correspondente ao próximo conteúdo não vazio/NULL."""
    j = start_idx
    limite = min(len(linhas_norm), start_idx + max_lookahead + 1)
    while j < limite and (linhas_norm[j] == "" or linhas_norm[j] == "NULL"):
        j += 1
    if j < len(linhas_orig):
        return linhas_orig[j].strip()
    return None

# Padrões úteis
PLACA_RE = re.compile(r"\b([A-Z]{3}\d{4}|[A-Z]{3}\d[A-Z]\d{2})\b")  # ABC1234 ou ABC1D23 (Mercosul)
ANO_RE   = re.compile(r"\b(19|20)\d{2}\b")
RENAVAM_RE = re.compile(r"\b\d{9,12}\b")  # RENAVAM 9-12 dígitos

# ---- Extração por rótulo ---------------------------------------------------

def extrair_campos_crlv(pdf_file: str) -> dict:
    """
    Extrai campos do CRLV digital.
    Campos: RENAVAM, PLACA, ANO FABRICAÇÃO, ANO MODELO, MARCA/MODELO/VERSÃO, COR, CHASSI
    """
    alvo_labels = {
        "renavam": "CÓDIGO RENAVAM",
        "placa": "PLACA",
        "ano_fabricacao": "ANO FABRICAÇÃO",
        "ano_modelo": "ANO MODELO",
        "marca_modelo_versao": "MARCA / MODELO / VERSÃO",
        "cor_predominante": "COR PREDOMINANTE",
        "teste_chassi": "Chassi"
    }

    res = {k: None for k in alvo_labels.keys()}

    with pdfplumber.open(pdf_file) as pdf:
        linhas_orig = []
        for p in pdf.pages:
            texto = p.extract_text(x_tolerance=1, y_tolerance=1) or ""
            linhas_orig.extend(texto.splitlines())

    linhas_norm = [_normalize(l) for l in linhas_orig]

    idxs = {}
    for i, ln in enumerate(linhas_norm):
        for chave, rotulo in alvo_labels.items():
            if chave in idxs:
                continue
            if _normalize(rotulo) in ln:
                idxs[chave] = i

    # ---- RENAVAM ----
    if "renavam" in idxs:
        start = idxs["renavam"] + 1
        bloco = " ".join(linhas_orig[start:start+6])
        m = RENAVAM_RE.search(bloco.replace(".", "").replace(" ", ""))
        if not m:
            m = RENAVAM_RE.search(" ".join(linhas_orig))
        if m:
            res["renavam"] = m.group(0)

    # ---- PLACA ----
    if "placa" in idxs:
        start = idxs["placa"]
        bloco = " ".join(linhas_orig[start:start+6])
        m = PLACA_RE.search(_normalize(bloco))
        if not m:
            m = PLACA_RE.search(" ".join(_normalize(l) for l in linhas_orig))
        if m:
            res["placa"] = m.group(1)

    # ---- ANO FABRICAÇÃO ----
    if "ano_fabricacao" in idxs:
        cand = _proxima_linha_valida(linhas_norm, linhas_orig, idxs["ano_fabricacao"] + 1)
        if cand:
            m = ANO_RE.search(cand)
            if m: res["ano_fabricacao"] = m.group(0)
        if not res["ano_fabricacao"]:
            for off in range(2, 8):
                j = idxs["ano_fabricacao"] + off
                if j < len(linhas_orig):
                    m = ANO_RE.search(linhas_orig[j])
                    if m:
                        res["ano_fabricacao"] = m.group(0)
                        break

    # ---- ANO MODELO ----
    if "ano_modelo" in idxs:
        cand = _proxima_linha_valida(linhas_norm, linhas_orig, idxs["ano_modelo"] + 1)
        if cand:
            m = ANO_RE.search(cand)
            if m: res["ano_modelo"] = m.group(0)
        if not res["ano_modelo"]:
            for off in range(2, 8):
                j = idxs["ano_modelo"] + off
                if j < len(linhas_orig):
                    m = ANO_RE.search(linhas_orig[j])
                    if m:
                        res["ano_modelo"] = m.group(0)
                        break

    # ---- MARCA/MODELO/VERSÃO ----
    if "marca_modelo_versao" in idxs:
        val = _proxima_linha_valida(linhas_norm, linhas_orig, idxs["marca_modelo_versao"] + 4)
        if val:
            res["marca_modelo_versao"] = val

    # ---- COR ----
    if "cor_predominante" in idxs:
        val = _proxima_linha_valida(linhas_norm, linhas_orig, idxs["cor_predominante"] + 3)
        if val:
            res["cor_predominante"] = _normalize(val).title()

    # ---- CHASSI ----
    if "teste_chassi" in idxs:
        val = _proxima_linha_valida(linhas_norm, linhas_orig, idxs["teste_chassi"] + 3)
        if val:
            res["teste_chassi"] = _normalize(val).title()

    return res

# ---- Loop na pasta e impressão --------------------------------------------

pdfs = sorted(glob.glob(os.path.join(PASTA, "*.pdf")))
if not pdfs:
    print(f"Nenhum PDF encontrado em {PASTA!r}.")
else:
    resultados = []
    for pdf_file in pdfs:
        campos = extrair_campos_crlv(pdf_file)
        linha = {"arquivo": os.path.basename(pdf_file), **campos}
        resultados.append(linha)
        print(f"{linha['arquivo']}: "
              f"RENAVAM={linha['renavam']}, "
              f"PLACA={linha['placa']}, "
              f"ANO FABRICAÇÃO={linha['ano_fabricacao']}, "
              f"ANO MODELO={linha['ano_modelo']}, "
              f"MARCA/MODELO/VERSÃO={linha['marca_modelo_versao']}, "
              f"COR={linha['cor_predominante']}, "
              f"CHASSI={linha['teste_chassi']}")

    # (Opcional) Salvar em Excel/CSV:
import pandas as pd
df = pd.DataFrame(resultados)
df.to_excel("/content/resultado_crlv.xlsx", index=False)
df.to_csv("/content/resultado_crlv.csv", index=False, encoding="utf-8-sig")
print("Planilhas salvas em /content/resultado_crlv.xlsx e /content/resultado_crlv.csv")
