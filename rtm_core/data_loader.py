"""
Módulo de Ingestão e Higienização de Dados (Data Loader).

Responsável por:
1. Carregamento dos dados brutos (Dados_RTM.csv).
2. Validação e padronização de nomes de colunas.
3. Filtragem por país (padrão: Equador / EC).
4. Higienização geoespacial (coordenadas válidas e dentro do território).
5. Tipagem e saneamento de valores de faturamento e compras.
6. Emissão de métricas de qualidade de dados (Data Quality Audit).
"""
import pandas as pd
import numpy as np
from rtm_core.config import RAW_DATA_PATH, COUNTRY_CODE, GEO_BOUNDS


def carregar_dados_brutos(caminho_csv=RAW_DATA_PATH) -> pd.DataFrame:
    """Carrega o arquivo CSV mestre com tratamento de codificação."""
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado em: {caminho_csv}")
    
    df = pd.read_csv(caminho_csv, encoding="utf-8", low_memory=False)
    # Padronizar nomes de colunas: sem espaços extras e com underline
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    return df


def higienizar_dados_rtm(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Executa o pipeline de saneamento e gera métricas de auditoria de dados.
    
    Retorna:
        df_clean: DataFrame limpo e tipado.
        metrics: Dicionário com métricas do processo de higienização.
    """
    total_linhas_inicial = len(df_raw)
    
    # 1. Filtro de País
    df_pais = df_raw[df_raw["COUNTRY_NAME"] == COUNTRY_CODE].copy()
    linhas_pais = len(df_pais)
    
    # 2. Tipagem Numérica Rigorosa
    df_pais["AVG_LATITUDE"] = pd.to_numeric(df_pais["AVG_LATITUDE"], errors="coerce")
    df_pais["AVG_LONGITUDE"] = pd.to_numeric(df_pais["AVG_LONGITUDE"], errors="coerce")
    df_pais["Faturamento_Mensal_USD"] = pd.to_numeric(df_pais["Faturamento_Mensal_USD"], errors="coerce").fillna(0.0)
    df_pais["Número_de_Compras"] = pd.to_numeric(df_pais["Número_de_Compras"], errors="coerce").fillna(0).astype(int)
    
    # 3. Higienização de Coordenadas (Remover nulos, zeros e bounding box fora do país)
    # No passado, filtrava-se apenas != 0. Aqui validamos os limites geográficos reais.
    sem_coordenadas = df_pais["AVG_LATITUDE"].isna() | df_pais["AVG_LONGITUDE"].isna()
    coordenadas_zero = (df_pais["AVG_LATITUDE"] == 0) & (df_pais["AVG_LONGITUDE"] == 0)
    
    fora_da_fronteira = (
        (df_pais["AVG_LATITUDE"] < GEO_BOUNDS["min_lat"]) |
        (df_pais["AVG_LATITUDE"] > GEO_BOUNDS["max_lat"]) |
        (df_pais["AVG_LONGITUDE"] < GEO_BOUNDS["min_lon"]) |
        (df_pais["AVG_LONGITUDE"] > GEO_BOUNDS["max_lon"])
    )
    
    linhas_invalidas_geo = sem_coordenadas | coordenadas_zero | fora_da_fronteira
    df_clean = df_pais[~linhas_invalidas_geo].copy()
    
    # 4. Remover duplicatas exatas de visitas repetidas se houver
    df_clean = df_clean.drop_duplicates(subset=["POC", "Vendedor", "Dia_da_Visita"]).reset_index(drop=True)
    
    metrics = {
        "total_linhas_inicial": total_linhas_inicial,
        "linhas_pais_selecionado": linhas_pais,
        "registros_outros_paises": total_linhas_inicial - linhas_pais,
        "linhas_invalidas_gps": int(linhas_invalidas_geo.sum()),
        "linhas_finais_validas": len(df_clean),
        "pocs_unicos": df_clean["POC"].nunique(),
        "vendedores_unicos": df_clean["Vendedor"].nunique(),
        "faturamento_total_usd": float(df_clean["Faturamento_Mensal_USD"].sum()),
    }
    
    return df_clean, metrics
