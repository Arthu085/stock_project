import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

server = 'SEU SERVIDOR'  
database = 'SEU BANCO'  
connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

engine = create_engine(connection_string)

def carregar_dados(query):
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

def inserir_dados(query, retornar_id=False):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            connection.commit()
            
            if retornar_id:
                id_result = connection.execute(text("SELECT SCOPE_IDENTITY() AS informacoes_id"))
                informacoes_id = id_result.fetchone()[0]
                return informacoes_id 

        return True  
    except SQLAlchemyError as e:
        st.error(f"Erro ao inserir dados: {e}")
        return False


def atualizar_dados(query):
    try:
        with engine.connect() as connection:
            connection.execute(query)
    except SQLAlchemyError as e:
        st.error(f"Erro ao atualizar dados: {e}")
