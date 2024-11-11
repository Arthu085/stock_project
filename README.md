# Projeto Estoque

Este é um projeto de gerenciamento de estoque desenvolvido com **Streamlit**, **SQLAlchemy** e **pandas**. O objetivo é fornecer uma interface para controlar entradas e saídas de itens no estoque, com integração a um banco de dados SQL Server.

## Funcionalidades

- Cadastro e movimentação de itens no estoque.
- Consultas filtradas por data e tipo de movimentação.
- Exibição e inserção de dados diretamente no banco de dados SQL Server.
- Conexão otimizada com o banco de dados, utilizando SQLAlchemy.

## Como usar

### Requisitos

1. **Python 3.8+**
2. **Bibliotecas**:
   - pandas
   - streamlit
   - sqlalchemy
   - pyodbc (para conexão com o SQL Server)

Você pode instalar as dependências do projeto utilizando o seguinte comando:

```bash
pip install -r requirements.txt
```

### Estrutura do Projeto
- stock_project/: Contém os scripts principais para rodar o Streamlit e interação com a interface do usuário.
- services/: Contém o código relacionado à conexão com o banco de dados e scripts SQL.
- db_script.py: Script SQL utilizado para criar as tabelas no banco de dados.
- connection.py: Script que contém a lógica para conectar ao banco de dados SQL Server.

### Como configurar a conexão com o banco de dados
Na pasta services/, o arquivo connection.py é responsável pela conexão com o banco de dados SQL Server. Você pode ajustar os detalhes de conexão conforme o seu ambiente (nome do servidor, banco de dados, credenciais).

### Executando o Banco de Dados
Na pasta services/, o arquivo db_script.py contém o script SQL que cria as tabelas necessárias para o funcionamento do sistema. Execute o script no seu banco de dados para garantir que as tabelas estejam criadas corretamente.


### Rodando o Streamlit
Após configurar o banco de dados e a conexão, você pode rodar o aplicativo Streamlit com o seguinte comando:

```bash
streamlit run stock_project/index.py
```
Isso abrirá a interface no seu navegador, onde você poderá interagir com o sistema de gerenciamento de estoque.
