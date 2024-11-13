import streamlit as st
import pandas as pd

st.title('Upload de Arquivo e Exibição de Dados')

uploaded_file = st.file_uploader("Carregar arquivo CSV ou Excel", type=["csv", "xlsx"])
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, engine='openpyxl')

    st.write("Dados carregados com sucesso!")
    st.write(df)
