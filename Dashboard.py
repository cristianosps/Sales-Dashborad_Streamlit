
# Bibliotecas necessárias para implementação do projeto.

import streamlit as st
import requests
import pandas as pd
import  plotly.express as px

@st.cache_data

# Função para o carregamento dos dados a serem analisados.

def _f_load_data(query_string):
    _response = requests.get("https://labdados.com/produtos", params=query_string)
    _api_data = pd.DataFrame.from_dict(_response.json())
    _api_data["Data da Compra"] = pd.to_datetime(_api_data["Data da Compra"], format="%d/%m/%Y")
    return _api_data

# Função para formatação das métricas utlizadas,

def _f_format_number(_value, _prefix=""):
    
    for _unit in ["", "thousand"]:
        if (_value < 1000):
            return f"{_prefix} {_value:.2f} {_unit}"
        _value /= 1000  

    return f"{_prefix} {_value:.2f} million"

# Início da página do app Reporting Tool - Sales Dashboard.

st.set_page_config(layout="wide")

# Títilo e cabeçalho da página.

st.markdown("<h1 style='text-align: center; margin-bottom: -12px;'>Reporting Tool - Sales Dashboard</h1>", unsafe_allow_html=True,)
st.markdown("<p style='text-align: center; color: gray; margin-top: 0px;'>By: Cristiano Santana</p>", unsafe_allow_html=True,)

st.markdown("<br>", unsafe_allow_html=True)

# Componentes da Sidebar com os filtros do dashboard.

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

# Iniciando o carregamento dos dados do projeto - Dados de Produtos.

_raw_data = _f_load_data(_query_string)

# Filtro vendedores

_sellers_filter = st.sidebar.multiselect("Sellers", _raw_data["Vendedor"].unique())
if _sellers_filter:
    _raw_data["Vendedor"].isin(_sellers_filter)

# Tabela - Agrupamento para a receita e vendas por UF. 

# Receita por UF. 
_revenue_by_state_map = _raw_data.groupby("Local da compra")[["Preço"]].sum()
_revenue_by_state_map = _raw_data.drop_duplicates(subset="Local da compra")[["Local da compra", "lat", "lon"]].merge(_revenue_by_state_map, 
                                                                                                            left_on="Local da compra", 
                                                                                                            right_index=True).sort_values("Preço", ascending=False)
# Vendas por UF. 
_sales_by_state_map = _raw_data.groupby("Local da compra")[["Preço"]].count()
_sales_by_state_map = _raw_data.drop_duplicates(subset="Local da compra")[["Local da compra", "lat", "lon"]].merge(_sales_by_state_map, 
                                                                                                            left_on="Local da compra", 
                                                                                                            right_index=True).sort_values("Preço", ascending=False)

# Tabelas - Agrupamento para receita e vendas por mês.

# Receita por mês.
_revenue_by_month = _raw_data.set_index("Data da Compra").groupby(pd.Grouper(freq="ME"))["Preço"].sum().reset_index()
_revenue_by_month["Ano"] = _revenue_by_month["Data da Compra"].dt.year
_revenue_by_month["Mes"] = _revenue_by_month["Data da Compra"].dt.month_name()

# Vendas por mês.
_sales_by_month = _raw_data.set_index("Data da Compra").groupby(pd.Grouper(freq="ME"))["Preço"].count().reset_index()
_sales_by_month["Ano"] = _sales_by_month["Data da Compra"].dt.year
_sales_by_month["Mes"] = _sales_by_month["Data da Compra"].dt.month_name()

# Tabelas - Agrupamento receita e vendas por categoria de produto.

# Receita por categoria de produto.
_revenue_by_category = _raw_data.groupby("Categoria do Produto")[["Preço"]].sum().sort_values("Preço", ascending=False)

# Vendas por categoria de produto.
_sales_by_category = _raw_data.groupby("Categoria do Produto")[["Preço"]].count().sort_values("Preço", ascending=False)

# Tabela - Vendas e Receita: Vendedores

_sellers_report = pd.DataFrame(_raw_data.groupby("Vendedor")["Preço"].agg(["count", "sum"]))


# Gráfico de receita por UF no Mapa.
_figure_revenue_by_state_map = px.scatter_geo(_revenue_by_state_map, lat="lat", lon="lon",
                                              size="Preço", color="Preço",
                                              size_max=45,
                                              color_continuous_scale="Blues",
                                              hover_name="Local da compra",
                                              hover_data={"lat": False, "lon": False, "Preço": ":,.2f"},
                                              labels={"Preço": "Revenue (R$)"},
                                              title="Revenue by State - Map",
                                              template="plotly_white",
                                              height=600)

_figure_revenue_by_state_map.update_traces(marker=dict(opacity=0.75,
                                                       line=dict(width=0.5, color="black")))

_figure_revenue_by_state_map.update_geos(scope="south america",
                                         lataxis_range=[-35, 6],
                                         lonaxis_range=[-75, -32],
                                         showcountries=True, countrycolor="lightgray",
                                         showland=True, landcolor="#F2F2F2")

_figure_revenue_by_state_map.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))

# Gráfico de vendas por UF no Mapa.
_figure_sales_by_state_map = px.scatter_geo(_sales_by_state_map, lat="lat", lon="lon", 
                                           size="Preço", color="Preço",
                                           size_max=45,
                                           color_continuous_scale="Blues",
                                           hover_name="Local da compra", 
                                           hover_data={"lat":False, "lon":False},
                                           labels={"Preço": "Sales"},
                                           title="Sales by State - Map",
                                           template="plotly_white",
                                           height=600)

_figure_sales_by_state_map.update_traces(marker=dict(opacity=0.75,
                                                       line=dict(width=0.5, color="black")))

_figure_sales_by_state_map.update_geos(scope="south america",
                                         lataxis_range=[-35, 6],
                                         lonaxis_range=[-75, -32],
                                         showcountries=True, countrycolor="lightgray",
                                         showland=True, landcolor="#F2F2F2")

_figure_sales_by_state_map.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))
 
# Gráfico de receita por mês.
_figure_revenue_by_month = px.line(_revenue_by_month,
                                   x="Mes", y="Preço",
                                   markers=True,
                                   color="Ano",
                                   line_dash="Ano",
                                   color_discrete_sequence=["#BEBEBE", "#7F7F7F", "#FFB066", "#FF6B00"],
                                   labels={"Ano": ""},
                                   template="plotly_white",
                                   title="Revenue by Month",
                                   height=580)

_figure_revenue_by_month.update_traces(line_width=2, marker_size=7,
                                       hovertemplate="R$ %{y:,.2f}")

_figure_revenue_by_month.update_yaxes(range=[_revenue_by_month["Preço"].min() * 0.95, _revenue_by_month["Preço"].max() * 1.05],
                                      tickformat="~s", tickprefix="R$ ")

_figure_revenue_by_month.update_layout(title_x=0,
                                       xaxis_title=None,
                                       yaxis_title="Revenue (R$)",
                                       hovermode="x unified",                                       
                                       legend=dict(orientation="h", yanchor="bottom", y=.95,
                                                   xanchor="center", x=0.5),
                                       margin=dict(l=0, r=0, t=80, b=0))

# Gráfico de vendas por mês.
_figure_sales_by_month = px.line(_sales_by_month,
                                    x="Mes", y="Preço",
                                    markers=True,
                                    range_y=(0, _revenue_by_month.max()),
                                    color="Ano",
                                    line_dash="Ano",
                                    color_discrete_sequence=["#BEBEBE", "#7F7F7F", "#FFB066", "#FF6B00"],
                                    labels={"Ano": ""},
                                    template="plotly_white",
                                    title="Sales by Month",
                                    height=580)

_figure_sales_by_month.update_yaxes(range=[_sales_by_month["Preço"].min() * 0.92, _sales_by_month["Preço"].max() * 1.056])

_figure_sales_by_month.update_traces(line_width=2, marker_size=7,
                                       hovertemplate="Sales: %{y}")

_figure_sales_by_month.update_layout(xaxis_title=None, yaxis_title="Sales by Month")

_figure_sales_by_month.update_layout(title_x=0,
                                    hovermode="x unified", 
                                    legend=dict(orientation="h", yanchor="bottom", y=.95,
                                                xanchor="center", x=0.5),   
                                     margin=dict(l=0, r=0, t=60, b=0))

# Gráfico de receita por UF - Barras.
_figure_revenue_by_state = px.bar(_revenue_by_state_map[:5],
                                  x="Local da compra",
                                  y="Preço",
                                  text_auto=".2s",
                                  title="Revenue by State - Top 5",
                                  height=520)

_figure_revenue_by_state.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       marker_line_width=0.5, textposition="outside")

_figure_revenue_by_state.update_layout(xaxis_title="State", 
                                       yaxis_title="Revenue by State (R$)")

_figure_revenue_by_state.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))


# Gráfico de vendas por UF - Barras.
_figure_sales_by_state = px.bar(_sales_by_state_map[:5],
                                  x="Local da compra",
                                  y="Preço",
                                  text_auto=True,
                                  title="Sales by State - Top 5",
                                  height=520)

_figure_sales_by_state.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       marker_line_width=0.5, textposition="outside")

_figure_sales_by_state.update_layout(xaxis_title="State", yaxis_title="Sales by State")

_figure_sales_by_state.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))

# _top5 = _sales_by_state_map[:5].copy()
# _top5["share"] = _top5["Preço"] / _sales_by_state_map["Preço"].sum() * 100

# _figure_sales_by_state = px.bar(_top5,
#                                 x="Local da compra",
#                                 y="Preço",
#                                 text_auto=True,
#                                 custom_data=["share"],
#                                 title="Sales by State - Top 5",
#                                 height=520)

# _figure_sales_by_state.update_traces(hovertemplate="<b>%{x}</b><br>Sales: %{y:,.0f}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
#                                      marker_color="#a3b9d0", marker_line_color="black",
#                                      marker_line_width=0.5, textposition="outside")

# _figure_sales_by_state.update_layout(xaxis_title="State", yaxis_title="Sales by State")

# _figure_sales_by_state.update_layout(title_x=0,
#                                      margin=dict(l=0, r=0, t=60, b=0))

# Gráfico de barras para receita por categoria de produto.
_figure_revenue_by_category = px.bar(_revenue_by_category,
                                     text_auto=".2s",
                                     title="Revenue by Product Category",
                                     height=520)    

_figure_revenue_by_category.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       marker_line_width=0.5, textposition="outside")

_figure_revenue_by_category.update_layout(xaxis_title="Category", yaxis_title="Revenue by Category (R$)", showlegend=False)

_figure_revenue_by_category.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))

# Gráfico de barras para vendas por categoria de produto.
_figure_sales_by_category = px.bar(_sales_by_category,
                                     text_auto=True,
                                     title="Sales by Product Category",
                                     height=520)

_figure_sales_by_category.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       marker_line_width=0.5, textposition="outside")

_figure_sales_by_category.update_layout(xaxis_title="Category", yaxis_title="Sales by Category", showlegend=False)

_figure_sales_by_category.update_layout(title_x=0,
                                           margin=dict(l=0, r=0, t=60, b=0))

# Métricas relacionadas a tabela de vendas do projeto: 

# - Revenue: Receita (em R$).
# - Sales  : Quantidade de vendas.

# Tab 01
# Gráficos: Revenue by State - Map (Receita por Estado - Mapa)
#           Revenue by Month (Receita por Mês)
#           Revenue by State (Receita por Estado)
#           Revenue by Product Category (Receita por Categoria de Produtos)

# Tab 02
# Gráficos: Sales by State - Map (Vendas por Estado - Mapa)
#           Sales by Month (Vendas por Mês)
#           Sales by State (Vendas por Estado)
#           Sales by Product Category (Vendas por Categoria de Produtos)

# Tab 03
# Gráficos: Revenue by Seller - Top __ (Receita por Vendedor - Top __)
#           Sales by Seller - Top __.  (Vendas por Vendedor - Top __)


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
        st.plotly_chart(_figure_sales_by_state_map, use_container_width=True)
        st.plotly_chart(_figure_sales_by_state, use_container_width=True)
        
    with _column2:
        st.metric("Sales: ", _f_format_number(_raw_data.shape[0]))
        st.plotly_chart(_figure_sales_by_month, use_container_width=True)
        st.plotly_chart(_figure_sales_by_category, use_container_width=True)

with _tab_03: 

    _quantity_of_salesmans = st.number_input("Quantity of sellers", 2, 10, 5)

    _column1, _column2 = st.columns(2)
    
    with _column1:
        st.metric("Revenue: ", _f_format_number(_raw_data["Preço"].sum(), "R$"))    
        
        _figure_sellers_revenue = px.bar(_sellers_report[["sum"]].sort_values("sum", ascending=False)[:_quantity_of_salesmans],
                                          x="sum", 
                                          y=_sellers_report[["sum"]].sort_values("sum", ascending=False)[:_quantity_of_salesmans].index,
                                          title=f"Revenue by Seller - Top {_quantity_of_salesmans}",
                                          height=550)

        _figure_sellers_revenue.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       texttemplate="\u00a0\u00a0\u00a0%{x:.2s}", marker_line_width=0.5, textposition="outside")    
            
        _figure_sellers_revenue.update_layout(xaxis_title="Revenue by seller (R$)", yaxis_title="Sellers")
        
        st.plotly_chart(_figure_sellers_revenue)

    with _column2:
        st.metric("Sales: ", _f_format_number(_raw_data.shape[0]))
            
        _figure_sales_sellers = px.bar(_sellers_report[["count"]].sort_values("count", ascending=False)[:_quantity_of_salesmans],
                                          x="count", 
                                          y=_sellers_report[["count"]].sort_values("count", ascending=False)[:_quantity_of_salesmans].index,
                                          text_auto=True,
                                          title=f"Sales by Seller - Top {_quantity_of_salesmans}",
                                          height=550)

        _figure_sales_sellers.update_traces(marker_color="#a3b9d0", marker_line_color="black",
                                       texttemplate="\u00a0\u00a0\u00a0%{x}", marker_line_width=0.5, textposition="outside")        
        
        _figure_sales_sellers.update_layout(xaxis_title="Sales by seller", yaxis_title="Sellers")
        
        st.plotly_chart(_figure_sales_sellers)
