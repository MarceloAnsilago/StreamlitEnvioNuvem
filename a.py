import streamlit as st
import pandas as pd
import re

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
