
# Bibliotecas necessárias para implementação do projeto.

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime


@st.cache_data

def _f_load_data():
    _response = requests.get("https://labdados.com/produtos")
    _api_data = pd.DataFrame.from_dict(_response.json())
    _api_data["Data da Compra"] = pd.to_datetime(_api_data["Data da Compra"], format="%d/%m/%Y")
    return _api_data

def _f_converts_csv(data):
    return data.to_csv(index = False).encode('utf-8')

def _f_sucess_message():
    sucesso = st.success('Table download sucessful.', icon = "✅")
    time.sleep(5)
    sucesso.empty()

# Início da página do app Hawk Store - Sales Dashboard.
# Dados brutos.

st.set_page_config(layout="wide")

# Títilo e cabeçalho da página.

st.markdown("<h1 style='text-align: center; margin-bottom: -12px;'>Reporting Tool - Sales Dashboard</h1>", unsafe_allow_html=True,)
st.markdown("<p style='text-align: center; color: gray; margin-top: 0px;'>By: Cristiano Santana</p>", unsafe_allow_html=True,)

st.markdown("<br>", unsafe_allow_html=True)

# Carregamento dos dados do projeto - Dados de Produtos.

# _url_data = "https://labdados.com/produtos"

# _response = requests.get(_url_data)

# _raw_data = pd.DataFrame.from_dict(_response.json())
# _raw_data["Data da Compra"] = pd.to_datetime(_raw_data["Data da Compra"], format="%d/%m/%Y")

_raw_data = _f_load_data()

# Tabela de produtos. 

st.markdown("<h4 style='text-align: center;'>Raw Data - Product Information</h4>", unsafe_allow_html=True,)

with st.expander("Columns"):
    _columns = st.multiselect("Select columns", list(_raw_data.columns), list(_raw_data.columns))

st.sidebar.title("Raw data filters")

with st.sidebar.expander("Product name"):
    _products = st.multiselect("Select products", _raw_data["Produto"].unique(), _raw_data["Produto"].unique())

with st.sidebar.expander('Product category'):
    _category = st.multiselect('Select category', _raw_data['Categoria do Produto'].unique(), _raw_data['Categoria do Produto'].unique())

with st.sidebar.expander("Product price"):
    _price = st.slider("Select price", 0, 5000, (0, 5000))

with st.sidebar.expander('Sale shipping'):
     _freight = st.slider('Freight', 0,250, (0,250))

with st.sidebar.expander("Purchase date"):
     _purchase_date = st.date_input("Select a date", (_raw_data["Data da Compra"].min(), _raw_data["Data da Compra"].max()))
    
if len(_purchase_date) != 2:
    st.warning("Select both the start and end dates.")
    st.stop()

with st.sidebar.expander('Sellers'):
     _sellers = st.multiselect('Select sellers', _raw_data['Vendedor'].unique(), _raw_data['Vendedor'].unique())

with st.sidebar.expander('Purchase place'):
     _purchase_place = st.multiselect('Select state', _raw_data['Local da compra'].unique(), _raw_data['Local da compra'].unique())

with st.sidebar.expander('Purchase evaluation'):
     _evaluation = st.slider('Select rating',1,5, value = (1,5))

with st.sidebar.expander('Payment type'):
     _payment_type = st.multiselect('Select Payment Type', _raw_data['Tipo de pagamento'].unique(), _raw_data['Tipo de pagamento'].unique())

with st.sidebar.expander('Number of installments'):
     _number_of_installments = st.slider('Select number of installments', 1, 24, (1,24))

_query = '''
    Produto in @_products and \
    `Categoria do Produto` in @_category and \
    @_price[0] <= Preço <= @_price[1] and \
    @_freight[0] <= Frete <= @_freight[1] and \
    @_purchase_date[0] <= `Data da Compra` <= @_purchase_date[1] and \
    Vendedor in @_sellers and \
    `Local da compra` in @_purchase_place and \
    @_evaluation[0]<= `Avaliação da compra` <= @_evaluation[1] and \
    `Tipo de pagamento` in @_payment_type and \
    @_number_of_installments[0] <= `Quantidade de parcelas` <= @_number_of_installments[1]
 '''

_filtered_data = _raw_data.query(_query)
_filtered_data = _filtered_data[_columns]

st.dataframe(_filtered_data)

st.markdown(f"Result: **:orange[{_filtered_data.shape[0]}]** lines e **:orange[{_filtered_data.shape[1]}]** columns.")

st.markdown("File name")
_column1, _column2 = st.columns(2)
with _column1:
    _file_name = st.text_input("", label_visibility = 'collapsed', value = f"result_table_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    _file_name += ".csv"
with _column2:
    st.download_button('Download table (.csv)', data = _f_converts_csv(_filtered_data), file_name = _file_name, mime = 'text/csv', on_click = _f_sucess_message)
