import streamlit as st
import pandas as pd
from services import conn

st.set_page_config(page_title='Estoque - Item',
                    layout="wide")

st.title('Adicionar Item')

query_categoria = "SELECT categoria_id, nome FROM categoria"
df_categoria = conn.carregar_dados(query_categoria)
df_categoria['nome'] = df_categoria['nome'].replace({'classe': 'Classe', 'material': 'Material'})
categoria_dict = dict(zip(df_categoria['nome'], df_categoria['categoria_id']))


query_classes = """
SELECT a.id_classe, a.nome_classe 
FROM classes a 
LEFT JOIN categoria b 
ON a.categoria_id = b.categoria_id
"""
df_classes = conn.carregar_dados(query_classes)

query_material = """SELECT a.id_material, a.nome_material 
FROM material a 
LEFT JOIN categoria b 
ON a.categoria_id = b.categoria_id"""
df_material = conn.carregar_dados(query_material)
df_material['nome_material'] = df_material['nome_material'].replace({'material_paciente': 'Material Paciente'})

item_name = st.text_input('Digite o nome do item:', placeholder='Escreva o item aqui')
choice_categoria = st.selectbox('Selecione a categoria:', options=list(categoria_dict.keys()))

categoria_id = categoria_dict[choice_categoria]

if choice_categoria == 'Classe':
    choice_classe = st.selectbox('Selecione a classe:', options=df_classes['nome_classe'])
    choice_classe_id = df_classes.loc[df_classes['nome_classe'] == choice_classe, 'id_classe'].values[0]
    choice_material_id = None
else:
    choice_material = st.selectbox('Selecione o material:', options=df_material['nome_material'])
    choice_material_id = df_material.loc[df_material['nome_material'] == choice_material, 'id_material'].values[0]
    choice_classe_id = None
    
if st.button('Adicionar'):
    if item_name and categoria_id:
        columns = ['nome', 'categoria_id']
        values = [f"'{item_name}'", f"{categoria_id}"] 

        if choice_classe_id is not None:
            columns.append('id_classe')
            values.append(f"{choice_classe_id}")

        if choice_material_id is not None:
            columns.append('id_material')
            values.append(f"{choice_material_id}") 

        query_add_item = f"INSERT INTO item ({', '.join(columns)}) VALUES ({', '.join(values)})"
        
        try:
            conn.inserir_dados(query_add_item)
            st.success('Item adicionado com sucesso!')
        except Exception as e:
            st.error(f'Ocorreu um erro ao adicionar o item: {str(e)}')
    else:
        st.error('Preencha todas as colunas necessárias!')