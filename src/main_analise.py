# Converted from main_analise.ipynb
# --- Markdown Cell 1 ---
# ## **Bibliotecas**

# --- Code Cell 2 ---
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

# --- Markdown Cell 3 ---
# ## **Carregamento de dados**

# --- Code Cell 4 ---
file_path = 'C:/Users/jmana/OneDrive/Documentos/RTM_Project/dados/Dados_RTM.csv'
data = pd.read_csv(file_path)

# --- Code Cell 5 ---
df_ec = data[data['COUNTRY_NAME'] == 'EC'].reset_index(drop=True)
df_pe = data[data['COUNTRY_NAME'] == 'PE'].reset_index(drop=True)

# --- Code Cell 6 ---
df_ec

# --- Markdown Cell 7 ---
# | Numero de vendedores df_ec

# --- Code Cell 8 ---
num_vendedores_unicos = df_ec['Vendedor'].nunique()
print(f"Número de vendedores únicos: {num_vendedores_unicos}")

# --- Markdown Cell 9 ---
# ## **Filtragem / Limpeza**

# --- Markdown Cell 10 ---
# Remover geolocalizações nulas

# --- Code Cell 11 ---
df_ec = df_ec[(df_ec['AVG_LATITUDE'] != 0) | (df_ec['AVG_LONGITUDE'] != 0)]

# --- Markdown Cell 12 ---
# Adicionando coluna de faturamento formatada

# --- Code Cell 13 ---
df_ec["Faturamento Mensal USD (formatado)"] = df_ec["Faturamento Mensal USD"].apply(lambda x: f"${x:,.2f}")

# --- Code Cell 14 ---
# Confirmar se o tipo de dado deveria ser float
df_ec["Faturamento Mensal USD"] = df_ec["Faturamento Mensal USD"].astype(float)
print(df_ec["Faturamento Mensal USD"].dtype)

# --- Code Cell 15 ---
df_ec.columns

# --- Code Cell 16 ---
df_ec.dtypes

# --- Markdown Cell 17 ---
# ## **Visualização geral**

# --- Code Cell 18 ---
# Criação do gráfico usando scatter_mapbox sem token
fig = px.scatter_mapbox(
    df_ec,
    lat="AVG_LATITUDE",
    lon="AVG_LONGITUDE",
    title="",
    color="Vendedor",  # Coloração por vendedor
    zoom=7,  # Nível de zoom
    center=dict(lat=-1.5, lon=-78.183406),  # Centro no Equador
    height=800,
    width=800,
    color_discrete_sequence=px.colors.qualitative.Set1
)

# Configurações de layout para o estilo OpenStreetMap
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": -1.54, "lon": -79.983406},  # Usa o estilo OpenStreetMap que não requer token
    margin={"r":0,"t":70,"l":0,"b":0}  # Remove margens para um ajuste perfeito
)
# Alterar a fonte da legenda para Roboto
fig.update_layout(
    legend=dict(
        font=dict(
            family="Roboto",
            size=12,
            color="black"
        )
    )
)
# Adicionar título ao gráfico
fig.update_layout(title_text="", 
                  title_font_family="Roboto", 
                  title_font_size=24, 
                  title_font_weight="bold", 
                  title_font_color="black",
                  title_y=0.964,
                  title_x=0.5)
# Exibir o gráfico
fig.show()

# --- Markdown Cell 19 ---
# ## **Limpeza e adição de dados**

# --- Markdown Cell 20 ---
# **Frequência de Visitas Mensais**
# | Código | Valor Equivalente | Frequência de Visita |
# |--------|------------------|----------------------|
# | 1      | 0.25            | 1 vez no mês        |
# | 2      | 0.5             | 2 vezes no mês      |
# | 4      | 1               | Todas as semanas do mês |

# --- Markdown Cell 21 ---
# ### Diretrizes para Duplicação de Registros  
# 
# - **Se a análise for baseada em cada visita individualmente** →  **Sim, duplique os registros.**  
# - **Se o foco for análises agregadas** (exemplo: faturamento por cliente) →  **Evite duplicar, crie uma coluna de ponderação.**  

# --- Code Cell 22 ---
# Criar a coluna "Visita Semanal" baseada na Frequência de Visita
mapping_frequencia = {1: 0.25, 2: 0.5, 4: 1.0}
df_ec["Visita Semanal"] = df_ec["Frequência de Visita"].map(mapping_frequencia)

# --- Markdown Cell 23 ---
# criando colunas para distribuição semanal

# --- Code Cell 24 ---
# Ajustar a distribuição com base na "Semana da Visita"
def ajustar_visitas_por_semana(row):
    semanas = [0, 0, 0, 0]  # Inicializa como sem visitas
    
    if not pd.isna(row["Semana da Visita"]):  # Verifica se a semana da visita está preenchida
        semana_visita = int(row["Semana da Visita"]) - 1  # Ajusta índice (1 → 0, 2 → 1)
        semanas[semana_visita] = 1  # Marca a semana correta com visita

    return semanas

# Aplicar a função para definir a distribuição real das visitas por semana
df_ec[["Semana_1", "Semana_2", "Semana_3", "Semana_4"]] = df_ec.apply(ajustar_visitas_por_semana, axis=1, result_type="expand")

# --- Code Cell 25 ---
# Preencher os valores NaN na "Semana da Visita" com visitas em todas as semanas (1 em todas)
df_ec.loc[df_ec["Semana da Visita"].isna(), ["Semana_1", "Semana_2", "Semana_3", "Semana_4"]] = [1, 1, 1, 1]

# --- Code Cell 26 ---
# Substituir os valores NaN na coluna "Semana da Visita" por "CMPL" - "COMPLETE"
df_ec["Semana da Visita"] = df_ec["Semana da Visita"].fillna("CMPL")

# --- Code Cell 27 ---
df_ec.head(20)

# --- Code Cell 28 ---
dias_unicos_visita = df_ec['Dia da Visita'].unique()
print(dias_unicos_visita)

# --- Markdown Cell 29 ---
# **Adicionando dias da semana ao dataset**

# --- Code Cell 30 ---
# Mapping of numeric days to string days
dias_semana = {2: 'seg', 3: 'ter', 4: 'qua', 5: 'qui', 6: 'sex', 7: 'sab'}

# Create a new column with string values for the day of the visit
df_ec['Dia da Semana'] = df_ec['Dia da Visita'].map(dias_semana)

# Display the updated dataframe
df_ec.head()

# --- Markdown Cell 31 ---
# **Adicionando "_" a todas os titulos de coluna**

# --- Code Cell 32 ---
# df_ec.columns = df_ec.columns.str.replace(' ', '_')
df_ec.columns = df_ec.columns.str.replace(' ', '_')

df_ec.head()

# --- Markdown Cell 33 ---
# ## **Filtragem por faturamento**

# --- Code Cell 34 ---
# Garantir que a coluna de faturamento está no formato correto
df_ec["Faturamento_Mensal_USD"] = pd.to_numeric(df_ec["Faturamento_Mensal_USD"], errors="coerce")

# Ordenar os POCs pelo faturamento em ordem decrescente
df_ec_sorted = df_ec.sort_values(by="Faturamento_Mensal_USD", ascending=False).reset_index(drop=True)

# Calcular o Percentil 90 e 95
percentil_60 = df_ec_sorted["Faturamento_Mensal_USD"].quantile(0.60)
percentil_90 = df_ec_sorted["Faturamento_Mensal_USD"].quantile(0.90)
percentil_95 = df_ec_sorted["Faturamento_Mensal_USD"].quantile(0.95)

# Calcular o faturamento acumulado
df_ec_sorted["Faturamento Acumulado"] = df_ec_sorted["Faturamento_Mensal_USD"].cumsum()

# Determinar o ponto onde 80% do faturamento é atingido (Regra de Pareto)
faturamento_total = df_ec_sorted["Faturamento_Mensal_USD"].sum()
df_ec_sorted["Porcentagem Acumulada"] = df_ec_sorted["Faturamento Acumulado"] / faturamento_total

# Selecionar as POCs que representam 80% do faturamento total
pareto_pocs = df_ec_sorted[df_ec_sorted["Porcentagem Acumulada"] <= 0.80]

# Selecionar as POCs com faturamento acima do Percentil 90
top_faturamentos = df_ec_sorted[df_ec_sorted["Faturamento_Mensal_USD"] >= percentil_90]

# Exibir os resultados corrigidos
resultados = {
    "Percentil 60": percentil_60,
    "Percentil 90": percentil_90,
    "Percentil 95": percentil_95,
    "Faturamento Total": faturamento_total,
    "Número de POCs no Pareto (80%)": len(pareto_pocs),
    "Número de POCs acima do Percentil 90": len(top_faturamentos),
}

resultados

# --- Markdown Cell 35 ---
# - **Percentil 90:** POCs que faturam **mais de $1,134.70** mensais estão no **top 10% de faturamento**.
# - **Percentil 95:** POCs que faturam **mais de $1,951.00** mensais estão no **top 5% de faturamento**.
# - **Faturamento Total:** **$84,666,950** é o faturamento total de todas as POCs analisadas.
# - **Número de POCs no Pareto 80/20:** **15,243 POCs** representam **80% do faturamento total**.
# - **Número de POCs acima do Percentil 90:** **11,011 POCs** faturam **mais do que 90% das outras**.

# --- Code Cell 36 ---
# Filtrar as POCs que estão acima do percentil 60
df_ec_top_pocs = df_ec[df_ec["Faturamento_Mensal_USD"] >= 220.56]  

# --- Code Cell 37 ---
df_ec_top_pocs.sort_values(by="Faturamento_Mensal_USD", ascending=True)

# --- Code Cell 38 ---
df_ec_top_pocs['Faturamento_Mensal_USD'].describe()

# --- Code Cell 39 ---
df_ec['Faturamento_Mensal_USD'].sum()

# --- Code Cell 40 ---
df_ec_top_pocs['Faturamento_Mensal_USD'].sum()

# --- Code Cell 41 ---
df_ec_top_pocs.sort_values(by="Faturamento_Mensal_USD", ascending=True)

# --- Code Cell 42 ---
df_ec_top_pocs['Faturamento_Mensal_USD'].describe()

# --- Markdown Cell 43 ---
# - **Top faturamentos - Mapa**

# --- Code Cell 44 ---
# Criar um mapa centrado na média das coordenadas
mapa = folium.Map(location=[df_ec_top_pocs["AVG_LATITUDE"].mean(), df_ec_top_pocs["AVG_LONGITUDE"].mean()], zoom_start=7)

# Adicionar um cluster de marcadores
marker_cluster = MarkerCluster().add_to(mapa)

# Adicionar marcadores ao cluster
for idx, row in df_ec_top_pocs.iterrows():
    folium.Marker(
        location=[row["AVG_LATITUDE"], row["AVG_LONGITUDE"]],
        popup=folium.Popup(f"POC: {row['POC']}<br>Vendedor: {row['Vendedor']}<br>Faturamento Mensal USD: ${row['Faturamento_Mensal_USD']:.2f}", max_width=300),
        icon=folium.Icon(color="blue" if row["Faturamento_Mensal_USD"] < 1000 else "green" if row["Faturamento_Mensal_USD"] < 5000 else "red")
    ).add_to(marker_cluster)
    
    # Adicionar círculo proporcional ao faturamento
    folium.Circle(
        location=[row["AVG_LATITUDE"], row["AVG_LONGITUDE"]],
        radius=row["Faturamento_Mensal_USD"] / 10,  # Ajuste o divisor para controlar o tamanho dos círculos
        color='crimson',
        fill=True,
        fill_color='crimson'
    ).add_to(mapa)

# Adicionar legenda personalizada
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 200px; height: 150px; 
            background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
            ">
    <div style="padding: 10px;">
        <b>Legenda</b><br>
        <i class="fa fa-map-marker fa-2x" style="color:blue"></i> < $1000<br>
        <i class="fa fa-map-marker fa-2x" style="color:green"></i> $1000 - $5000<br>
        <i class="fa fa-map-marker fa-2x" style="color:red"></i> > $5000<br>
    </div>
</div>
'''
mapa.get_root().html.add_child(folium.Element(legend_html))

# Exibir o mapa
mapa

# --- Markdown Cell 45 ---
# - **Contagem de visitas**

# --- Code Cell 46 ---
# Calcular o número de pocs por dia por vendedor
pocs_por_dia_vendedor = df_ec_top_pocs.groupby(['Vendedor'])['POC'].count().reset_index()

# Renomear colunas para melhor compreensão
pocs_por_dia_vendedor.rename(columns={"POC": "Número de pocs"}, inplace=True)
pocs_por_dia_vendedor.sort_values(by="Número de pocs", ascending=False).head(20)

# --- Markdown Cell 47 ---
# | Numero de Vendedores no dataset original

# --- Code Cell 48 ---
num_vendedores_unicos = df_ec['Vendedor'].nunique()
print(f"Número de vendedores únicos: {num_vendedores_unicos}")

# --- Markdown Cell 49 ---
# | Numero de Vendedores no dataset filtrado por faturamento

# --- Code Cell 50 ---
num_vendedores_unicos_top_pocs = df_ec_top_pocs['Vendedor'].nunique()
print(f"Número de vendedores únicos: {num_vendedores_unicos_top_pocs}")

# --- Code Cell 51 ---
# Calcular o total de visitas por mês para cada vendedor
visitas_por_mes = df_ec_top_pocs.groupby("Vendedor")["Frequência_de_Visita"].sum().reset_index()

# Renomear a coluna para indicar que representa visitas mensais
visitas_por_mes.rename(columns={"Frequência de Visita": "Total Visitas Mensais"}, inplace=True)

# --- Code Cell 52 ---
visitas_por_mes.sort_values(by='Frequência_de_Visita', ascending=False, inplace=True)
visitas_por_mes

# --- Code Cell 53 ---
df_ec_top_pocs

# --- Code Cell 54 ---
# Definir o caminho para salvar o arquivo CSV
csv_file_path = 'C:/Users/jmana/OneDrive/Documentos/RTM_Project/dados/visitas_por_mes.csv'

# Salvar o dataframe como um arquivo CSV
visitas_por_mes.to_csv(csv_file_path, index=False)

# --- Code Cell 55 ---
import plotly.express as px

# Criar o gráfico de barra interativo
fig = px.bar(visitas_por_mes, x='Vendedor', y='Frequência_de_Visita', title='Frequência Total de Visitas por Vendedor')

# Exibir o gráfico
fig.show()

# --- Code Cell 56 ---
visitas_por_mes['Frequência_de_Visita'].sum()

# --- Code Cell 57 ---
visitas_por_mes.describe()

# --- Code Cell 58 ---
import plotly.express as px

# Criar o gráfico de boxplot interativo
fig = px.box(visitas_por_mes, x='Frequência_de_Visita', title='Boxplot de Visitas Mensais por Vendedor')

# Ajustar o layout do gráfico
fig.update_layout(
    xaxis_title='Frequência de Visita',
    yaxis_title='Total de Visitas Mensais',
    width=800,
    height=600
)

# Exibir o gráfico
fig.show()

# --- Markdown Cell 59 ---
# ## **Ajuste - Localização, Visitas &  Faturamento**

# --- Markdown Cell 60 ---
# - CTRL + K + C = Comentar
# - CTRL + K + U = Descomentar

# --- Code Cell 61 ---
df = df_ec_top_pocs.copy()

# --- Markdown Cell 62 ---
# ## **Visualização de faturamento**

# --- Code Cell 63 ---
# Ordenar o dataframe por faturamento
df_ec_top_pocs_sorted = df_ec_top_pocs.sort_values(by="Faturamento_Mensal_USD", ascending=False)

# Converter a coluna 'POC' para string
df_ec_top_pocs_sorted['POC'] = df_ec_top_pocs_sorted['POC'].astype(str)

# Criar o gráfico de barras interativo
fig = px.bar(df_ec_top_pocs_sorted, x='POC', y='Faturamento_Mensal_USD', title='Faturamento por POC')

# Ajustar o layout do gráfico
fig.update_layout(
    xaxis_title='POC',
    yaxis_title='Faturamento Mensal USD',
    xaxis_tickangle=-90  # Rotacionar os rótulos do eixo x para melhor visualização
)

# Exibir o gráfico
fig.show()

# --- Code Cell 64 ---
# Filtrar as POCs que faturam acima de:
pocs_acima = df_ec_top_pocs[df_ec_top_pocs['Faturamento_Mensal_USD'] > 190000]

# Contar o número de POCs
num_pocs_acima = pocs_acima.shape[0]
print(f"Número de POCs que faturam acima de 190k dólares: {num_pocs_acima}")

# --- Code Cell 65 ---
# Separar o dataframe em quartis com base no faturamento mensal
df_ec_top_pocs['Quartil_Faturamento'] = pd.qcut(df_ec_top_pocs['Faturamento_Mensal_USD'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# Exibir o dataframe com a nova coluna de quartil
df_ec_top_pocs

# --- Code Cell 66 ---
# Separar o dataframe em quartis com base no faturamento mensal
df_ec_top_pocs['Quartil_Faturamento'] = pd.qcut(df_ec_top_pocs['Faturamento_Mensal_USD'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# Criar o gráfico de boxplot para visualizar a divisão de quartis
plt.figure(figsize=(10, 6))
sns.boxplot(x='Quartil_Faturamento', y='Faturamento_Mensal_USD', data=df_ec_top_pocs)
plt.title('Divisão de Quartis do Faturamento Mensal')
plt.xlabel('Quartil')
plt.ylabel('Faturamento Mensal USD')
plt.show()

# --- Code Cell 67 ---
df_ec_top_pocs[df_ec_top_pocs['Quartil_Faturamento'] == "Q4"].describe()

# --- Code Cell 68 ---
df_ec_top_pocs

# --- Code Cell 69 ---
import matplotlib.pyplot as plt
import seaborn as sns

# Verificar se a coluna existe e o DataFrame não está vazio
if "Frequência_de_Visita" in df_ec_top_pocs.columns and not df_ec_top_pocs.empty:

    # Configuração do gráfico
    plt.figure(figsize=(8, 5))
    sns.boxplot(x="Dia_da_Semana", y="Frequência_de_Visita", data=df_ec_top_pocs, color="green", showfliers=True)

    # Adicionar linha da capacidade ideal (48 visitas)
    plt.axhline(y=48, color='red', linestyle="--", linewidth=1.5, label="Capacidade Ideal (48 visitas)")

    # Personalizar rótulos e título
    plt.xlabel("Semana da Visita", fontsize=12)
    plt.ylabel("Número de Visitas", fontsize=12)
    plt.title("Distribuição de Visitas por Dia da Semana - EC", fontsize=14, fontweight="bold")

    # Adicionar legenda
    plt.legend()

    # Exibir o gráfico
    plt.show()
else:
    print("Erro: A coluna 'Frequência_de_Visita' não existe ou o DataFrame está vazio.")

# --- Code Cell 70 ---
# Definir o caminho para salvar o arquivo CSV
csv_file_path_df_ec_top_pocs = 'C:/Users/jmana/OneDrive/Documentos/RTM_Project/dados/df_ec_top_pocs_novo.csv'

# Salvar o dataframe como um arquivo CSV
df_ec_top_pocs.to_csv(csv_file_path_df_ec_top_pocs, index=False)

# --- Markdown Cell 71 ---
# ************************************************************************************************************************************************************************************************************************************************************************

# --- Markdown Cell 72 ---
# ************************************************************************************************************************************************************************************************************************************************************************

# --- Markdown Cell 73 ---
# ************************************************************************************************************************************************************************************************************************************************************************

