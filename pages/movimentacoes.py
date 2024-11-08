import streamlit as st
from services import conn
import pandas as pd



st.set_page_config(page_title='Estoque - Saldo',
                    layout="wide")

st.title('Consultar Movimentações de Estoque')

query_item = """SELECT id_item, nome FROM item"""
df_item = conn.carregar_dados(query_item)

choice_item = st.selectbox('Selecione o item:', options=df_item['nome'].tolist())
item_id = df_item.loc[df_item['nome'] == choice_item, 'id_item'].values[0]

query_tipo = """SELECT tipo_entrada_saida_nome FROM entradasaida"""
df_query_tipo = conn.carregar_dados(query_tipo)
df_query_tipo_exibicao = df_query_tipo.copy()
df_query_tipo_exibicao['tipo_entrada_saida_nome'] = df_query_tipo_exibicao['tipo_entrada_saida_nome'].replace({'balanco': 'Balanço', 'devolucao': 'Devolução', 'paciente': 'Paciente', 'perda': 'Perda', 'nota_fiscal': 'Nota Fiscal'})
opcoes_tipo = ['Geral'] + df_query_tipo_exibicao['tipo_entrada_saida_nome'].tolist()
choice_tipo_exibicao = st.selectbox('Selecione o tipo:', options=opcoes_tipo)

tipo_map = {
    'Balanço': 'balanco',
    'Devolução': 'devolucao',
    'Paciente': 'paciente',
    'Perda': 'perda',
    'Nota Fiscal': 'nota_fiscal'
}
choice_tipo = tipo_map.get(choice_tipo_exibicao, choice_tipo_exibicao)

col1, col2 = st.columns(2)
with col1:
    data1 = st.date_input('Selecione a primeira data:', format="DD/MM/YYYY")
with col2:
    data2 = st.date_input('Selecione a segunda data:', format="DD/MM/YYYY")

data1_str = data1.strftime('%Y-%m-%d') if data1 else ''
data2_str = data2.strftime('%Y-%m-%d') if data2 else ''


if st.button('Pesquisar'):

    if choice_tipo == 'Geral':
        query_search_movi = f"""SELECT e.nome, 
        a.quantidade, 
        FORMAT(a.data_movi, 'dd/MM/yyyy') AS data_formatada, 
        b.tipo_entrada_saida_nome, 
        c.numero_nota, 
        c.devolucao_obs, 
        c.paciente_nome, 
        c.motivo_perda, 
        d.tipo FROM moviestoque a
        INNER JOIN entradasaida b
            ON a.tipo_entrada_saida_id = b.tipo_entrada_saida_id
        INNER JOIN informacoes c
            ON a.informacoes_id = c.informacoes_id
        INNER JOIN tipomov d
            ON a.tipo_mov_id = d.tipo_mov_id
        INNER JOIN item e
            ON a.id_item = e.id_item
        WHERE e.id_item = ('{item_id}')
            AND CONVERT(DATE, a.data_movi) BETWEEN '{data1_str}' AND '{data2_str}'"""
        
        df_query_search_movi = conn.carregar_dados(query_search_movi)
        df_query_search_movi.rename(columns={
        'nome': 'Item', 
        'quantidade': 'Quantidade',
        'data_formatada': 'Data',
        'tipo_entrada_saida_nome': 'Tipo de Movimento',
        'numero_nota': 'Número da Nota',
        'devolucao_obs': 'Observação da Devolução',
        'paciente_nome': 'Nome do Paciente',
        'motivo_perda': 'Motivo da Perda',
        'tipo': 'Tipo de Movimentação'
        }, inplace=True)
        
        df_query_search_movi['Quantidade'] = df_query_search_movi['Quantidade'].apply(lambda x: f"{x:,}".replace(",", ""))
        df_query_search_movi['Número da Nota'] = df_query_search_movi['Número da Nota'].apply(
            lambda x: f"{x:,}".replace(",", "") if pd.notna(x) else x)
        
        tipo_movimento_map = {
        'nota_fiscal': 'Nota Fiscal',
        'devolucao': 'Devolução',
        'balanco': 'Balanço',
        'paciente': 'Paciente',
        'perda': 'Perda'
        }

        df_query_search_movi['Tipo de Movimento'] = df_query_search_movi['Tipo de Movimento'].replace(tipo_movimento_map)
        st.write(df_query_search_movi)
    else:
        query_search_movi = f"""SELECT e.nome, 
        a.quantidade, 
        FORMAT(a.data_movi, 'dd/MM/yyyy') AS data_formatada, 
        b.tipo_entrada_saida_nome, 
        c.numero_nota, 
        c.devolucao_obs, 
        c.paciente_nome, 
        c.motivo_perda, 
        d.tipo FROM moviestoque a
        INNER JOIN entradasaida b
            ON a.tipo_entrada_saida_id = b.tipo_entrada_saida_id
        INNER JOIN informacoes c
            ON a.informacoes_id = c.informacoes_id
        INNER JOIN tipomov d
            ON a.tipo_mov_id = d.tipo_mov_id
        INNER JOIN item e
            ON a.id_item = e.id_item
        WHERE e.id_item = ('{item_id}')
            AND CONVERT(DATE, a.data_movi) BETWEEN '{data1_str}' AND '{data2_str}'
            AND b.tipo_entrada_saida_nome = ('{choice_tipo}')"""
        
        df_query_search_movi = conn.carregar_dados(query_search_movi)
        df_query_search_movi.rename(columns={
        'nome': 'Item', 
        'quantidade': 'Quantidade',
        'data_formatada': 'Data',
        'tipo_entrada_saida_nome': 'Tipo de Movimento',
        'numero_nota': 'Número da Nota',
        'devolucao_obs': 'Observação da Devolução',
        'paciente_nome': 'Nome do Paciente',
        'motivo_perda': 'Motivo da Perda',
        'tipo': 'Tipo de Movimentação'
        }, inplace=True)

        df_query_search_movi['Quantidade'] = df_query_search_movi['Quantidade'].apply(lambda x: f"{x:,}".replace(",", ""))
        df_query_search_movi['Número da Nota'] = df_query_search_movi['Número da Nota'].apply(
            lambda x: f"{x:,}".replace(",", "") if pd.notna(x) else x)
        
        tipo_movimento_map = {
        'nota_fiscal': 'Nota Fiscal',
        'devolucao': 'Devolução',
        'balanco': 'Balanço',
        'paciente': 'Paciente',
        'perda': 'Perda'
        }

        df_query_search_movi['Tipo de Movimento'] = df_query_search_movi['Tipo de Movimento'].replace(tipo_movimento_map)
        st.write(df_query_search_movi)