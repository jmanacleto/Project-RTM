"""
Módulo de Segmentação Comercial & Regras de Route-to-Market (RTM).

Responsável por:
1. Análise real de Pareto / Curva ABC sobre receita acumulada (Lorenz).
2. Definição da matriz de atendimento e frequência padrão de varejo (1x, 2x, 4x/mês).
3. Detecção de pontos de rodovia / 'Beira de Estrada' via isolamento espacial.
"""
import pandas as pd
import numpy as np
from rtm_core.geo_utils import matriz_distancias_haversine


def aplicar_curva_abc_pareto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifica cada POC na Curva ABC com base na contribuição acumulada de faturamento:
    - Tier A: POCs que compõem os primeiros 80% da receita da empresa.
    - Tier B: POCs que compõem os próximos 15% (80% a 95%).
    - Tier C: POCs da cauda longa (últimos 5% da receita).
    """
    df_sorted = df.sort_values(by="Faturamento_Mensal_USD", ascending=False).copy()
    faturamento_total = df_sorted["Faturamento_Mensal_USD"].sum()
    
    if faturamento_total > 0:
        df_sorted["Receita_Acumulada"] = df_sorted["Faturamento_Mensal_USD"].cumsum()
        df_sorted["Pct_Receita_Acumulada"] = df_sorted["Receita_Acumulada"] / faturamento_total
    else:
        df_sorted["Pct_Receita_Acumulada"] = 1.0

    # Classificação ABC
    condicoes = [
        df_sorted["Pct_Receita_Acumulada"] <= 0.80,
        df_sorted["Pct_Receita_Acumulada"] <= 0.95,
    ]
    escolhas = ["Tier_A", "Tier_B"]
    df_sorted["Classificacao_ABC"] = np.select(condicoes, escolhas, default="Tier_C")

    # Mapeamento de Frequência Comercial Padrão de Varejo (CPG):
    # Tier A = 4 visitas/mês (Semanal - toda semana no mesmo dia)
    # Tier B = 2 visitas/mês (Quinzenal - a cada 15 dias)
    # Tier C = 1 visita/mês  (Mensal - 1x ao mês)
    mapa_frequencia = {
        "Tier_A": 4,
        "Tier_B": 2,
        "Tier_C": 1
    }
    df_sorted["Frequencia_Mensal"] = df_sorted["Classificacao_ABC"].map(mapa_frequencia)

    return df_sorted.sort_index()


def identificar_pocs_rodovia(df: pd.DataFrame, limiar_isolamento_km: float = 6.0) -> pd.DataFrame:
    """
    Identifica POCs de 'Beira de Estrada' (Corredor Rodoviário).
    
    Critério espacial: POCs cuja distância para o vizinho mais próximo
    seja superior a limiar_isolamento_km (ex: 6 km longe de qualquer aglomeração urbana).
    """
    df_result = df.copy()
    coords = df_result[["AVG_LATITUDE", "AVG_LONGITUDE"]].to_numpy()
    
    if len(coords) < 2:
        df_result["Isolado_Rodovia"] = False
        return df_result

    # Matriz de distâncias entre todos os pontos
    dist_matrix = matriz_distancias_haversine(coords, coords)
    
    # Preencher a diagonal principal (distância do ponto a ele mesmo) com infinito
    np.fill_diagonal(dist_matrix, np.inf)
    
    # Menor distância para qualquer outro POC
    menor_dist_vizinho = np.min(dist_matrix, axis=1)
    df_result["Dist_Vizinho_Mais_Proximo_Km"] = menor_dist_vizinho
    df_result["Isolado_Rodovia"] = menor_dist_vizinho >= limiar_isolamento_km

    return df_result
