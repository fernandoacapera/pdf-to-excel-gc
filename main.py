#%%
from criacao_colunas import df
import pymupdf
import re

def importar_pdf(pdf_path: str) -> list:
    with pymupdf.open('pdfs/' + pdf_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])

        find = text.find("Dados do Veículo")

        if find != -1:
            text = text[find:]

        lista_bruta = re.findall(r":(.*?)\n", text)
        print(lista_bruta)


resultado = importar_pdf('EEB1197.pdf')
# %%
