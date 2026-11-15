# Converted from RTM-2.ipynb
# --- Code Cell 1 ---
import pandas as pd
import plotly.express as px
import nbformat
import folium
import numpy as np
from sklearn.cluster import KMeans
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN
from scipy.spatial.distance import cdist
from itertools import permutations
from geopy.distance import great_circle
import seaborn as sns
import random
from geopy.distance import geodesic
import networkx as nx
from sklearn.metrics import silhouette_score

# --- Code Cell 2 ---
df_ec = pd.read_csv('C:/Users/jmana/OneDrive/Documentos/RTM_Project/dados/df.csv')

# --- Code Cell 3 ---
df = df_ec.copy()
df

# --- Code Cell 4 ---
# **1- Clusters de POCs (Clusterização Geográfica Melhorada)**
from sklearn.cluster import KMeans

# Converter coordenadas para valores numéricos
df["AVG_LATITUDE"] = pd.to_numeric(df["AVG_LATITUDE"], errors="coerce")
df["AVG_LONGITUDE"] = pd.to_numeric(df["AVG_LONGITUDE"], errors="coerce")

# Remover POCs sem coordenadas
df = df.dropna(subset=["AVG_LATITUDE", "AVG_LONGITUDE"])

# Definir o número de clusters (20% maior que o número de vendedores para evitar sobrecarga)
num_clusters = int(df["Vendedor"].nunique() * 1.2)

# Aplicar K-Means para agrupar POCs geograficamente
coords = df[["AVG_LATITUDE", "AVG_LONGITUDE"]].values
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(coords)

# --- Code Cell 5 ---
#**2- Distribuição de Vendedores por Cluster**
from scipy.spatial.distance import cdist

# Criar um dicionário para armazenar a distribuição de vendedores por cluster
cluster_vendedor_map = {}

# Criar um dicionário para contar os POCs por vendedor
pocs_por_vendedor = {vendedor: 0 for vendedor in df["Vendedor"].unique()}

# Criar matriz de distâncias entre clusters e vendedores para atribuição otimizada
vendedores_coords = df.groupby("Vendedor")[["AVG_LATITUDE", "AVG_LONGITUDE"]].mean().dropna()
clusters_coords = df.groupby("Cluster")[["AVG_LATITUDE", "AVG_LONGITUDE"]].mean().dropna()

dist_matrix = cdist(clusters_coords, vendedores_coords, metric="euclidean")
dist_df = pd.DataFrame(dist_matrix, index=clusters_coords.index, columns=vendedores_coords.index)

# Atribuir vendedores aos clusters considerando proximidade e balanceamento
for cluster in clusters_coords.index:
    vendedores_ordenados = dist_df.loc[cluster].sort_values().index.tolist()
    
    for vendedor in vendedores_ordenados:
        if pocs_por_vendedor[vendedor] < (len(df) / num_clusters):  # Garantir distribuição equilibrada
            cluster_vendedor_map[cluster] = vendedor
            pocs_por_vendedor[vendedor] += df[df["Cluster"] == cluster].shape[0]
            break

# Aplicar a nova distribuição ao DataFrame
df["Vendedor_Atribuído"] = df["Cluster"].map(cluster_vendedor_map)

# --- Code Cell 6 ---
#**3- Cálculo de Pareto Global (Correção do Top 20%)**
# Converter valores numéricos corretamente
df["Faturamento_Mensal_USD"] = pd.to_numeric(df["Faturamento_Mensal_USD"], errors="coerce")

# Aplicar o Pareto Global (Top 20% do faturamento geral)
threshold_global = df["Faturamento_Mensal_USD"].quantile(0.8)  
df["Alto_Valor"] = df["Faturamento_Mensal_USD"] >= threshold_global

# --- Code Cell 7 ---
#**4- Frequência Otimizada de Visitas**
# Ajustar a frequência de visitas para POCs de alto valor
df["Frequência_Ajustada"] = df["Frequência_de_Visita"]
df.loc[df["Alto_Valor"], "Frequência_Ajustada"] = 4

# --- Code Cell 8 ---
#**5- Comparação de RTM (Antes e Depois da Otimização)**
import numpy as np

# Aproximação para conversão de graus em quilômetros
KM_PER_DEGREE_LAT = 111  # 1 grau de latitude ≈ 111 km
df[["Delta_Lat", "Delta_Lon"]] = df.groupby("Vendedor")[["AVG_LATITUDE", "AVG_LONGITUDE"]].diff().abs()

# Converter as diferenças em quilômetros
df["Distância_Km_Lat"] = df["Delta_Lat"] * KM_PER_DEGREE_LAT
df["Distância_Km_Lon"] = df["Delta_Lon"] * KM_PER_DEGREE_LAT * np.cos(np.radians(df["AVG_LATITUDE"]))

# Calcular a distância total percorrida
df["Distância_Total_Km"] = df["Distância_Km_Lat"] + df["Distância_Km_Lon"]
df["Distância_Total_Km"] = df["Distância_Total_Km"].fillna(0)

# Ajustar o primeiro POC de cada vendedor com a média de distâncias seguintes
media_dist_por_vendedor = df.groupby("Vendedor")["Distância_Total_Km"].transform(lambda x: x[x > 0].mean())
df.loc[df.groupby("Vendedor").head(1).index, "Distância_Total_Km"] = media_dist_por_vendedor

# Comparação de métricas
comparacao_rtm = pd.DataFrame({
    "Métrica": ["Visitas Médias por Dia", "Frequência POCs Alto Valor", "Distância Total Percorrida"],
    "RTM Atual": [
        df.groupby("Vendedor")["Frequência_de_Visita"].sum().mean(),
        df[df["Alto_Valor"] == True]["Frequência_de_Visita"].mean(),
        df["Distância_Total_Km"].sum()
    ],
    "RTM Otimizado": [
        df.groupby("Vendedor_Atribuído")["Frequência_Ajustada"].sum().mean(),
        df[df["Alto_Valor"] == True]["Frequência_Ajustada"].mean(),
        df["Distância_Total_Km"].sum()
    ]
})

# --- Code Cell 9 ---
#**6- Implementação das Recomendações**
from scipy.spatial.distance import cdist

# Criar um limite de redistribuição de visitas por distância (evitar sobrecarga geográfica)
limite_distancia_km = 200

# Criar matriz de distâncias entre vendedores
vendedores_coords = df.groupby("Vendedor_Atribuído")[["AVG_LATITUDE", "AVG_LONGITUDE"]].mean().dropna()
dist_matrix = cdist(vendedores_coords, vendedores_coords, metric="euclidean")
dist_df = pd.DataFrame(dist_matrix, index=vendedores_coords.index, columns=vendedores_coords.index)

# Recalcular a contagem de visitas por vendedor
visitas_por_vendedor = df.groupby("Vendedor_Atribuído")["Frequência_Ajustada"].sum()

# Identificar vendedores que ainda têm capacidade de receber visitas**
vendedores_com_folga = visitas_por_vendedor[visitas_por_vendedor < 240].index

# Identificar POCs com menor número de visitas para redistribuição**
pocs_para_redistribuir = df[df["Frequência_Ajustada"] < 10].index

# Redistribuir visitas para vendedores abaixo de 240 visitas**
for poc in pocs_para_redistribuir:
    vendedor_origem = df.at[poc, "Vendedor_Atribuído"]

    # Encontrar vendedores disponíveis próximos dentro do limite de distância
    if vendedor_origem in dist_df.index:
        vendedores_proximos = dist_df.loc[vendedor_origem][dist_df.loc[vendedor_origem] <= (limite_distancia_km / 111)].sort_values().index.tolist()
    else:
        vendedores_proximos = []

    # Transferir para vendedores que ainda têm capacidade
    for vendedor_destino in vendedores_proximos:
        if vendedor_destino in vendedores_com_folga and visitas_por_vendedor[vendedor_destino] + df.at[poc, "Frequência_Ajustada"] <= 240:
            df.at[poc, "Vendedor_Atribuído"] = vendedor_destino
            visitas_por_vendedor[vendedor_destino] += df.at[poc, "Frequência_Ajustada"]
            visitas_por_vendedor[vendedor_origem] -= df.at[poc, "Frequência_Ajustada"]
            break  # Passar para o próximo POC

# --- Code Cell 10 ---
pd.set_option('display.max_columns', None)
df

# --- Code Cell 11 ---
# Métricas globais importantes para reconfiguração

# Número de clusters
num_clusters = df["Cluster"].nunique()

# Distribuição de vendedores por cluster
vendedores_por_cluster = df.groupby("Cluster")["Vendedor_Atribuído"].nunique()

# Quantidade de POCs de alto valor
pocs_alto_valor = df["Alto_Valor"].sum()

# Distância total percorrida
distancia_total_percorrida = df["Distância_Total_Km"].sum()

# Média de visitas por vendedor
media_visitas_por_vendedor = df.groupby("Vendedor_Atribuído")["Frequência_Ajustada"].mean()

# Média de faturamento mensal por POC
media_faturamento_por_poc = df["Faturamento_Mensal_USD"].mean()

# Resumo das métricas globais
metricas_globais = {
    "Número de Clusters": num_clusters,
    "Distribuição de Vendedores por Cluster": vendedores_por_cluster.describe(),
    "Quantidade de POCs de Alto Valor": pocs_alto_valor,
    "Distância Total Percorrida (Km)": distancia_total_percorrida,
    "Média de Visitas por Vendedor": media_visitas_por_vendedor.mean(),
    "Média de Faturamento Mensal por POC (USD)": media_faturamento_por_poc
}

# Exibir as métricas globais
for key, value in metricas_globais.items():
    print(f"{key}: {value}")

# --- Markdown Cell 12 ---
# -------------------------------------------------------------------------------------------------

# --- Code Cell 13 ---
import folium
import numpy as np

# Definir o vendedor que deseja visualizar
vendedor_selecionado = "ECECB046"  # Substitua pelo vendedor desejado

# Filtrar o DataFrame para exibir apenas os POCs do vendedor selecionado
df_vendedor = df[df["Vendedor_Atribuído"] == vendedor_selecionado]

# Calcular a média de quilômetros percorridos pelo vendedor
media_km_vendedor = df_vendedor["Distância_Total_Km"].mean()

# Criar um mapa centralizado na média das coordenadas do vendedor
map_center = [df_vendedor["AVG_LATITUDE"].mean(), df_vendedor["AVG_LONGITUDE"].mean()]
mapa_vendedor = folium.Map(location=map_center, zoom_start=6)

# Definir cores para os dias da semana
cores_dias = {
    "seg": "blue",
    "ter": "green",
    "qua": "red",
    "qui": "purple",
    "sex": "orange",
    "sab": "pink",
    "dom": "brown"
}

# Criar FeatureGroup para cada dia da semana
dias_unicos = df_vendedor["Dia_da_Semana"].dropna().unique()
dias_feature = {dia: folium.FeatureGroup(name=f"Dia {dia}") for dia in dias_unicos}

# Adicionar POCs ao mapa coloridos pelo dia da semana
for _, row in df_vendedor.iterrows():
    dia = row["Dia_da_Semana"].lower() if isinstance(row["Dia_da_Semana"], str) else "outros"
    cor = cores_dias.get(dia, "gray")  # Cor padrão caso o dia não esteja no dicionário

    if pd.notna(row["AVG_LATITUDE"]) and pd.notna(row["AVG_LONGITUDE"]):
        folium.CircleMarker(
            location=[row["AVG_LATITUDE"], row["AVG_LONGITUDE"]],
            radius=5,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.7,
            popup=folium.Popup(f"""
                <b>Vendedor:</b> {row["Vendedor_Atribuído"]} <br>
                <b>POC:</b> {row["POC"]} <br>
                <b>Faturamento:</b> ${row["Faturamento_Mensal_USD"]:.2f} <br>
                <b>Distância:</b> {row["Distância_Total_Km"]:.2f} km <br>
                <b>Dia da Visita:</b> {row["Dia_da_Semana"]} <br>
                <b>Frequência de Visita:</b> {row["Frequência_Ajustada"]} vezes/mês <br>
                <b>Média de KM Percorridos pelo Vendedor:</b> {media_km_vendedor:.2f} km
            """, max_width=250),
        ).add_to(dias_feature[dia])

# Adicionar grupos ao mapa
for dia in dias_feature.values():
    dia.add_to(mapa_vendedor)

# Adicionar controle de camadas
folium.LayerControl().add_to(mapa_vendedor)

# Exibir o mapa interativo
mapa_vendedor

# --- Code Cell 14 ---
import folium
import numpy as np

# Criar um mapa centralizado na média das coordenadas
map_center = [df["AVG_LATITUDE"].mean(), df["AVG_LONGITUDE"].mean()]
mapa_clusters = folium.Map(location=map_center, zoom_start=6)

# Criar um dicionário de cores para os clusters
clusters_unicos = df["Cluster"].unique()
cores = ["#" + ''.join(np.random.choice(list('0123456789ABCDEF'), 6)) for _ in range(len(clusters_unicos))]
cluster_cores = dict(zip(clusters_unicos, cores))

# Criar FeatureGroup para cada cluster
clusters_feature = {cluster: folium.FeatureGroup(name=f"Cluster {cluster}") for cluster in clusters_unicos}

# Adicionar POCs ao mapa coloridos pelos clusters
for _, row in df.iterrows():
    cluster = row["Cluster"]
    if pd.notna(row["AVG_LATITUDE"]) and pd.notna(row["AVG_LONGITUDE"]):
        folium.CircleMarker(
            location=[row["AVG_LATITUDE"], row["AVG_LONGITUDE"]],
            radius=5,
            color=cluster_cores[cluster],
            fill=True,
            fill_color=cluster_cores[cluster],
            fill_opacity=0.7,
            popup=folium.Popup(f"""
                <b>Cluster:</b> {cluster} <br>
                <b>Vendedor:</b> {row["Vendedor_Atribuído"]} <br>
                <b>POC:</b> {row["POC"]} <br>
                <b>Faturamento:</b> ${row["Faturamento_Mensal_USD"]:.2f} <br>
                <b>Distância:</b> {row["Distância_Total_Km"]:.2f} km
                <b>Dia da Visita:</b> {row["Dia_da_Semana"]}<br>
                <b>Frequência de Visita:</b> {row["Frequência_Ajustada"]} vezes/mês
            """, max_width=250),
        ).add_to(clusters_feature[cluster])

# Adicionar grupos ao mapa
for cluster in clusters_feature.values():
    cluster.add_to(mapa_clusters)

# Adicionar controle de camadas
folium.LayerControl().add_to(mapa_clusters)

# Exibir o mapa interativo
mapa_clusters

