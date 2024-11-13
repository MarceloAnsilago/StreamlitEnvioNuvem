import streamlit as st
import pandas as pd
import re
import random
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

st.title('Upload de Arquivo e Exibição de Dados')

# Função para processar o DataFrame
def preprocess_dataframe(df):
    colunas_a_manter = ['Nome do Titular da Ficha de bovideos', 'Nome da Propriedade', 'Endereço da Prop.', 'Dec. Rebanho', 'Telefone 1', 'Telefone 2', 'Celular']
    df = df[colunas_a_manter]

    # Transformar colunas de telefone em linhas
    colunas_para_derreter = ['Telefone 1', 'Telefone 2', 'Celular']
    df = pd.melt(df, id_vars=['Nome do Titular da Ficha de bovideos', 'Nome da Propriedade', 'Endereço da Prop.', 'Dec. Rebanho'], value_vars=colunas_para_derreter, value_name='Telefone')
    df = df.drop(columns=['variable'])

    # Criar uma coluna "Nome" concatenando informações
    df['Nome'] = df.apply(lambda row: f"{row['Nome do Titular da Ficha de bovideos']} - {row['Nome da Propriedade']} - {row['Endereço da Prop.']}", axis=1)
    df = df.drop(columns=['Nome do Titular da Ficha de bovideos', 'Nome da Propriedade', 'Endereço da Prop.'])
    df = df[['Nome'] + [col for col in df.columns if col != 'Nome']]

    # Limpeza e formatação dos números de telefone
    df['Telefone'] = df['Telefone'].astype(str).str.replace(r'[^0-9-]', '', regex=True).str.zfill(10)
    df = df[~df['Telefone'].str.endswith('00')]
    df['Telefone'] = '+55' + df['Telefone']
    df['Telefone'] = df['Telefone'].apply(lambda telefone: telefone[:5] + telefone[6:] if len(telefone) == 15 else telefone)
    df['Telefone'] = df['Telefone'].str[:3] + ' ' + df['Telefone'].str[3:5] + ' ' + df['Telefone'].str[5:]

    # Adicionar coluna de status inicial
    df["Status"] = "Fila de envio"
    df = df[["Status"] + [col for col in df.columns if col != "Status"]]

    return df

uploaded_file = st.file_uploader("Carregar arquivo CSV ou Excel", type=["csv", "xlsx"])
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, engine='openpyxl')

    st.write("Dados carregados com sucesso!")
    st.write(df)

# Mensagem padrão
MensagemGenericaTexto = (
    "Olá tudo bem?😊 *Esta mensagem é da IDARON de São Miguel do Guaporé.* \n\n"
    "Prezado(a) produtor(a),\n\n"
    "A segunda etapa da declaração semestral de rebanho de 2024 começou em novembro, e gostaríamos de convidá-lo(a) a realizar sua declaração nos primeiros dias, aproveitando o menor movimento.\n\n"
    "A declaração pode ser feita de forma prática e rápida pela internet, onde você também pode cadastrar sua senha eletrônica, caso ainda não a possua. Se preferir, você pode comparecer a qualquer agência da IDARON, das 07h30 às 13h30.\n\n"
    "Contamos com sua colaboração!\n\n"
    "O número -&numero está cadastrado na *IDARON* para contato com -&nome.\n"
    "Se você não é ele(a)(s) ou responde por ele(a)(s), por favor nos avise que "
    "retiraremos seu contato de nossa base de dados, nos perdoe pelo incômodo e tenha um bom dia.\n\n"
)

st.header("Configuração de Mensagem e Intervalos de Envio")

# Input para mensagem personalizada
mensagem_customizada = st.text_area("Mensagem a ser enviada", MensagemGenericaTexto, height=300)

# Inputs adicionais para definir os tempos mínimo e máximo de espera entre envios
col1, col2 = st.columns(2)
with col1:
    tempo_minimo = st.number_input("Tempo mínimo entre envios (segundos)", min_value=1, value=10)
with col2:
    tempo_maximo = st.number_input("Tempo máximo entre envios (segundos)", min_value=1, value=15)

# Salvar as configurações no Streamlit e confirmar ao usuário
st.write("Configurações definidas:")
st.write(f"Mensagem padrão: {mensagem_customizada}")
st.write(f"Tempo mínimo entre envios: {tempo_minimo} segundos")
st.write(f"Tempo máximo entre envios: {tempo_maximo} segundos")

# Botão para avançar para a próxima etapa
if st.button("Avançar para o envio de mensagens"):
    st.success("Configurações salvas! Pronto para a etapa de envio.")


# Função para iniciar o driver do Selenium
from webdriver_manager.chrome import ChromeDriverManager

# Função para iniciar o driver do Selenium
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')

    # Iniciar o ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://web.whatsapp.com')
    st.write("Aguarde enquanto o WhatsApp Web carrega...")
    time.sleep(5)  # Aguardar o carregamento do WhatsApp Web

    return driver

# Função para criar o link de envio do WhatsApp
def criar_link_whatsapp(numero, mensagem):
    mensagem_codificada = urllib.parse.quote(mensagem)
    link = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem_codificada}"
    return link

# Função para enviar a mensagem pelo WhatsApp Web
def disparar_mensagem(driver, link_whatsapp):
    driver.get(link_whatsapp)
    time.sleep(5)  # Aguardar o carregamento da conversa

    try:
        # Enviar mensagem clicando no botão de enviar
        botao_enviar = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button')
        botao_enviar.click()
        time.sleep(2)  # Aguardar o envio
        return True
    except Exception as e:
        st.error(f"Erro ao enviar mensagem: {e}")
        return False

# Função para enviar mensagens com intervalo
def enviar_mensagens_com_intervalo(df, driver, mensagem_base, tempo_minimo, tempo_maximo):
    for index, row in df.iterrows():
        numero = row['Telefone']
        nome = row['Nome']
        mensagem = mensagem_base.replace('-&numero', numero).replace('-&nome', nome)
        link = criar_link_whatsapp(numero, mensagem)

        if disparar_mensagem(driver, link):
            st.write(f"Mensagem enviada para {nome} ({numero})")
            df.at[index, 'Status'] = 'Enviado'
        else:
            df.at[index, 'Status'] = 'Erro no envio'
        
        # Intervalo aleatório entre envios
        intervalo = random.randint(tempo_minimo, tempo_maximo)
        st.write(f"Aguardando {intervalo} segundos antes do próximo envio...")
        time.sleep(intervalo)

# Interface do Streamlit para iniciar o envio
if st.button("Iniciar envio de mensagens"):
    if uploaded_file is not None:
        df_tratado = preprocess_dataframe(df)
        driver = iniciar_driver()
        try:
            enviar_mensagens_com_intervalo(df_tratado, driver, mensagem_customizada, tempo_minimo, tempo_maximo)
            st.success("Envio de mensagens concluído!")
        finally:
            driver.quit()
    else:
        st.warning("Por favor, faça o upload de um arquivo antes de iniciar o envio.")    

