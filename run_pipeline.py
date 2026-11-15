"""
Pipeline Principal de Otimização Route-to-Market (RTM).

Orquestra todas as etapas do processo:
1. Ingestão e Auditoria de Dados
2. Segmentação ABC (Pareto Real) e Filtros Espaciais
3. Dimensionamento da Frota e Clusterização Balanceada
4. Roteirização Diária via Caixeiro-Viajante (TSP 2-Opt)
5. Geração de Mapa Interativo com Rotas Conectadas
6. Emissão de Relatório Comparativo Executivo
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path

from rtm_core.config import DATA_DIR, OUTPUT_DIR
from rtm_core.data_loader import carregar_dados_brutos, higienizar_dados_rtm
from rtm_core.segmentation import aplicar_curva_abc_pareto, identificar_pocs_rodovia
from rtm_core.clustering import dimensionar_frota_ideal, clusterizacao_balanceada
from rtm_core.routing import agendar_rotas_semanais, resolver_tsp_vizinho_mais_proximo
from rtm_core.visualization import gerar_mapa_rotas_territorio


def executar_pipeline_completo():
    print("=" * 70)
    print("🚀 INICIANDO NOVO PIPELINE DE OTIMIZAÇÃO ROUTE-TO-MARKET (RTM)")
    print("=" * 70)
    
    # --- ETAPA 1: CARGA E SEGMENTAÇÃO ---
    print("\n[Etapa 1/5] Carregando e segmentando os dados prioritários (Top POCs)...")
    caminho_df = DATA_DIR / "df.csv"
    if not caminho_df.exists():
        print(f"Arquivo {caminho_df} não encontrado. Usando dados brutos...")
        df_raw = carregar_dados_brutos()
        df, _ = higienizar_dados_rtm(df_raw)
    else:
        df = pd.read_csv(caminho_df)
    
    df_seg = aplicar_curva_abc_pareto(df)
    df_seg = identificar_pocs_rodovia(df_seg, limiar_isolamento_km=6.0)
    
    total_pocs = len(df_seg)
    faturamento_total = df_seg["Faturamento_Mensal_USD"].sum()
    total_visitas = df_seg["Frequencia_Mensal"].sum()
    
    print(f"  ✓ POCs Analisados: {total_pocs:,}")
    print(f"  ✓ Faturamento Mensal Total: ${faturamento_total:,.2f}")
    print(f"  ✓ Total de Visitas Mensais Necessárias: {total_visitas:,}")
    print(f"  ✓ Clientes de Corredor Rodoviário Isolados: {df_seg['Isolado_Rodovia'].sum()}")

    # --- ETAPA 2: DIMENSIONAMENTO E CLUSTERIZAÇÃO BALANCEADA ---
    print("\n[Etapa 2/5] Dimensionando frota e gerando clusters com restrição de capacidade...")
    frota_ideal = dimensionar_frota_ideal(df_seg, visitas_max_mensais_vendedor=150)
    print(f"  ✓ Frota Dimensionada: {frota_ideal} vendedores (antigo: 418)")
    
    df_clustered, resumo_territorios = clusterizacao_balanceada(
        df_seg,
        num_territorios=frota_ideal,
        teto_visitas_mensais=165
    )
    print(f"  ✓ Média de Visitas por Vendedor: {resumo_territorios['Total_Visitas_Mensais'].mean():.1f}")
    print(f"  ✓ Menor Carteira: {resumo_territorios['Total_POCs'].min()} POCs | Maior Carteira: {resumo_territorios['Total_POCs'].max()} POCs")

    # --- ETAPA 3: ROTEIRIZAÇÃO E TSP 2-OPT ---
    print("\n[Etapa 3/5] Resolvendo Caixeiro-Viajante (TSP) e agendando rotas por dia...")
    territorio_alvo_id = "Territorio_000"
    df_territorio = df_clustered[df_clustered["Territorio_ID"] == territorio_alvo_id].copy()
    
    df_agendado = agendar_rotas_semanais(df_territorio)
    
    coords = df_territorio[["AVG_LATITUDE", "AVG_LONGITUDE"]].to_numpy()
    _, km_tsp = resolver_tsp_vizinho_mais_proximo(coords)
    
    # Cálculo antigo para benchmark
    deltas_lat = np.abs(np.diff(coords[:, 0]))
    deltas_lon = np.abs(np.diff(coords[:, 1]))
    km_antigo = np.sum(deltas_lat * 111 + deltas_lon * 111 * np.cos(np.radians(coords[:-1, 0])))
    
    print(f"  ✓ Território Modelo: {territorio_alvo_id} ({len(df_territorio)} lojas)")
    print(f"  ✓ Km Calculados Método Antigo (.diff): {km_antigo:.1f} km")
    print(f"  ✓ Km Reais Otimizados com TSP 2-Opt:   {km_tsp:.1f} km")
    print(f"  ✓ Redução de Deslocamento Inútil:      {((km_antigo - km_tsp)/km_antigo)*100:.1f}%")

    # --- ETAPA 4: GERAÇÃO DO MAPA INTERATIVO ---
    print("\n[Etapa 4/5] Desenhando mapa interativo com polilinhas e camadas semanais...")
    caminho_mapa = gerar_mapa_rotas_territorio(df_agendado, territorio_id=territorio_alvo_id)
    print(f"  ✓ Mapa gerado com sucesso em: {caminho_mapa}")

    # --- ETAPA 5: SALVANDO ARTEFATOS CONSOLIDADOS ---
    print("\n[Etapa 5/5] Exportando datasets consolidados...")
    caminho_dados_otimizados = OUTPUT_DIR / "dados_rtm_otimizados.csv"
    df_clustered.to_csv(caminho_dados_otimizados, index=False)
    
    caminho_resumo = OUTPUT_DIR / "resumo_executivo_territorios.csv"
    resumo_territorios.to_csv(caminho_resumo, index=False)
    print(f"  ✓ Dados otimizados salvos em: {caminho_dados_otimizados}")
    
    print("\n" + "=" * 70)
    print("🏆 PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    
    return caminho_mapa


if __name__ == "__main__":
    executar_pipeline_completo()
