#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np
import streamlit as st

st.set_page_config(page_title='Visão Restaurante', page_icon='🍽️', layout='wide')
#import dataset
df = pd.read_csv('train.csv')


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


st.header("Marketplace - Visão Restaurantes", divider=True)



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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.markdown("""---""")
        st.title("Overall Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', delivery_unique)
        with col2:
                        # Definindo as colunas de latitude e longitude para cálculo
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                    'Restaurant_latitude', 'Restaurant_longitude']
            
            # Calculando a distância entre o restaurante e o local de entrega usando a fórmula de haversine
            df1['distance'] = df1.loc[:, cols].apply(
                lambda x: haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
            
            # Calculando a distância média das entregas
            avg_distance = np.round(df1['distance'].mean(), 2)
            
            # Exibindo a métrica na coluna 2
            col2.metric('A distância média das entregas', avg_distance)

        
        with col3:
            df_aux = (
                df1.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean', 'std']})
            )
            
            # Renomeando as colunas para maior clareza
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            # Filtrando para o caso de festival
            avg_time_festival = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'].values[0],2)
            
            # Exibindo a métrica do tempo médio de entrega durante festivais
            col3.metric('Tempo Médio de Entrega c/ Festival', avg_time_festival)
            
        with col4:
            df_aux = (
                df1.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean', 'std']})
            )
            
            # Renomeando as colunas para maior clareza
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            # Filtrando para o caso de festival
            avg_time_festival = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'].values[0],2)
            
            # Exibindo a métrica do tempo médio de entrega durante festivais
            col4.metric('STD de Entrega c/ Festival', avg_time_festival)

        
        with col5:
            df_aux = (
                df1.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean', 'std']})
            )
            
            # Renomeando as colunas para maior clareza
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            # Filtrando para o caso de festival
            avg_time_festival = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'].values[0],2)
            
            # Exibindo a métrica do tempo médio de entrega durante festivais
            col5.metric('Tempo Médio de Entrega s/ Festival', avg_time_festival)

        
        with col6:
            df_aux = (
            df1.loc[:, ['Time_taken(min)', 'Festival']]
            .groupby('Festival')
            .agg({'Time_taken(min)': ['mean', 'std']})
            )
            
            # Renomeando as colunas para maior clareza
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            # Filtrando para o caso de festival
            avg_time_festival = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'].values[0],2)
            
            # Exibindo a métrica do tempo médio de entrega durante festivais
            col6.metric('STD de Entrega s/ Festival', avg_time_festival)

    with st.container():
        st.markdown("""---""")
        st.title("Tempo Medio de entrega por cidade")
        cols = ['City', 'Time_taken(min)']
        df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})

        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control',
                                x=df_aux['City'],
                                y=df_aux['avg_time'],
                                error_y=dict(type='data', array=df_aux['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)






    

    with st.container():
        st.markdown("""---""")
        st.title("Distribuição do Tempo")
        col1, col2 = st.columns(2)
        with col1:
                   # Definindo as colunas de latitude e longitude para cálculo da distância
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                    'Restaurant_latitude', 'Restaurant_longitude']
            
            # Calculando a distância entre o restaurante e o local de entrega usando a fórmula de haversine
            df1['distance'] = df1.loc[:, cols].apply(
                lambda x: haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
            
            # Calculando a distância média por cidade
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            
            # Criando um gráfico de pizza para mostrar a distância média por cidade
            fig = go.Figure(data=[
                go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])
            ])
            
            # Exibindo o gráfico no Streamlit
            st.plotly_chart(fig)





        
with col2:
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(
        df_aux,
        path=['City', 'Road_traffic_density'],
        values='avg_time',
        color='std_time',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=np.average(df_aux['std_time'])
    )
    st.plotly_chart(fig)
            



    





       





























