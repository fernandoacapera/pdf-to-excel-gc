
#%%
import pandas as pd
import pymupdf
import re

def extrair_pdf(pdf_path: str) -> list:

    with pymupdf.open('pdfs/' + pdf_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])

    find = text.find("Dados do Veículo")
    if find != -1:
        text = text[find:]

    lista_bruta = re.findall(r"\n(.*?):", text)

    padrao_data = r"\d{2}/\d{2}/\d{4}"


    lista_limpa = [item for item in lista_bruta if not re.match(padrao_data, item.strip())]

    return lista_limpa



try:

    resultado = extrair_pdf('EEB1197.pdf')
    print(resultado)

except Exception as e:
    print(f"Erro ao abrir o arquivo: {e}")
# %%
def criar_colunas(resultado: list):
    df = pd.DataFrame()

    for v in resultado:
        df[v] = None

    return df

df = criar_colunas(resultado)
# %%
