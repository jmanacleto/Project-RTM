"""
Configurações Centrais do Projeto RTM (Route-to-Market).

Este módulo centraliza caminhos de diretórios dinâmicos e parâmetros
operacionais do negócio, evitando 'hardcoded values' espalhados pelo código.
"""
from pathlib import Path

# --- 1. CAMINHOS DE DIRETÓRIOS DINÂMICOS ---
# Raiz do projeto (onde está o repositório)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Diretórios de dados e saídas
DATA_DIR = ROOT_DIR / "dados"
OUTPUT_DIR = ROOT_DIR / "output"

# Cria a pasta de saída se não existir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Arquivo de dados mestre
RAW_DATA_PATH = DATA_DIR / "Dados_RTM.csv"

# --- 2. PARÂMETROS OPERACIONAIS DE NEGÓCIO (RTM) ---
COUNTRY_CODE = "EC"  # Foco de análise: Equador

# Bounding Box geográfico realista do Equador continental
# Evita pontos espúrios com lat/lon fora do território nacional
GEO_BOUNDS = {
    "min_lat": -5.0,
    "max_lat": 1.5,
    "min_lon": -81.5,
    "max_lon": -75.0,
}

# Parâmetros de Jornada do Vendedor
JORNADA_DIARIA_MINUTOS = 480       # 8 horas por dia
TEMPO_MEDIO_ATENDIMENTO_MIN = 15   # Tempo em cada POC (loja)
VELOCIDADE_MEDIA_KMH = 35          # Velocidade média em trânsito urbano/misto
MAX_VISITAS_DIA = 18               # Teto físico de visitas diárias sustentáveis
DIAS_UTEIS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sab"]
