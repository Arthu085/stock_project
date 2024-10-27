import streamlit as st
import pandas as pd
from services import conn

st.set_page_config(page_title='Estoque - Classes',
                    layout="wide")

st.title('Adicionar Classe')

classe_name = st.text_input('Digite o nome da classe:', placeholder='Escreva a classe aqui')

if st.button('Adicionar'):
    if classe_name:
        try:
            query_add_classe = f"INSERT INTO classes (nome_classe, categoria_id) VALUES ('{classe_name}', 1)"
            conn.inserir_dados(query_add_classe)
            st.success('Classe adicionada com sucesso!')
        except Exception as e:
            st.error(f'Ocorreu um erro ao adicionar a classe: {str(e)}')
    else:
        st.error('Digite o nome da classe!')