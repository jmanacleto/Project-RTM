"""
Módulo de Roteirização e Otimização de Sequenciamento (TSP / Routing).

Resolve o problema do Caixeiro-Viajante (Traveling Salesperson Problem)
dentro de cada território comercial usando:
1. Setorização Geográfica por Dia (um bairro/região para cada dia da semana).
2. Otimização TSP com Heurística do Vizinho Mais Próximo e Refinamento 2-Opt.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from rtm_core.geo_utils import matriz_distancias_haversine


def resolver_tsp_vizinho_mais_proximo(coords: np.ndarray) -> tuple[list[int], float]:
    """
    Heurística de Vizinho Mais Próximo (Nearest Neighbor) + Refinamento 2-Opt.
    
    Recebe coords: array (N, 2) de coordenadas dos POCs.
    Retorna:
        rota_ordenada: Lista de índices na ordem ótima de visitação.
        distancia_total_km: Soma real dos deslocamentos em km.
    """
    n = len(coords)
    if n <= 1:
        return [0], 0.0

    dist_matrix = matriz_distancias_haversine(coords, coords)
    
    # 1. Rota inicial pelo vizinho mais próximo
    visitados = [False] * n
    rota = [0]
    visitados[0] = True
    
    atual = 0
    for _ in range(n - 1):
        proximo = -1
        menor_dist = np.inf
        for j in range(n):
            if not visitados[j] and dist_matrix[atual, j] < menor_dist:
                menor_dist = dist_matrix[atual, j]
                proximo = j
        rota.append(proximo)
        visitados[proximo] = True
        atual = proximo

    # 2. Refinamento 2-Opt para desatar cruzamentos de rotas
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue
                d_antiga = dist_matrix[rota[i - 1], rota[i]] + dist_matrix[rota[j - 1], rota[j]]
                d_nova = dist_matrix[rota[i - 1], rota[j - 1]] + dist_matrix[rota[i], rota[j]]
                if d_nova < d_antiga - 1e-4:
                    rota[i:j] = reversed(rota[i:j])
                    melhorou = True

    # 3. Calcular distância final da rota ordenada
    distancia_total = 0.0
    for idx in range(n - 1):
        distancia_total += dist_matrix[rota[idx], rota[idx + 1]]

    return rota, distancia_total


def agendar_rotas_semanais(
    df_territorio: pd.DataFrame,
    dias_semana: list[str] = ["seg", "ter", "qua", "qui", "sex"]
) -> pd.DataFrame:
    """
    Divide o território em setores geográficos contíguos (um setor por dia da semana)
    e executa o TSP separadamente para cada dia, evitando que o vendedor fique
    cruzando a cidade de um lado para o outro.
    """
    df_res = df_territorio.copy()
    coords = df_res[["AVG_LATITUDE", "AVG_LONGITUDE"]].to_numpy()
    num_dias = len(dias_semana)
    
    if len(coords) < num_dias:
        # Menos lojas que dias úteis: atribui 1 por dia
        df_res["Dia_Semana"] = [dias_semana[i % num_dias] for i in range(len(df_res))]
        df_res["Ordem_Visita_Dia"] = 1
        return df_res

    # 1. Setorização por dia: Agrupa lojas próximas espacialmente para o mesmo dia
    kmeans_dias = KMeans(n_clusters=num_dias, random_state=42, n_init=10)
    setores = kmeans_dias.fit_predict(coords)
    mapa_dias = {i: dias_semana[i] for i in range(num_dias)}
    df_res["Dia_Semana"] = [mapa_dias[s] for s in setores]
    
    # 2. Para cada dia, ordenar as lojas via TSP
    dfs_ordenados_dia = []
    for dia in dias_semana:
        df_dia = df_res[df_res["Dia_Semana"] == dia].copy()
        if df_dia.empty:
            continue
        coords_dia = df_dia[["AVG_LATITUDE", "AVG_LONGITUDE"]].to_numpy()
        ordem_tsp, _ = resolver_tsp_vizinho_mais_proximo(coords_dia)
        df_dia_ordenado = df_dia.iloc[ordem_tsp].copy()
        df_dia_ordenado["Ordem_Visita_Dia"] = np.arange(1, len(df_dia_ordenado) + 1)
        dfs_ordenados_dia.append(df_dia_ordenado)
        
    df_final = pd.concat(dfs_ordenados_dia).reset_index(drop=True)
    return df_final
