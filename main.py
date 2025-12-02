import streamlit as st
import pymupdf
import re
import pandas as pd
import io

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
    'Valor das Multas Outros', 'Bloqueio', 'Tipo Bloqueio', 'Descrição Bloqueio', 'Municipio Bloqueio', 'Número Edital Bloqueio', 
    'Ano Edital Bloqueio', 'Autoridade Bloqueio', 'Número Lote Bloqueio', 'Número Protocolo Bloqueio', 'Ano Protocolo Bloqueio', 
    'Data Inclusão Bloqueio', 'Hora Inclusão Bloqueio', 'Motivo 1 Bloqueio', 'Transacao ID', 'Data/Hora'
]

def processar_pdf(file_obj) -> list:
    with pymupdf.open(stream=file_obj.read(), filetype="pdf") as doc:
        text = chr(12).join([page.get_text() for page in doc])
        

        match_data = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})", text)
        data_hora_final = match_data.group(1) if match_data else "Não informado"
        
        text = re.sub(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}", "", text)
        text = text.replace("Informamos que os débitos de multas por", "")
        text = text.replace("infrações de trânsito podem apresentar divergências", "")
        text = text.replace("Aviso Importante:", "")

        find = text.find("Placa")
        if find != -1:
            text = text[find:]


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


        valores_comuns = re.findall(r":(.*?)\n", texto_geral)
        valores_comuns = [v.strip() if v.strip() != "" else "Não informado" for v in valores_comuns]

        QTD_CAMPOS_COMUNS = 69
        
        if len(valores_comuns) > QTD_CAMPOS_COMUNS:
            valores_comuns = valores_comuns[:QTD_CAMPOS_COMUNS] # Remove campos extras "fantasmas"
        elif len(valores_comuns) < QTD_CAMPOS_COMUNS:
            valores_comuns.extend(['Não informado'] * (QTD_CAMPOS_COMUNS - len(valores_comuns)))


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


        linhas_finais = []
        
        campos_bloqueio = [
            'Tipo', 'Descrição', 'Município',
            'Número Edital', 'Ano Edital', 'Autoridade',
            'Número Lote', 'Número Protocolo', 'Ano Protocolo',
            'Data Inclusão', 'Hora Inclusão', 'Motivo 1'
        ]

        todos_campos_regex = "|".join([c.replace(" ", r"\s+") for c in campos_bloqueio])

        if not tem_bloqueio:
            linha = valores_comuns.copy()
            linha.append('0') 
            linha.extend(['Não informado'] * len(campos_bloqueio)) 
            linhas_finais.append(linha)
        else:
            matches = list(re.finditer(r"Bloqueio\s+(\d+)", texto_bloqueios))
            
            for i, match in enumerate(matches):
                linha = valores_comuns.copy()
                num_bloqueio = match.group(1)
                
                inicio = match.start()
                fim = matches[i+1].start() if i+1 < len(matches) else len(texto_bloqueios)
                chunk_bloqueio = texto_bloqueios[inicio:fim]
                
                linha.append(num_bloqueio)
                
                for campo in campos_bloqueio:
                    padrao = fr"{campo}:\s*(.*?)(?=\n|\s+(?:{todos_campos_regex}):|$)"
                    match_campo = re.search(padrao, chunk_bloqueio, re.IGNORECASE)
                    valor = "Não informado"
                    
                    if match_campo:
                        valor_extraido = match_campo.group(1).strip()
                        eh_outro_campo = any(k.upper() + ":" in valor_extraido.upper() for k in campos_bloqueio)
                        if valor_extraido != "" and not eh_outro_campo:
                            valor = valor_extraido
                            
                    linha.append(valor)
                
                linhas_finais.append(linha)

        transacao_id = re.search(r"Transação Id:\s*(.*?)\n", text)
        valor_transacao = transacao_id.group(1).strip() if transacao_id else "Não informado"

        linhas_tratadas = []
        for linha in linhas_finais:
            linha.append(valor_transacao)
            linha.append(data_hora_final)

            if len(linha) > len(COLUNAS):
                linha = linha[:len(COLUNAS)]
            elif len(linha) < len(COLUNAS):
                linha.extend(['Não informado'] * (len(COLUNAS) - len(linha)))
            
            linhas_tratadas.append(linha)

        return linhas_tratadas


st.set_page_config(page_title="Extrator de Veículos", layout="wide")
st.title("Extrator de Dados de Veículos - Leilões")
st.subheader("Faça o upload de um ou vários PDFs para gerar a planilha.")

uploaded_files = st.file_uploader("Escolha os arquivos PDF", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Processar {len(uploaded_files)} Arquivo(s)"):
        
        dados_totais = []
        barra_progresso = st.progress(0)
        
        for i, pdf_file in enumerate(uploaded_files):
            try:
                linhas_extraidas = processar_pdf(pdf_file)
                dados_totais.extend(linhas_extraidas)
            except Exception as e:
                st.error(f"Erro ao ler o arquivo {pdf_file.name}: {e}")
            
            barra_progresso.progress((i + 1) / len(uploaded_files))
            
        if dados_totais:
            # Cria o DataFrame
            df = pd.DataFrame(dados_totais, columns=COLUNAS)
            
            st.success("Processamento concluído com sucesso!")
            st.subheader("Prévia dos Dados")
            st.dataframe(df.head())
            
            # --- CONVERSÃO PARA EXCEL ---
            buffer = io.BytesIO() # Cria um buffer na memória
            
            # Usa o motor 'xlsxwriter' para escrever no buffer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados Veiculos')
                
                # Ajuste automático de largura das colunas (Opcional, mas fica bonito)
                worksheet = writer.sheets['Dados Veiculos']
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, 20) # Define largura 20 para todas as colunas
            
            # Prepara o arquivo para download
            st.download_button(
                label="Baixar Planilha",
                data=buffer,
                file_name="dados_veiculos_extraidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )