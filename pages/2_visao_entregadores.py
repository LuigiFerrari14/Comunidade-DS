#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import streamlit as st

st.set_page_config(page_title='Visão Entregadores', page_icon='🚙', layout='wide')
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


st.header("Marketplace - Visão Entregadores", divider=True)



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
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.subheader('Maior de Idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
        with col2:
            #st.subheader('Menor de Idade')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Maior de idade', menor_idade)
        with col3:
            #st.subheader('Melhor Condição de veiculos')
            maior_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', maior_condicao)
        with col4:
            #st.subheader('Pior Condição de veiculos')
            menor_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', menor_condicao)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')

            # Calcula a média de avaliações por entregador
            df_avg_ratings_per_deliver = (
                df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                .groupby('Delivery_person_ID')
                .mean()
                .reset_index()
            )
            
            # Exibe o DataFrame resultante
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
                        # Calcula a média e o desvio padrão das avaliações por condição de trânsito
            df_avg_std_rating_by_traffic = (
                df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                .groupby('Road_traffic_density')
                .agg({'Delivery_person_Ratings': ['mean', 'std']})
            )
            
            # Renomeia as colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            
            # Reseta o índice
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            
            # Exibe o DataFrame resultante
            st.dataframe(df_avg_std_rating_by_traffic)

            
            #st.markdown('### Avaliação média por condição de trânsito')




            
            #st.subheader('Avaliação média por clima')
            st.markdown('##### Avaliação média por condição climática')

            # Calcula a média e o desvio padrão das avaliações por condição climática
            df_avg_std_rating_by_weather = (
                df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                .groupby('Weatherconditions')
                .agg({'Delivery_person_Ratings': ['mean', 'std']})
            )
            
            # Renomeia as colunas
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            
            # Reseta o índice
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            
            # Exibe o DataFrame resultante
            st.dataframe(df_avg_std_rating_by_weather)



    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
                        # Group by 'City' and 'Delivery_person_ID' to calculate the mean time taken
            df2 = (
                df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending=True)
                .reset_index()
            )
            
            # Filter the top 10 fastest delivery persons for each city category
            df_aux01 = df2[df2['City'] == 'Metropolitan'].head(10)
            df_aux02 = df2[df2['City'] == 'Urban'].head(10)
            df_aux03 = df2[df2['City'] == 'Semi-Urban'].head(10)
            
            # Concatenate the results into a single DataFrame and reset index
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            
            # Display the resulting DataFrame
            st.dataframe(df3)
                    
        with col2:
            st.markdown('##### Top entregadores mais lentos') 
                        # Group by 'City' and 'Delivery_person_ID' to calculate the mean time taken
            df2 = (
                df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending=False)
                .reset_index()
            )
            
            # Filter the top 10 fastest delivery persons for each city category
            df_aux01 = df2[df2['City'] == 'Metropolitan'].head(10)
            df_aux02 = df2[df2['City'] == 'Urban'].head(10)
            df_aux03 = df2[df2['City'] == 'Semi-Urban'].head(10)
            
            # Concatenate the results into a single DataFrame and reset index
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            
            # Display the resulting DataFrame
            st.dataframe(df3)







