# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:36:18 2024

@author: stfey
"""
import pandas as pd
import numpy as np
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium

# import plotly.io as pio
# pio.templates.default = 'plotly' 

filepath = (r'C:\Users\stfey\Documents\SUPINFO\4DVST\publications_scientifiques_par_pays.xlsx')
df = pd.read_excel(filepath)

political_countries_url = (
    "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
)

# Rename countries
df['Country'] = df['Country'].replace(['South Korea'], 'Republic of Korea')
df['Country'] = df['Country'].replace(['North Korea'], 'Dem. Rep. Korea')
df['Country'] = df['Country'].replace(['Viet Nam'], 'Vietnam')
df['Country'] = df['Country'].replace(['Laos'], 'Lao PDR')
df['Country'] = df['Country'].replace(['Syrian Arab Republic'], 'Syria')
df['Country'] = df['Country'].replace(['Palestine '], 'Palestine')
df['Country'] = df['Country'].replace(['Libyan Arab Jamahiriya'], 'Libya')
df['Country'] = df['Country'].replace(['Somalia'], 'Somalia')
df['Country'] = df['Country'].replace(['Democratic Republic Congo'], 'Democratic Republic of the Congo')

st.title('Analyse de Publications Scientifiques')

nb_pays = len(pd.unique(df['Country']))
nb_annees = df['Year'].max() - df['Year'].min()
nb_doc_min = df['Documents'].min()
nb_doc_max = df['Documents'].max()
df_2014 = df.loc[df['Year'] == 2014]
top_5 = df_2014.loc[df['Rank'] <= 5]
bottom_5 = df_2014['Rank'].max() - 5
flop_5 = df_2014.loc[df['Rank'] > bottom_5]

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="NB de pays", value = nb_pays)
col2.metric(label="Total des années", value = nb_annees)
col3.metric(label="NB documents min", value = nb_doc_min)
col4.metric(label="ND documents max", value = nb_doc_max)

st.dataframe(top_5)
st.dataframe(flop_5)

# Nombre moyen de documents produits par an et le nombre moyen de citations par an, pour chaque pays

pays_prod_moy = df.groupby(['Country']).agg({'Rank' : "median", 'Documents' : "mean", 'Citations' : "mean", 'H.index' : "mean"}).reset_index()
pays_prod_moy['Rank'] = pays_prod_moy['Rank'].astype(int)
pays_prod_moy['Documents'] = pays_prod_moy['Documents'].astype(int)
pays_prod_moy['Citations'] = pays_prod_moy['Citations'].astype(int)
pays_prod_moy['H.index'] = pays_prod_moy['H.index'].astype(int)

st.subheader("Nombre moyen de documents produits par an et le nombre moyen de citations par an, par pays")

fig = px.scatter(x = pays_prod_moy['Citations'],
                  y = pays_prod_moy['Documents'],
                  size = pays_prod_moy['H.index'], 
                  color = pays_prod_moy['Rank'],
                  hover_name = pays_prod_moy['Country'], 
                  log_x=True, 
                  size_max=20,
                  color_continuous_scale='RdBu')
fig.update_layout(
    xaxis_title="Average Documents",
    yaxis_title="Average Citations",
    coloraxis_colorbar_title="Rank"
)
fig.add_shape(
    type="line",
    x0=pays_prod_moy['Citations'].mean(),
    y0=pays_prod_moy['Documents'].min(),
    x1=pays_prod_moy['Citations'].mean(),
    y1=pays_prod_moy['Documents'].max(),
    line=dict(
        color="black",
        width=1,
        dash="dashdot",
    )
)
fig.add_shape(
    type="line",
    x0=pays_prod_moy['Citations'].min(),
    y0=pays_prod_moy['Documents'].mean(),
    x1=pays_prod_moy['Citations'].max(),
    y1=pays_prod_moy['Documents'].mean(),
    line=dict(
        color="black",
        width=1,
        dash="dashdot",
    )
)

st.plotly_chart(fig, use_container_width=True)


# L’évolution dans le temps des top 10 rangs des pays, avec le pays en 1er en haut
rank_top10 = df.loc[df['Rank'] <= 10]
rank_top10['inverted_values'] = rank_top10['Rank'].max() - rank_top10['Rank'] + rank_top10['Rank'].min()

st.subheader("L’évolution dans le temps de top 10 des pays en fonction de leur rang")

fig3 = px.line(rank_top10, 
               x="Year", 
               y="inverted_values", 
               color='Country', 
               labels={'inverted_values':'Rank'},
               hover_data = 'Rank',
               markers=True)
fig3.update_layout(
    yaxis = dict(showticklabels = False))
st.plotly_chart(fig3, use_container_width=True)


# Une carte des pays dont le H-index moyen est supérieur à un seuil choisi par l’utilisateur

st.subheader("Une carte des pays dont le H-index moyen est supérieur à un seuil selectionné")

max_value = pays_prod_moy['H.index'].max()
values = st.slider(
    'Selectionner le seuil de H-index',
    0, max_value, (0, max_value))
st.write('Values:', values)
filtered_data = pays_prod_moy[(pays_prod_moy['H.index'] >= values[0]) & (pays_prod_moy['H.index'] <= values[1])]

m = folium.Map(location=(30, 10), zoom_start=1, tiles="cartodb positron")
folium.Choropleth(
    geo_data=political_countries_url,
    data=filtered_data,
    columns=["Country", "H.index"],
    key_on="feature.properties.name_long",
    fill_color="YlGnBu",
    fill_opacity=0.8,
    line_opacity=0.3,
    nan_fill_color="white",
    legend_name="Average H.index",
).add_to(m)
st_data = st_folium(m, height=400, width=725)


#Une carte des pays représentant le TOP réalisé plus haut avec la couleur dependant du nombre de docs

st.subheader("Une carte de top 10 de pays au niveau du rank avec le nombre de documets par an")
sel_rank = st.slider(
    'Selectionner le seuil de rank',
    0, 10, (0,10))
st.write('Values:', sel_rank)

years = rank_top10['Year'].unique()
my_year = st.radio("Selectionner l'année", years)
selected_year = rank_top10[(rank_top10['Year'] == my_year) & (rank_top10['Rank'] >= sel_rank[0]) & (rank_top10['Rank'] <= sel_rank[1])]
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

m1 = folium.Map(location=(30, 10), zoom_start=1, tiles="cartodb positron")
folium.Choropleth(
    geo_data=political_countries_url,
    data=selected_year,
    columns=["Country", "Documents"],
    key_on="feature.properties.name_long",
    fill_color="YlGnBu",
    fill_opacity=0.8,
    line_opacity=0.3,
    nan_fill_color="white",
    legend_name="Documents",
).add_to(m1)
st_data1 = st_folium(m1, height=400, width=725)



