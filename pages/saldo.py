import streamlit as st
from services import conn

st.set_page_config(page_title='Estoque - Saldo',
                    layout="wide")

st.title('Consultar Saldo de Estoque')

query_item = """SELECT nome FROM item"""
df_item = conn.carregar_dados(query_item)
opcoes_itens = ['Geral'] + df_item['nome'].tolist()

choice_item = st.selectbox('Selecione o item:', options=opcoes_itens)

if choice_item == 'Geral':
    query_saldo = """SELECT b.nome, a.quantidade FROM saldoestoque a
                INNER JOIN item b
                ON a.id_item = b.id_item"""
    df_query_saldo = conn.carregar_dados(query_saldo)
    df_query_saldo = df_query_saldo.rename(columns={'nome': 'Item', 'quantidade': 'Quantidade'})
    df_query_saldo['Quantidade'] = df_query_saldo['Quantidade'].apply(lambda x: f"{x:,}".replace(",", ""))
    st.write(df_query_saldo)
else:
    query_saldo = f"""SELECT b.nome, a.quantidade FROM saldoestoque a
                INNER JOIN item b
                ON a.id_item = b.id_item
                WHERE b.nome = ('{choice_item}')"""
    df_query_saldo = conn.carregar_dados(query_saldo)
    df_query_saldo = df_query_saldo.rename(columns={'nome': 'Item', 'quantidade': 'Quantidade'})
    df_query_saldo['Quantidade'] = df_query_saldo['Quantidade'].apply(lambda x: f"{x:,}".replace(",", ""))
    st.write(df_query_saldo)