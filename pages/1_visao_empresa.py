#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import streamlit as st

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#import dataset
df = pd.read_csv("train.csv")


df1 = df.copy()

# 1. Convertendo a coluna Age de texto para número
linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Time_taken(min)'] != 'nan')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['City'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Festival'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)


# 2. Convertendo a coluna Ratings de texto para número decimal (float)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)


# 3. Convertendo a coluna order date de texto para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# 4. Convertendo multiple_deliveries de texto para número inteiro (int)
linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# 5. Removendo os espaços dentro de strings/texto/object
#df1 = df1.reset_index(drop=True)
# for i in range(len(df1)):
#     df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

# 6. Removendo os espaços dentro de strings/texto/object
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()


# 7. Limpando a coluna de time taken
df1 = df1.dropna(subset=['Time_taken(min)'])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).apply(lambda x: x.split('(min)')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)


#Visão Empresa

#cols = ['ID', 'Order_Date']
#df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
#
#px.bar(df_aux, x='Order_Date', y='ID')


# ===================================================================
# Barra Lateral
# ===================================================================


st.header("Marketplace - Visão Cliente", divider=True)



image_path = 'tec.jpg'
image = Image.open( image_path )
st.sidebar.image(image, width=120)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('# Fastested Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value=pd.to_datetime('2022-04-06').date(),
    min_value=pd.to_datetime('2022-02-11').date(),
    max_value=pd.to_datetime('2022-04-13').date(),
    format='DD-MM-YYYY'
)

st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as confições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Comunidade DS: Luigi Silva Ferrari')

#filtros de data
linhas_selecionadas = df1['Order_Date'] < pd.to_datetime(date_slider)
df1 = df1.loc[linhas_selecionadas, :]

#filtros de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]
st.dataframe(df1.head())

# ===================================================================
# Layout no Streamlit
# ===================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:

    with st.container():
    
        st.markdown('# Orders by Day')
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_widht=True)


    with st.container():
    
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

            # Remove as linhas onde o valor de 'Road_traffic_density' é NaN
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
            
            # Calcula a porcentagem de entregas para cada densidade de tráfego
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            
            # Cria um gráfico de pizza com os dados de porcentagem de entregas por densidade de tráfego
            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

            st.plotly_chart(fig, use_container_widht=True)
            
        with col2:
            st.header('Traffic Order City')
            # Agrupa os dados por 'City' e 'Road_traffic_density' e conta o número de ocorrências para cada combinação
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            
            # Remove as linhas onde o valor de 'City' é NaN
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            
            # Remove as linhas onde o valor de 'Road_traffic_density' é NaN
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            
            # Cria um gráfico de dispersão com 'City' no eixo x, 'Road_traffic_density' no eixo y,
            # o tamanho dos pontos representando a coluna 'ID' e a cor dos pontos representando as cidades
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_widht=True)
                    
    
with tab2:
    with st.container():
        st.markdown("# Order by Week")
            # Criar a coluna de semana
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        
        # Agrupar por semana e contar o número de pedidos por semana
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        
        # Plotar o gráfico de linha
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_widht=True)


    with st.container():
        st.markdown("# Order Share by Week")
        # Quantidade de pedidos por semana e número único de entregadores por semana
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        
        # Mesclar os dois DataFrames no campo 'week_of_year'
        df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
        
        # Calcular a quantidade de pedidos por entregador
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        
        # Plotar o gráfico de linha
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_widht=True)



with tab3:
    st.markdown('# Country Map')
    # Filtrando e agrupando dados
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
    df_aux = df_aux.groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    # Removendo linhas com valores 'NaN' nas colunas 'City' e 'Road_traffic_density'
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    # Criando o mapa
    map = folium.Map()
    
    # Adicionando marcadores no mapa
    for index, location_info in df_aux.iterrows():
        folium.Marker(
            [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
            popup=f"{location_info['City']}, {location_info['Road_traffic_density']}"
        ).add_to(map)
    folium_static(map, width=1024, height=600)

#print(df_aux.head())


