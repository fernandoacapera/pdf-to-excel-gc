import streamlit as st
import pymupdf
import re
import pandas as pd
import io
import gc
import zipfile

# --- 1. Definição das Colunas ---
COLUNAS = [
    'Placa', 'Renavam', 'Ano modelo', 'Marca modelo', 'Ano Fabricação', 'Cor', 'Chassi', 'Remarcação Chassi', 
    'Combustível', 'Tipo', 'Bloqueio de furto', 'Blindagem', 'Bloqueio de guincho', 'Ultimo licenciamento', 
    'Carroceria', 'Arrolamento', 'Restrição Judicial 1', 'Restrição Judicial 2', 'Tribunal', 'Órgão Judicial', 
    'N° Órgão Judicial', 'N° do Processo', 'Nome Proprietário', 'CPF/CNPJ Proprietário', 'Endereço Proprietário', 
    'Bairro Proprietário', 'Número Proprietário', 'Complemento Proprietário', 'CEP Proprietário', 'Municipio Proprietário', 
    'UF Proprietário', 'Data da Inclusão', 'Data da Venda', 'Nome Comprador', 'CPF/CNPJ Comprador', 'Endereço Comprador', 
    'Número Comprador', 'Complemento Comprador', 'Bairro Comprador', 'CEP Comprador', 'Municipio Comprador', 'UF Comprador', 
    'Código da financeira', 'CNPJ Financeira', 'Número do contrato', 'Vigência do contrato', 'CGC Financiado', 'Nome Financeira', 
    'Número do Motor BIN', 'Peso bruto total', 'Restrição 1', 'Restrição 2', 'Restrição 3', 'Restrição 4', 'Chassi regravado', 
    'Situação do veiculo', 'Número do motor', 'Motivo da baixa', 'Data da baixa', 'Hora da baixa', 'Taxa de estadia', 
    'Taxa de guinchamento', 'Taxa de oficio de liberação', 'Débitos de licenciamento', 'Débitos de IPVA', 'Débitos de DPVAT', 
    'Débitos de multa', 'Débitos na divida ativa', 'Débitos total', 'Quant.Multas Municipal', 'Valor das Multas Municipal', 
    'Quant.Multas Detran', 'Valor das Multas Detran', 'Quant.Multas D.E.R', 'Valor das Multas D.E.R', 'Quant. Multas Outros', 
    'Valor das Multas Outros', 
    # Bloqueios 1 a 10
    'Bloqueio 1', 'Tipo Bloqueio 1', 'Descrição Bloqueio 1', 'Municipio Bloqueio 1', 'Número Edital Bloqueio 1', 'Ano Edital Bloqueio 1', 'Autoridade Bloqueio 1' , 'Número Lote Bloqueio 1', 'Número Protocolo Bloqueio 1', 'Ano Protocolo Bloqueio 1', 'Data Inclusão Bloqueio 1', 'Hora Inclusão Bloqueio 1', 'Motivo 1 Bloqueio 1',
    'Bloqueio 2', 'Tipo Bloqueio 2', 'Descrição Bloqueio 2', 'Municipio Bloqueio 2', 'Número Edital Bloqueio 2', 'Ano Edital Bloqueio 2', 'Autoridade Bloqueio 2' , 'Número Lote Bloqueio 2', 'Número Protocolo Bloqueio 2', 'Ano Protocolo Bloqueio 2', 'Data Inclusão Bloqueio 2', 'Hora Inclusão Bloqueio 2', 'Motivo 1 Bloqueio 2',
    'Bloqueio 3', 'Tipo Bloqueio 3', 'Descrição Bloqueio 3', 'Municipio Bloqueio 3', 'Número Edital Bloqueio 3', 'Ano Edital Bloqueio 3', 'Autoridade Bloqueio 3' , 'Número Lote Bloqueio 3', 'Número Protocolo Bloqueio 3', 'Ano Protocolo Bloqueio 3', 'Data Inclusão Bloqueio 3', 'Hora Inclusão Bloqueio 3', 'Motivo 1 Bloqueio 3',
    'Bloqueio 4', 'Tipo Bloqueio 4', 'Descrição Bloqueio 4', 'Municipio Bloqueio 4', 'Número Edital Bloqueio 4', 'Ano Edital Bloqueio 4', 'Autoridade Bloqueio 4' , 'Número Lote Bloqueio 4', 'Número Protocolo Bloqueio 4', 'Ano Protocolo Bloqueio 4', 'Data Inclusão Bloqueio 4', 'Hora Inclusão Bloqueio 4', 'Motivo 1 Bloqueio 4',
    'Bloqueio 5', 'Tipo Bloqueio 5', 'Descrição Bloqueio 5', 'Municipio Bloqueio 5', 'Número Edital Bloqueio 5', 'Ano Edital Bloqueio 5', 'Autoridade Bloqueio 5' , 'Número Lote Bloqueio 5', 'Número Protocolo Bloqueio 5', 'Ano Protocolo Bloqueio 5', 'Data Inclusão Bloqueio 5', 'Hora Inclusão Bloqueio 5', 'Motivo 1 Bloqueio 5',
    'Bloqueio 6', 'Tipo Bloqueio 6', 'Descrição Bloqueio 6', 'Municipio Bloqueio 6', 'Número Edital Bloqueio 6', 'Ano Edital Bloqueio 6', 'Autoridade Bloqueio 6' , 'Número Lote Bloqueio 6', 'Número Protocolo Bloqueio 6', 'Ano Protocolo Bloqueio 6', 'Data Inclusão Bloqueio 6', 'Hora Inclusão Bloqueio 6', 'Motivo 1 Bloqueio 6',
    'Bloqueio 7', 'Tipo Bloqueio 7', 'Descrição Bloqueio 7', 'Municipio Bloqueio 7', 'Número Edital Bloqueio 7', 'Ano Edital Bloqueio 7', 'Autoridade Bloqueio 7' , 'Número Lote Bloqueio 7', 'Número Protocolo Bloqueio 7', 'Ano Protocolo Bloqueio 7', 'Data Inclusão Bloqueio 7', 'Hora Inclusão Bloqueio 7', 'Motivo 1 Bloqueio 7',
    'Bloqueio 8', 'Tipo Bloqueio 8', 'Descrição Bloqueio 8', 'Municipio Bloqueio 8', 'Número Edital Bloqueio 8', 'Ano Edital Bloqueio 8', 'Autoridade Bloqueio 8' , 'Número Lote Bloqueio 8', 'Número Protocolo Bloqueio 8', 'Ano Protocolo Bloqueio 8', 'Data Inclusão Bloqueio 8', 'Hora Inclusão Bloqueio 8', 'Motivo 1 Bloqueio 8',
    'Bloqueio 9', 'Tipo Bloqueio 9', 'Descrição Bloqueio 9', 'Municipio Bloqueio 9', 'Número Edital Bloqueio 9', 'Ano Edital Bloqueio 9', 'Autoridade Bloqueio 9' , 'Número Lote Bloqueio 9', 'Número Protocolo Bloqueio 9', 'Ano Protocolo Bloqueio 9', 'Data Inclusão Bloqueio 9', 'Hora Inclusão Bloqueio 9', 'Motivo 1 Bloqueio 9',
    'Bloqueio 10', 'Tipo Bloqueio 10', 'Descrição Bloqueio 10', 'Municipio Bloqueio 10', 'Número Edital Bloqueio 10', 'Ano Edital Bloqueio 10', 'Autoridade Bloqueio 10' , 'Número Lote Bloqueio 10', 'Número Protocolo Bloqueio 10', 'Ano Protocolo Bloqueio 10', 'Data Inclusão Bloqueio 10', 'Hora Inclusão Bloqueio 10', 'Motivo 1 Bloqueio 10',
    'Transacao ID', 'Data/Hora'
]

# --- 2. Função de Processamento (Recebe os bytes do arquivo) ---
def processar_bytes_pdf(file_bytes) -> list:
    # Abre o PDF a partir da memória
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        text = chr(12).join([page.get_text() for page in doc])
        
        # --- Limpeza e Padronização ---
        match_data = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})", text)
        data_hora_final = match_data.group(1) if match_data else "Não informado"
        
        text = re.sub(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}", "", text)
        text = text.replace("Informamos que os débitos de multas por", "")
        text = text.replace("infrações de trânsito podem apresentar divergências", "")
        text = text.replace("Aviso Importante:", "")

        find = text.find("Placa")
        if find != -1:
            text = text[find:]

        # --- Separar Dados Gerais vs Bloqueios ---
        match_primeiro_bloqueio = re.search(r"(Bloqueio\s+\d+)", text)
        
        if match_primeiro_bloqueio:
            idx_corte = match_primeiro_bloqueio.start()
            texto_geral = text[:idx_corte]
            texto_bloqueios = text[idx_corte:]
            tem_bloqueio = True
        else:
            texto_geral = text
            texto_bloqueios = ""
            tem_bloqueio = False

        # --- Extração Dados Comuns ---
        valores_comuns = re.findall(r":(.*?)\n", texto_geral)
        valores_comuns = [v.strip() if v.strip() != "" else "Não informado" for v in valores_comuns]

        QTD_CAMPOS_COMUNS = 69
        if len(valores_comuns) > QTD_CAMPOS_COMUNS:
            valores_comuns = valores_comuns[:QTD_CAMPOS_COMUNS]
        elif len(valores_comuns) < QTD_CAMPOS_COMUNS:
            valores_comuns.extend(['Não informado'] * (QTD_CAMPOS_COMUNS - len(valores_comuns)))

        # --- Multas ---
        qtd_municipal = '0'; val_municipal = '0,00'
        qtd_detran = '0'; val_detran = '0,00'
        qtd_der = '0'; val_der = '0,00'
        qtd_outros = '0'; val_outros = '0,00'

        padrao_multa = r"(MUNICIPAL|DETRAN|D\.?E\.?R\.?|PRF|RENAINF|AMBIENTAL)\s+(\d+|J)\s+(?:R\$\s*)?([\d.,]+)"
        multas = re.findall(padrao_multa, text)
        
        for orgao, qtd, valor in multas:
            if "MUNICIPAL" in orgao: qtd_municipal = qtd; val_municipal = valor
            elif "DETRAN" in orgao: qtd_detran = qtd; val_detran = valor
            elif "D.E.R." in orgao or "DER" in orgao: qtd_der = qtd; val_der = valor
            else: qtd_outros = qtd; val_outros = valor

        novos_valores = [qtd_municipal, val_municipal, qtd_detran, val_detran, qtd_der, val_der, qtd_outros, val_outros]
        valores_comuns.extend(novos_valores)

        # --- Bloqueios ---
        dados_todos_bloqueios = []
        
        campos_bloqueio = [
            'Tipo', 'Descrição', 'Município',
            'Número Edital', 'Ano Edital', 'Autoridade',
            'Número Lote', 'Número Protocolo', 'Ano Protocolo',
            'Data Inclusão', 'Hora Inclusão', 'Motivo 1'
        ]
        
        regex_freio = "|".join([c.replace(" ", r"\s+") for c in campos_bloqueio])

        if tem_bloqueio:
            matches = list(re.finditer(r"Bloqueio\s+(\d+)", texto_bloqueios))
            matches = matches[:10]
            
            for i, match in enumerate(matches):
                num_bloqueio = match.group(1)
                inicio = match.start()
                fim = matches[i+1].start() if i+1 < len(matches) else len(texto_bloqueios)
                chunk_bloqueio = texto_bloqueios[inicio:fim]
                dados_todos_bloqueios.append(num_bloqueio)
                
                for campo in campos_bloqueio:
                    padrao = fr"{campo}:\s*(.*?)(?=\n|\s*(?:{regex_freio}):|$)"
                    match_campo = re.search(padrao, chunk_bloqueio, re.IGNORECASE)
                    valor = "Não informado"
                    if match_campo:
                        valor_extraido = match_campo.group(1).strip()
                        if ":" in valor_extraido:
                             parte_limpa = valor_extraido.split(":")[0]
                             eh_nome_campo = any(k.upper() in parte_limpa.upper() for k in campos_bloqueio)
                             if not eh_nome_campo and len(parte_limpa) > 0: valor = parte_limpa
                        elif valor_extraido != "":
                            valor = valor_extraido
                    dados_todos_bloqueios.append(valor)

        TOTAL_SLOTS_BLOQUEIO = 10 * 13 
        qtd_atual = len(dados_todos_bloqueios)
        if qtd_atual < TOTAL_SLOTS_BLOQUEIO:
            faltam = TOTAL_SLOTS_BLOQUEIO - qtd_atual
            dados_todos_bloqueios.extend(['Não informado'] * faltam)
            
        linha_completa = valores_comuns + dados_todos_bloqueios
        transacao_id = re.search(r"Transação Id:\s*(.*?)\n", text)
        valor_transacao = transacao_id.group(1).strip() if transacao_id else "Não informado"
        linha_completa.append(valor_transacao)
        linha_completa.append(data_hora_final)

        return [linha_completa]

# --- 3. Interface Visual do Streamlit ---

st.set_page_config(page_title="Extrator de Veículos", layout="wide")
st.title("Extrator de Dados de Veículos - Leilões")
st.write("**OBS:** Caso seja muitos PDFS, transformar em ZIP")

# Aceita PDF e ZIP
uploaded_files = st.file_uploader("Arraste seus PDFs ou arquivo ZIP aqui", type=['pdf', 'zip'], accept_multiple_files=True)

if uploaded_files:
    if st.button("Iniciar Processamento"):
        
        dados_totais = []
        barra_progresso = st.progress(0)
        status_text = st.empty()
        
        total_arquivos_processados = 0
        
        # --- Lógica para lidar com ZIP ou PDFs soltos ---
        for i, file_obj in enumerate(uploaded_files):
            
            # CASO 1: É um arquivo ZIP
            if file_obj.name.lower().endswith('.zip'):
                with zipfile.ZipFile(file_obj) as z:
                    # Filtra apenas arquivos PDF dentro do ZIP
                    lista_pdfs = [f for f in z.namelist() if f.lower().endswith('.pdf')]
                    total_zip = len(lista_pdfs)
                    
                    for k, nome_pdf in enumerate(lista_pdfs):
                        try:
                            status_text.text(f"Lendo do ZIP: {nome_pdf}")
                            # Lê o arquivo PDF específico dentro do ZIP (bytes)
                            pdf_bytes = z.read(nome_pdf)
                            
                            # Processa
                            linhas = processar_bytes_pdf(pdf_bytes)
                            dados_totais.extend(linhas)
                            
                            # Libera memória
                            del pdf_bytes
                            if k % 50 == 0: gc.collect()
                            
                        except Exception as e:
                            st.error(f"Erro no arquivo {nome_pdf}: {e}")
            
            # CASO 2: É um arquivo PDF solto
            elif file_obj.name.lower().endswith('.pdf'):
                try:
                    status_text.text(f"Lendo arquivo: {file_obj.name}")
                    pdf_bytes = file_obj.read()
                    linhas = processar_bytes_pdf(pdf_bytes)
                    dados_totais.extend(linhas)
                except Exception as e:
                    st.error(f"Erro ao ler {file_obj.name}: {e}")
            
            # Atualiza barra de progresso geral
            barra_progresso.progress((i + 1) / len(uploaded_files))
            
        # --- Geração do Excel ---
        if dados_totais:
            linhas_ajustadas = []
            for linha in dados_totais:
                if len(linha) > len(COLUNAS):
                    linha = linha[:len(COLUNAS)]
                elif len(linha) < len(COLUNAS):
                    linha.extend(['Não informado'] * (len(COLUNAS) - len(linha)))
                linhas_ajustadas.append(linha)
            
            df = pd.DataFrame(linhas_ajustadas, columns=COLUNAS)
            
            st.success("Processamento concluído!")
            st.subheader("Prévia dos Dados")
            st.dataframe(df.head())
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados Veiculos')
                worksheet = writer.sheets['Dados Veiculos']
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, 20)
            
            st.download_button(
                label="Baixar Planilha",
                data=buffer,
                file_name="dados_veiculos_extraidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado válido encontrado.")