
# Bibliotecas necessárias para implementação do projeto.

import streamlit as st
import requests
import pandas as pd
import  plotly.express as px

@st.cache_data

def _f_load_data(query_string):
    _response = requests.get("https://labdados.com/produtos", params=query_string)
    _api_data = pd.DataFrame.from_dict(_response.json())
    _api_data["Data da Compra"] = pd.to_datetime(_api_data["Data da Compra"], format="%d/%m/%Y")
    return _api_data

# Função para formatação das métricas utlizadas,

def _f_format_number(_value, _prefix=""):
    
    for _unit in ["", "mil"]:
        if (_value < 1000):
            return f"{_prefix} {_value:.2f} {_unit}"
        _value /= 1000  

    return f"{_prefix} {_value:.2f} milhões"

# Início da página do app Hawk Store - Sales Dashboard.

st.set_page_config(layout="wide")

# Títilo e cabeçalho da página.

st.markdown("<h1 style='text-align: center; margin-bottom: -12px;'>Reporting Tool - Sales Dashboard</h1>", unsafe_allow_html=True,)
st.markdown("<p style='text-align: center; color: gray; margin-top: 0px;'>By: Cristiano Santana</p>", unsafe_allow_html=True,)

st.markdown("<br>", unsafe_allow_html=True)

# Carregamento dos dados do projeto - Dados de Produtos.

# _url_data = "https://labdados.com/produtos"

# Sidebar com os filtros do dashboard.

_regions = ["Brasil", "Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"]

st.sidebar.title("Dashboard filters")

_region = st.sidebar.selectbox("Regions", _regions)
if _region == "Brasil":
    _region = ""

_every_year = st.sidebar.checkbox("Entire period", value=True)
if _every_year:
    _year = ""
else: 
    _year = st.sidebar.slider("Year", 2020, 2023)

_query_string = {"regiao":_region.lower(), "ano":_year}    

# _response = requests.get(_url_data, params=_query_string)

# _raw_data = pd.DataFrame.from_dict(_response.json())
# _raw_data["Data da Compra"] = pd.to_datetime(_raw_data["Data da Compra"], format="%d/%m/%Y")

_raw_data = _f_load_data(_query_string)

# Filtro vendedores

_sellers_filter = st.sidebar.multiselect("Sellers", _raw_data["Vendedor"].unique())
if _sellers_filter:
    _raw_data["Vendedor"].isin(_sellers_filter)



# Tabela - Agrupamento para o valor total de vendas por UF. 

_revenue_by_state_map = _raw_data.groupby("Local da compra")[["Preço"]].sum()
_revenue_by_state_map = _raw_data.drop_duplicates(subset="Local da compra")[["Local da compra", "lat", "lon"]].merge(_revenue_by_state_map, 
                                                                                                            left_on="Local da compra", 
                                                                                                            right_index=True).sort_values("Preço", ascending=False)

# Tabela - Agrupamento de vendas por mês.

_revenue_by_month = _raw_data.set_index("Data da Compra").groupby(pd.Grouper(freq="ME"))["Preço"].sum().reset_index()
_revenue_by_month["Ano"] = _revenue_by_month["Data da Compra"].dt.year
_revenue_by_month["Mes"] = _revenue_by_month["Data da Compra"].dt.month_name()

# Tabela - Agrupamento por categoria de produto.

_revenue_by_category = _raw_data.groupby("Categoria do Produto")[["Preço"]].sum().sort_values("Preço", ascending=False)

# Tabela - Vendas e Receita: Vendedores

_sellers_report = pd.DataFrame(_raw_data.groupby("Vendedor")["Preço"].agg(["count", "sum"]))



# Gráfico de receita por UF no Mapa.

_figure_revenue_by_state_map = px.scatter_geo(_revenue_by_state_map, lat="lat", lon="lon", 
                                           scope="south america", size="Preço", template="seaborn",
                                           hover_name="Local da compra", hover_data={"lat":False, "lon":False},
                                           title="Revenue by State - Map",
                                           width=1200, height=600)

_figure_revenue_by_state_map.update_geos(
    projection_scale=1.6,          # Aumenta o ZOOM (padrão é 1, valores maiores aproximam)
    center=dict(lat=-15, lon=-55)  # Centraliza o mapa em coordenadas específicas (ex: Brasil/América do Sul)
)
 
# Gráfico de receita por mês.

_figure_revenue_by_month = px.line(_revenue_by_month,
                                    x="Mes", y="Preço",
                                    markers=True,
                                    range_y=(0, _revenue_by_month.max()),
                                    color="Ano",
                                    line_dash="Ano",
                                    title="Revenue by Month",
                                    height=580)

_figure_revenue_by_month.update_layout(xaxis_title="Month", yaxis_title="Revenue by Month")

# Gráfico de receita por UF - Barras.

_figure_revenue_by_state = px.bar(_revenue_by_state_map[:5],
                                  x="Local da compra",
                                  y="Preço",
                                  text_auto=True,
                                  title="Revenue by State - Top 5",
                                  height=520)

_figure_revenue_by_state.update_layout(xaxis_title="State", yaxis_title="Revenue by State")

# Gráfico de receita por categoria de produto.

_figure_revenue_by_category = px.bar(_revenue_by_category,
                                     text_auto=True,
                                     title="Revenue by Product Category",
                                     height=520)

_figure_revenue_by_category.update_layout(xaxis_title="Category", yaxis_title="Revenue by Category", showlegend=False)

# Métricas relacionadas a tabela de vendas do projeto: 

# - Revenue: Receita (em R$).
# - Sales. : Quantidade de vendas.

# Gráficos: Revenue by State - Map (Receita por Estado - Mapa)
#           Revenue by Month (Receita por Mês)
#           Revenue by State (Receita por Estado)
#           Revenue by Product Category (Receita por Categoria de Produtos)

# Tabs: "Revenue", "Sales", "Sales People"

_tab_01, _tab_02, _tab_03 = st.tabs([ "Revenue", "Sales", "Sales People"])

with _tab_01: 
    _column1, _column2 = st.columns(2)

    with _column1:
        st.metric("Revenue: ", _f_format_number(_raw_data["Preço"].sum(), "R$"))    
        st.plotly_chart(_figure_revenue_by_state_map, use_container_width=True)
        st.plotly_chart(_figure_revenue_by_state, use_container_width=True)
        
    with _column2:
        st.metric("Sales: ", _f_format_number(_raw_data.shape[0]))
        st.plotly_chart(_figure_revenue_by_month, use_container_width=True)
        st.plotly_chart(_figure_revenue_by_category, use_container_width=True)

with _tab_02: 
    _column1, _column2 = st.columns(2)
    
    with _column1:
        st.metric("Revenue: ", _f_format_number(_raw_data["Preço"].sum(), "R$"))    
        
    with _column2:
        st.metric("Sales: ", _f_format_number(_raw_data.shape[0]))

with _tab_03: 

    _quantity_of_salesmans = st.number_input("Quantity of sellers", 2, 10, 5)

    _column1, _column2 = st.columns(2)
    
    with _column1:
        st.metric("Revenue: ", _f_format_number(_raw_data["Preço"].sum(), "R$"))    
        
        _figure_sellers_revenue = px.bar(_sellers_report[["sum"]].sort_values("sum", ascending=False)[:_quantity_of_salesmans],
                                          x="sum", 
                                          y=_sellers_report[["sum"]].sort_values("sum", ascending=False)[:_quantity_of_salesmans].index,
                                          text_auto=True,
                                          title=f"Revenue by Seller - Top {_quantity_of_salesmans}",
                                          width=800, height=550)
        
        _figure_sellers_revenue.update_layout(xaxis_title="Revenue by seller", yaxis_title="Sellers")
        
        st.plotly_chart(_figure_sellers_revenue)

    with _column2:
        st.metric("Sales: ", _f_format_number(_raw_data.shape[0]))
            
        _figure_sales_sellers = px.bar(_sellers_report[["count"]].sort_values("count", ascending=False)[:_quantity_of_salesmans],
                                          x="count", 
                                          y=_sellers_report[["count"]].sort_values("count", ascending=False)[:_quantity_of_salesmans].index,
                                          text_auto=True,
                                          title=f"Sales by Seller - Top {_quantity_of_salesmans}",
                                          width=800, height=550)
                
        _figure_sales_sellers.update_layout(xaxis_title="Sales by seller", yaxis_title="Sellers")
        
        st.plotly_chart(_figure_sales_sellers)
        
# Tabela de produtos. 
# st.markdown("<br>", unsafe_allow_html=True)
# st.markdown("<h4 style='text-align: center;'>Product Information</h4>", unsafe_allow_html=True,)

# st.dataframe(_raw_data) 