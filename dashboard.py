import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import gdown

def definicao_parametros_graficos():
    # Configuracoes gerais
    sns.set_theme() 
    plt.rcParams['figure.figsize'] = (8, 6) # Tamanho da figura
    plt.rcParams['axes.titlesize'] = 12 # Tamanho do titulo
    plt.rcParams['axes.labelsize'] = 10 # Tamanho dos rotulos
    plt.rcParams['xtick.labelsize'] = 10 # Tamanho dos ticks eixo x
    plt.rcParams['ytick.labelsize'] = 10 # Tamanho dos ticks eixo y
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['axes.titleweight'] = 'bold'  # Título em negrito
    

    return None

def filtra_df(df):
    st.sidebar.header("Filtros Globais")
    df_filtrado = df.copy()

    # Filtro de data
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_purchase_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    opcoes_ano_mes = sorted(df['order_purchase_year_month'].unique(), reverse=True) 
    ano_mes_selecionado = st.sidebar.multiselect("Selecione o período (Ano-Mês)", options=opcoes_ano_mes, default=opcoes_ano_mes[:12])
    df_filtrado = df[df['order_purchase_year_month'].isin(ano_mes_selecionado)]

    # Filtro de status do pedido
    status_lista = df_filtrado['order_status'].unique().tolist()
    status_selecionado = st.sidebar.multiselect("Selecione o status do pedido", options=status_lista, default=status_lista)
    df_filtrado = df_filtrado[df_filtrado['order_status'].isin(status_selecionado)]

    # Filtro de estado
    estados = sorted(list(df_filtrado['customer_state'].unique()))
    estado_selecionado = st.sidebar.multiselect("Selecione um estado", options=estados, default=estados)
    df_filtrado = df_filtrado[df_filtrado['customer_state'].isin(estado_selecionado)]

    # Filtro df clientes e vendedores
    customers_df_filter = df[df['customer_state'].isin(estado_selecionado)]
    sellers_df_filter = df[df['seller_state'].isin(estado_selecionado)]

    return df_filtrado, customers_df_filter, sellers_df_filter

def big_numbers(c_df, s_df):
    # Big numbers
    st.subheader('Indicadores Gerais')

    total_vendas = c_df['total_price'].sum() if 'total_price' in c_df.columns else 0
    total_customers = c_df['customer_unique_id'].nunique() if 'customer_unique_id' in c_df.columns else 0
    total_sellers = s_df['seller_id'].nunique() if 'seller_id' in s_df.columns else 0

    # Define 3 colunas
    col1, col2, col3 = st.columns(3)
    col1.metric('Vendas Totais', f"R${total_vendas:,.2f}")
    col2.metric('Clientes únicos', f"{total_customers:,.0f}")
    col3.metric('Vendedores únicos', f"{total_sellers:,.0f}")
    return None

def visoes_gerais(c_df, s_df):
    # Visoes Gerais
    st.subheader('Visão Geral de Vendas por Estado')
    col1, col2, col3 = st.columns(3)

    vendas_estados = c_df[['customer_state','total_price']].groupby('customer_state').sum().reset_index()
    fig1, ax1 = plt.subplots()
    sns.barplot(data=vendas_estados, x='customer_state', y='total_price', ax=ax1)
    ax1.set_title('Vendas Totais por Estado')
    plt.xlabel('Estado')
    plt.ylabel('Vendas (R$)')
    col1.pyplot(fig1)

    clientes_estados = c_df[['customer_state','customer_unique_id']].groupby('customer_state').nunique().reset_index()
    fig2, ax2 = plt.subplots()
    sns.barplot(data=clientes_estados, x='customer_state', y='customer_unique_id', ax=ax2)
    ax2.set_title('Clientes Totais por Estado')
    plt.xlabel('Estados')
    plt.ylabel('Clientes')
    col2.pyplot(fig2)

    seller_estados = s_df[['seller_state','seller_id']].groupby('seller_state').nunique().reset_index()
    fig3, ax3 = plt.subplots()
    sns.barplot(data=seller_estados, x='seller_state', y='seller_id', ax=ax3)
    ax3.set_title('Vendedores Totais por Estado')
    plt.xlabel('Estados')
    plt.ylabel('Vendedores Unicos')
    col3.pyplot(fig3)

    return None

def visoes_temporais(c_df, s_df):
    st.subheader("Visões Temporais por Estado")
    # Filtrando dados pelos estado selecionado
    vendas_temporal = c_df[['order_purchase_year_month','total_price']].groupby('order_purchase_year_month').sum().reset_index()
    clientes_temporal = c_df[['order_purchase_year_month','customer_unique_id']].groupby('order_purchase_year_month').nunique().reset_index()
    vendedores_temporal = s_df[['order_purchase_year_month','seller_id']].groupby('order_purchase_year_month').nunique().reset_index()

    col1, col2, col3 = st.columns(3)
    fig1, ax1 = plt.subplots()
    sns.lineplot(data = vendas_temporal, x = 'order_purchase_year_month', y = 'total_price', ax=ax1)
    ax1.set_title(f'Vendas em R$ por mes')
    plt.xlabel('Ano-Mes')
    plt.ylabel('Vendas (R$)')
    plt.xticks(rotation = 60)
    col1.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    sns.lineplot(data = clientes_temporal, x = 'order_purchase_year_month', y = 'customer_unique_id', ax=ax2)
    ax2.set_title(f'Clientes únicos por mes')
    plt.xlabel('Ano-Mes')
    plt.ylabel('Clientes únicos')
    plt.xticks(rotation = 60)
    col2.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    sns.lineplot(data = vendedores_temporal, x = 'order_purchase_year_month', y = 'seller_id', ax=ax3)
    ax3.set_title(f'Vendedores únicos por mes')
    plt.xlabel('Ano-Mes')
    plt.ylabel('Vendedores únicos')
    plt.xticks(rotation = 60)
    col3.pyplot(fig3)

    return None

def faturamento(df):
    st.subheader("Faturamento e Ticket Médio")
    col1, col2 = st.columns(2)
    # Evolução do faturamento ao longo do tempo
    faturamento = df_filtrado.groupby('order_purchase_year_month')['total_price'].sum().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(data=faturamento, x='order_purchase_year_month', y='total_price', ax=ax)
    ax.set_title('Evolução do Faturamento ao Longo do Tempo')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Faturamento em R$')
    plt.xticks(rotation=45)
    col1.pyplot(fig)

    # Evolução do ticket médio ao longo do tempo
    ticket_medio = df_filtrado.groupby('order_purchase_year_month').agg(
        total_price=('total_price', 'sum'),
        order_count=('order_id', 'nunique')).reset_index()
    ticket_medio['ticket_medio'] = ticket_medio['total_price'] / ticket_medio['order_count']

    fig, ax = plt.subplots()
    sns.lineplot(data=ticket_medio, x='order_purchase_year_month', y='ticket_medio', ax=ax)
    ax.set_title('Evolução do Ticket Médio ao Longo do Tempo')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Ticket Medio em R$')
    plt.xticks(rotation=45)
    col2.pyplot(fig)

    return None

def pedidos_atrasados(df):
    st.subheader("Análise de pedidos atrasados")
    col1, col2 = st.columns(2)
    # Percentual de pedidos atrasados
    df_filtrado['order_delivered_customer_date'] = pd.to_datetime(df_filtrado['order_delivered_customer_date'])
    df_filtrado['order_estimated_delivery_date'] = pd.to_datetime(df_filtrado['order_estimated_delivery_date'])
    df_filtrado['pedido_atrasado'] = (df_filtrado['order_delivered_customer_date'] > df_filtrado['order_estimated_delivery_date'])
    df_filtrado['ano_mes'] = df_filtrado['order_purchase_timestamp'].dt.to_period('M').astype(str)

    # Calculando a porcentagem de pedidos atrasados por mês
    atraso_por_mes = df_filtrado.groupby('ano_mes').agg(total_pedidos=('order_id', 'count'),pedidos_atrasados=('pedido_atrasado', 'sum')).reset_index()
    atraso_por_mes['percentual_atraso'] = (atraso_por_mes['pedidos_atrasados'] / atraso_por_mes['total_pedidos']) * 100

    fig, ax = plt.subplots()
    sns.lineplot(data=atraso_por_mes, x='ano_mes', y='percentual_atraso', color="Green", ax=ax)
    ax.set_title('% Pedidos Atrasados ao Longo do Tempo')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Porcentagem de Atraso (%)')
    ax.tick_params(axis='x', rotation=45)
    col1.pyplot(fig)

    # Quais estados ou cidades têm mais problemas de atraso na entrega
    df_filtrado['atraso_entrega'] = (df_filtrado['order_delivered_customer_date'] > df_filtrado['order_estimated_delivery_date'])
    atrasos_por_estado = df_filtrado[df_filtrado['atraso_entrega']].groupby('customer_state').size().reset_index(name='qtd_atrasos')

    fig, ax = plt.subplots()
    sns.barplot(data=atrasos_por_estado.sort_values(by='qtd_atrasos', ascending=False), x='customer_state', y='qtd_atrasos', palette="Greens_r", ax=ax)
    ax.set_title('Estados com Mais Problemas de Atraso na Entrega')
    ax.set_xlabel('Estado')
    ax.set_ylabel('Qtd Atrasos')
    plt.xticks(rotation=45)
    col2.pyplot(fig)

    return None

def categorias(df):
    st.subheader("Análise de categorias")
    col1, col2 = st.columns(2)

    # Top categorias mais vendidas
    top_categorias = df_filtrado[['product_category_name','price']].groupby(['product_category_name']).sum().reset_index()
    top_categorias = top_categorias.sort_values(by='price', ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(data=top_categorias, x='price', y='product_category_name', palette="Blues_r", ax=ax)
    ax.set_title('Top 10 Categorias Mais Vendidas')
    ax.set_xlabel('Faturamento em R$')
    ax.set_ylabel('Categoria')
    col1.pyplot(fig)

    # Ticket medio por categoria
    ticket_medio_cat = df.groupby('product_category_name').agg(
        total_price=('total_price', 'sum'),
        order_count=('order_id', 'nunique')).reset_index()
    ticket_medio_cat['ticket_medio'] = ticket_medio_cat['total_price'] / ticket_medio_cat['order_count']
    ticket_medio_cat = ticket_medio_cat.sort_values(by='ticket_medio', ascending=False).head(10)

    # Criar gráfico de barras
    fig, ax = plt.subplots(figsize=(8,7.5))
    sns.barplot(data=ticket_medio_cat, x='ticket_medio', y='product_category_name', palette="Blues_r", ax=ax)
    ax.set_title("Top 10 Categorias Ticket Médio ")
    ax.set_xlabel("Ticket Médio (R$)")
    ax.set_ylabel("Categoria")
    col2.pyplot(fig)

    return None

def clientes(df):
    st.subheader("Análise de clientes")
    col1, col2 = st.columns(2)
    # Quantos clientes são recorrentes e quantos compram apenas uma vez
    clientes_freq = df_filtrado.groupby('customer_unique_id').size().reset_index(name='qtd_compras')
    clientes_freq['tipo_cliente'] = clientes_freq['qtd_compras'].apply(lambda x: 'Recorrente' if x > 1 else 'Único')

    fig, ax = plt.subplots()
    sns.countplot(data=clientes_freq, x='tipo_cliente', palette="Purples_r", ax=ax)
    ax.set_title('Distribuição de Clientes Recorrentes vs. Únicos')
    ax.set_xlabel("Tipo Cliente")
    ax.set_ylabel("Quantidade")
    col1.pyplot(fig)

    return None

definicao_parametros_graficos()

file_id = "1Eur0vKnnXoJA-I35HJa7nGwrX4yMCWfE"
url = f"https://drive.google.com/uc?id={file_id}"
csv_path = "order_items_cleaned.csv"
gdown.download(url, csv_path, quiet=False)

order_items_df = pd.read_csv(csv_path)

st.set_page_config(page_title='Análise de Desempenho', layout='wide')

# Criar abas para organizar o dashboard
aba1, aba2 = st.tabs(["Análise Regional", "Análises Avançadas"])
 # Aba 1 - Visão Geral
with aba1: 
    # Título
    st.title('Dashboard de Análise de Vendas por Estado')

    # Side Bar e filtragem
    df_filtrado, customers_df_filter, sellers_df_filter = filtra_df(order_items_df)

     # Big numbers
    big_numbers(customers_df_filter, sellers_df_filter)

    # Visões Gerais
    visoes_gerais(customers_df_filter, sellers_df_filter)

    # Visões temporais
    visoes_temporais(customers_df_filter, sellers_df_filter)

# Aba 2 - Análises Avançadas
with aba2:
    st.title('Insights Estratégicos')
    st.subheader("Análises Avançadas sobre Faturamento e Clientes")
    faturamento(df_filtrado)
    pedidos_atrasados(df_filtrado)
    categorias(df_filtrado)
    clientes(df_filtrado)