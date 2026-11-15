"""
Módulo de Visualização Cartográfica e Mapas Interativos (Dark Theme Edition).

Gera mapas Folium interativos com estética Dark Mode, cores neon de alto contraste,
efeito glassmorphism e controle estilizado para apresentações executivas e portfólio.
"""
import folium
import pandas as pd
import numpy as np
from pathlib import Path
from rtm_core.config import OUTPUT_DIR


# Paleta Neon de Alto Contraste para Fundo Escuro (Cyberpunk / Modern Data Viz)
CORES_DIAS_DARK = {
    "seg": "#00f2fe",  # Cyan Neon Elétrico
    "ter": "#00e676",  # Emerald / Verde Neon
    "qua": "#ffb300",  # Amber / Ouro Vibrante
    "qui": "#c084fc",  # Roxo / Lilás Neon
    "sex": "#ff3366",  # Rosa / Coral Neon
}


def gerar_mapa_rotas_territorio(
    df_territorio_agendado: pd.DataFrame,
    territorio_id: str = "Territorio_000",
    output_dir: Path = OUTPUT_DIR
) -> Path:
    """
    Cria um mapa Folium interativo com tema escuro (Dark Gray Canvas).
    
    Características visuais:
    - Base de mapa: Esri Dark Gray Canvas (elegante, limpo e sem marcas d'água).
    - Paleta: Cores neon vibrantes sobre o asfalto escuro.
    - Glassmorphism: Card executivo com estatísticas do território.
    - Custom CSS: Popups e controle de camadas com estilo Dark UI.
    """
    df = df_territorio_agendado.copy()
    
    centro_lat = float(df["AVG_LATITUDE"].mean())
    centro_lon = float(df["AVG_LONGITUDE"].mean())
    total_lojas = len(df)
    
    # 1. Mapa Base Esri Dark Gray (Base limpa sem poluição visual)
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=13,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Dark Gray Canvas",
        control_scale=True
    )
    
    # Adicionar camada sutil de referências (nomes de cidades/ruas em cinza claro)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Labels",
        overlay=True,
        name="Rótulos de Vias"
    ).add_to(mapa)
    
    # 2. Marcador da Base Operacional (Ponto de Partida com Ícone Dourado Neon)
    folium.Marker(
        location=[centro_lat, centro_lon],
        popup=f"<b>BASE OPERACIONAL:</b> {territorio_id}",
        tooltip="Ponto de Partida / Centróide do Vendedor",
        icon=folium.Icon(color="black", icon_color="#ffb300", icon="star", prefix="fa")
    ).add_to(mapa)
    
    # Adicionar círculo de brilho ao redor da base
    folium.CircleMarker(
        location=[centro_lat, centro_lon],
        radius=14,
        color="#ffb300",
        weight=2,
        fill=True,
        fill_color="#ffb300",
        fill_opacity=0.25,
        tooltip="Raio Central da Base"
    ).add_to(mapa)

    dias = ["seg", "ter", "qua", "qui", "sex"]
    
    # 3. Traçado das Rotas Semanais com Cores Neon
    for i, dia in enumerate(dias):
        df_dia = df[df["Dia_Semana"] == dia].sort_values(by="Ordem_Visita_Dia").reset_index(drop=True)
        if df_dia.empty:
            continue
            
        cor_neon = CORES_DIAS_DARK.get(dia, "#00f2fe")
        nome_camada = f"Rota {dia.upper()} ({len(df_dia)} lojas)"
        
        # Apenas Segunda-feira ativa por padrão para manter a tela limpa
        mostrar_inicialmente = (i == 0)
        camada_dia = folium.FeatureGroup(name=nome_camada, show=mostrar_inicialmente)
        
        coords_rota = []
        # Saída da Base
        coords_rota.append([centro_lat, centro_lon])
        
        for _, row in df_dia.iterrows():
            lat, lon = row["AVG_LATITUDE"], row["AVG_LONGITUDE"]
            coords_rota.append([lat, lon])
            
            parada_num = row["Ordem_Visita_Dia"]
            faturamento = row.get("Faturamento_Mensal_USD", 0.0)
            classe = row.get("Classificacao_ABC", "N/A")
            freq = row.get("Frequencia_Mensal", 1)
            
            popup_html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; min-width: 200px;">
                <div style="background: {cor_neon}; color: #000; padding: 6px 10px; border-radius: 6px 6px 0 0; font-weight: 700;">
                    PARADA {parada_num} &bull; {dia.upper()}
                </div>
                <div style="padding: 10px; background: #0f172a; color: #f8fafc; border: 1px solid rgba(255,255,255,0.1); border-top: none; border-radius: 0 0 6px 6px;">
                    <div style="margin-bottom: 4px;"><b>Loja / POC:</b> <span style="color: #94a3b8;">{row['POC']}</span></div>
                    <div style="margin-bottom: 4px;"><b>Faturamento:</b> <span style="color: {cor_neon}; font-weight: 700;">${faturamento:,.2f}</span></div>
                    <div style="margin-bottom: 4px;"><b>Curva ABC:</b> <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">{classe}</span></div>
                    <div><b>Frequência:</b> {freq}x ao mês</div>
                </div>
            </div>
            """
            
            # Marcador em formato de Ponto Neon com borda luminosa
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color="#ffffff",
                weight=1.5,
                fill=True,
                fill_color=cor_neon,
                fill_opacity=1.0,
                tooltip=f"Parada {parada_num}: POC {row['POC']}",
                popup=folium.Popup(popup_html, max_width=320)
            ).add_to(camada_dia)
            
        # Retorno à Base
        coords_rota.append([centro_lat, centro_lon])
        
        # Traçado contínuo da rota com espessura moderna
        folium.PolyLine(
            locations=coords_rota,
            color=cor_neon,
            weight=4,
            opacity=0.9,
            tooltip=f"Circuito Otimizado: {dia.upper()}"
        ).add_to(camada_dia)
        
        camada_dia.add_to(mapa)

    # 4. Painel de Controle de Camadas
    folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

    # 5. Injeção de Card Executivo Glassmorphism & Estilos Dark Mode
    custom_ui_html = f"""
    <div style="
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        background: rgba(15, 23, 42, 0.88);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 16px 20px;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        min-width: 250px;
        pointer-events: auto;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="display: inline-block; width: 10px; height: 10px; background: #00e676; border-radius: 50%; box-shadow: 0 0 10px #00e676;"></span>
            <div style="font-size: 13px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase; color: #f8fafc;">RTM ROUTE OPTIMIZER</div>
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">{territorio_id} &bull; Ambato, Equador</div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
            <div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase; font-weight: 600;">Lojas Atendidas</div>
                <div style="font-size: 18px; font-weight: 800; color: #38bdf8;">{total_lojas}</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase; font-weight: 600;">Circuito Médio</div>
                <div style="font-size: 18px; font-weight: 800; color: #4ade80;">~10 km/dia</div>
            </div>
        </div>
        <div style="font-size: 11px; color: #64748b; line-height: 1.4;">
            Algoritmo: TSP (2-Opt) + Capacitated Clustering<br>
            <span style="color: #00f2fe;">&#9679;</span> Segunda &bull; 
            <span style="color: #00e676;">&#9679;</span> Terça &bull; 
            <span style="color: #ffb300;">&#9679;</span> Quarta &bull; 
            <span style="color: #c084fc;">&#9679;</span> Quinta &bull; 
            <span style="color: #ff3366;">&#9679;</span> Sexta
        </div>
    </div>

    <style>
        /* Estilização Dark Glassmorphism do Painel de Camadas Folium */
        .leaflet-control-layers {{
            background: rgba(15, 23, 42, 0.90) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            padding: 12px 16px !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6) !important;
        }}
        .leaflet-control-layers-base label,
        .leaflet-control-layers-overlays label {{
            color: #f8fafc !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            margin-bottom: 6px !important;
            cursor: pointer !important;
        }}
        .leaflet-control-layers input[type="checkbox"], 
        .leaflet-control-layers input[type="radio"] {{
            accent-color: #00f2fe !important;
            cursor: pointer !important;
        }}
        .leaflet-popup-content-wrapper {{
            background: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
            padding: 0 !important;
            overflow: hidden !important;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.7) !important;
        }}
        .leaflet-popup-content {{
            margin: 0 !important;
            line-height: 1.4 !important;
        }}
        .leaflet-popup-tip {{
            background: #0f172a !important;
        }}
    </style>
    """
    mapa.get_root().html.add_child(folium.Element(custom_ui_html))

    nome_arquivo = f"mapa_rotas_otimizadas_{territorio_id}.html"
    caminho_saida = output_dir / nome_arquivo
    mapa.save(str(caminho_saida))
    
    return caminho_saida
