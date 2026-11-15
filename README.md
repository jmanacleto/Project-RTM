# 🧭 Projeto RTM — Route-to-Market & Otimização de Rotas Comerciais

Este projeto apresenta uma reestruturação analítica completa da estratégia de **Route-to-Market (RTM)** e logística de atendimento comercial para a operação do **Equador (região de Ambato e entorno)**, abrangendo uma carteira de mais de **5.500 Pontos de Venda (POCs) estratégicos** que concentram mais de **US$ 55 milhões em faturamento**.

---

## 📌 O Desafio de Negócio

No modelo operacional anterior, a divisão territorial havia sido desenvolvida utilizando **K-Means clássico**, gerando severas distorções operacionais:
* **Desequilíbrio Extremo de Carga:** Um único vendedor foi alocado com **325 lojas**, enquanto **103 vendedores ficaram com menos de 5 lojas** no mês inteiro.
* **Superdimensionamento de Frota:** A operação calculava a necessidade de **418 vendedores**, gerando ociosidade massiva da equipe de campo.
* **Estimativas Irreais de Deslocamento:** As distâncias eram calculadas pela diferença linear entre linhas consecutivas do banco de dados (`.diff()`), gerando rotas em ziguezague que estimavam mais de **850 km** para atender lojas dentro da mesma cidade.

---

## 🛠️ A Solução Técnica (Pesquisa Operacional & Engenharia de Dados)

O pipeline foi completamente refatorado em um pacote Python modular (**`rtm_core`**), substituindo o agrupamento estatístico simples por métodos de **Pesquisa Operacional (Operations Research)**:

```mermaid
flowchart LR
    A["Dados Brutos (+280k)"] --> B["Higienização & Haversine"]
    B --> C["Curva ABC / Pareto Real"]
    C --> D["Clusterização com Restrição de Capacidade"]
    D --> E["Roteirização TSP (2-Opt) por Setor"]
    E --> F["Mapas Interativos & KPIs Operacionais"]
```

### 1. Engenharia de Dados Geoespaciais
* Validação de *bounding box* territorial para filtragem de coordenadas espúrias e nulas.
* Substituição de distâncias euclidianas planas pela **Fórmula de Haversine**, calculando a distância geodésica real em quilômetros sobre a curvatura da Terra.

### 2. Segmentação Comercial & Curva ABC (Pareto)
* Cálculo do Pareto sobre a **receita acumulada (Curva de Lorenz)**:
  * **Tier A (Top faturamento - 80% da receita):** Atendimento **Semanal** (4x ao mês).
  * **Tier B (Intermediário - 15% da receita):** Atendimento **Quinzenal** (2x ao mês).
  * **Tier C (Cauda longa - 5% da receita):** Atendimento **Mensal** (1x ao mês).
* Detecção algorítmica de clientes de **Corredor Rodoviário ("Beira de Estrada")** via isolamento espacial (> 6 km de distância do vizinho mais próximo).

### 3. Clusterização com Restrição de Capacidade (*Capacitated Clustering*)
* Dimensionamento da frota ideal baseado na soma real de visitas mensais necessárias.
* Algoritmo de agrupamento com teto e piso estritos de carga de trabalho, garantindo jornadas de trabalho humanas e viáveis (~7 a 8 atendimentos diários por consultor).

### 4. Roteirização Combinatória (Caixeiro-Viajante / TSP com 2-Opt)
* **Setorização Diária:** Divisão de cada território em setores geográficos contíguos (Segunda a Sexta), evitando que o consultor cruze a cidade várias vezes na mesma semana.
* **Resolução do TSP:** Heurística do Vizinho Mais Próximo com refinamento **2-Opt** para eliminar cruzamentos de rota, reduzindo a quilometragem calculada em mais de **90%**.

---

## 📊 Comparativo de Impacto (Antes vs. Depois)

| Métrica | Abordagem Anterior (K-Means Puro) | Nova Abordagem (Pesquisa Operacional) |
| :--- | :--- | :--- |
| **Tamanho da Frota** | 418 vendedores (superdimensionada) | **88 vendedores** (redução drástica de ociosidade) |
| **Maior Carteira** | 325 lojas / vendedor (sobrecarga desumana) | **81 lojas / vendedor** (plenamente viável) |
| **Menor Carteira** | 1 loja / vendedor | **9 lojas** (casos de dispersão rural extrema) |
| **Vendedores Ociosos (< 5 lojas)** | **103 vendedores** | **0 vendedores** |
| **Média de Visitas por Vendedor** | Desbalanceada e aleatória | **~149 visitas/mês** (~7 a 8 visitas diárias) |
| **Quilometragem no Território 0** | 859.1 km (saltos aleatórios no CSV) | **73.8 km** (**91.4% de redução em deslocamento inútil**) |
| **Visualização** | Pontos estáticos desconectados | **Mapas interativos Folium com circuitos traçados** |

---

## 🗺️ Visualização Cartográfica (Dark Mode)

O sistema gera mapas interativos Folium com tema escuro (*Dark Gray Canvas*), camadas por dia da semana e polilinhas traçando o circuito contínuo de atendimento:

- **Segunda-feira (Cyan Neon):** Circuito compacto no setor norte da base.
- **Terça-feira (Verde Esmeralda):** Circuito setorizado no quadrante leste.
- **Quarta a Sexta:** Rota balanceada para cada dia da semana.
- **Controle de Camadas:** Visualização individualizada de cada dia sem poluição visual.

Os mapas gerados ficam salvos no diretório `output/mapa_rotas_otimizadas_Territorio_000.html`.

---

## 📁 Estrutura do Repositório

```text
├── assets/                      # Imagens e comparativos visuais
├── dados/                       # Datasets históricos originais
├── notebooks/                   # Notebooks de análise exploratória e estudos legados
├── rtm_core/                    # Pacote Python profissional refatorado
│   ├── config.py                # Configurações globais e caminhos dinâmicos (pathlib)
│   ├── data_loader.py           # Ingestão, tipagem e higienização geoespacial
│   ├── geo_utils.py             # Funções de cálculo geodésico (Haversine vetorizado)
│   ├── segmentation.py          # Segmentação ABC / Pareto e detecção de rodovia
│   ├── clustering.py            # Clusterização balanceada com restrição de capacidade
│   ├── routing.py               # Roteirização diária via TSP (2-Opt)
│   └── visualization.py         # Geração de mapas interativos Folium (Dark Theme)
├── output/                      # Artefatos gerados, mapas HTML e dados consolidados
├── run_pipeline.py              # Script executivo para rodar o pipeline completo
└── README.md                    # Documentação do case
```

---

## 🚀 Como Executar o Projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/jmanacleto/Project-RTM.git
   cd Project-RTM
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install pandas numpy scikit-learn folium scipy plotly
   ```

3. Execute o pipeline completo:
   ```bash
   python run_pipeline.py
   ```

4. Abra os mapas interativos gerados na pasta `output/` diretamente no navegador.
