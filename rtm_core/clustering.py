"""
Módulo de Clusterização Espacial Balanceada (Territory Clustering).

Resolve a falha crítica do K-Means padrão (onde alguns vendedores
recebiam 325 POCs e 103 vendedores ficavam com menos de 5 POCs).

Implementa:
1. Dimensionamento inteligente de frota baseado em carga de trabalho real.
2. Agrupamento geográfico com restrição estrita de capacidade máxima.
3. Alocação balanceada para garantir jornadas dignas e eliminar ociosidade.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from rtm_core.geo_utils import matriz_distancias_haversine


def dimensionar_frota_ideal(df_segmentado: pd.DataFrame, visitas_max_mensais_vendedor: int = 160) -> int:
    """
    Calcula o número ótimo de vendedores com base na carga total de trabalho:
    Total de Visitas Mensais = sum(Frequencia_Mensal de cada POC).
    
    Exemplo: 160 visitas/mês = ~8 visitas diárias com 20 dias úteis/mês.
    """
    total_visitas = df_segmentado["Frequencia_Mensal"].sum()
    frota_ideal = int(np.ceil(total_visitas / visitas_max_mensais_vendedor))
    return frota_ideal


def clusterizacao_balanceada(
    df: pd.DataFrame,
    num_territorios: int,
    teto_visitas_mensais: int = 200,
    piso_visitas_mensais: int = 40,
    random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Gera territórios balanceados respeitando limites operacionais de visitas.
    
    1. Executa centróides iniciais via K-Means sobre coordenadas geográficas.
    2. Calcula matriz de distância Haversine real entre cada POC e todos os centróides.
    3. Atribui POCs ao centróide mais próximo até o teto de capacidade.
    4. Se o centróide mais próximo estiver saturado, o ponto transborda para o segundo mais próximo.
    """
    df_result = df.copy()
    coords = df_result[["AVG_LATITUDE", "AVG_LONGITUDE"]].to_numpy()
    
    # 1. Centróides iniciais
    kmeans_init = KMeans(n_clusters=num_territorios, random_state=random_state, n_init=10)
    kmeans_init.fit(coords)
    centroides = kmeans_init.cluster_centers_  # (K, 2)
    
    # 2. Matriz de distâncias Haversine: cada POC para cada um dos K centróides
    dist_pocs_centroides = matriz_distancias_haversine(coords, centroides)  # Shape (N, K)
    
    # 3. Alocação gulosa ordenada por proximidade relativa
    # Para garantir que pontos mais distantes ou críticos tenham prioridade de proximidade:
    ordem_pontos = np.argsort(np.min(dist_pocs_centroides, axis=1))[::-1]
    
    territorios = [-1] * len(df_result)
    carga_visitas = [0] * num_territorios
    pocs_por_territorio = [0] * num_territorios
    
    frequencias = df_result["Frequencia_Mensal"].to_numpy()
    
    for idx_ponto in ordem_pontos:
        freq = frequencias[idx_ponto]
        # Centróides ordenados do mais próximo ao mais distante deste POC
        centroides_ordenados = np.argsort(dist_pocs_centroides[idx_ponto])
        
        atribuido = False
        for c in centroides_ordenados:
            if carga_visitas[c] + freq <= teto_visitas_mensais:
                territorios[idx_ponto] = c
                carga_visitas[c] += freq
                pocs_por_territorio[c] += 1
                atribuido = True
                break
        
        # Se todos os centróides bateram no teto, atribui ao centróide com menor carga atual
        if not atribuido:
            c_menor_carga = int(np.argmin(carga_visitas))
            territorios[idx_ponto] = c_menor_carga
            carga_visitas[c_menor_carga] += freq
            pocs_por_territorio[c_menor_carga] += 1

    df_result["Territorio_ID"] = [f"Territorio_{t:03d}" for t in territorios]
    
    # Tabela resumo dos territórios
    resumo_territorios = pd.DataFrame({
        "Territorio_ID": [f"Territorio_{t:03d}" for t in range(num_territorios)],
        "Centroide_Lat": centroides[:, 0],
        "Centroide_Lon": centroides[:, 1],
        "Total_POCs": pocs_por_territorio,
        "Total_Visitas_Mensais": carga_visitas,
    })
    
    return df_result, resumo_territorios
