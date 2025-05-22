# 🧭 Projeto RTM — Route-to-Market

Este repositório apresenta uma análise voltada para a estratégia de **Route-to-Market (RTM)**, utilizando dados de pontos de venda (POCs) e técnicas de clusterização geográfica. O objetivo é identificar agrupamentos eficientes de atendimento e cobertura comercial a partir da distribuição espacial e características dos POCs.

---

## 📁 Notebooks do Projeto

### 🔹 `main_analise.ipynb`

Notebook de preparação inicial contendo:

* Importação de bibliotecas fundamentais
* Carregamento dos dados de POCs
* Estrutura base para análises posteriores

---

### 🔹 `RTM-1.ipynb` — **Clusters de POCs**

Foco em:

* **Clusterização geográfica de POCs**
* Otimização do número de grupos com K-Means
* Visualização interativa dos clusters
* Análise espacial para redesenho de territórios de atuação

---

### 🔹 `RTM-2.ipynb` — **Aprofundamento e Testes**

Complemento ao RTM-1 com:

* Ajustes em parâmetros de clusterização
* Testes com novos agrupamentos e filtros
* Estratégias de cobertura alternativa e análise de dispersão
* Potencial para alimentar sistemas de roteirização de campo

---

## ⚙️ Tecnologias Utilizadas

* **Python 3**
* **Pandas / NumPy**
* **Matplotlib / Seaborn / Plotly**
* **Scikit-learn** — KMeans
* **Jupyter Notebook**

> *Caso aplicável: `Geopandas`, `Folium` ou `OpenStreetMap` para visualizações geográficas podem ser necessários.*

---

## 🚀 Como Rodar o Projeto

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Instale os pacotes necessários:

   ```bash
   pip install pandas matplotlib seaborn scikit-learn plotly
   ```

3. Execute os notebooks na ordem:

   * `main_analise.ipynb`
   * `RTM-1.ipynb`
   * `RTM-2.ipynb`

> Certifique-se de que os arquivos de dados estão na pasta correta ou ajuste os caminhos no código.

---

## 📈 Resultados Esperados

* Segmentação eficiente de áreas de atuação
* Redesenho de territórios comerciais baseado em dados
* Melhoria na alocação de equipes de vendas
* Apoio na construção de roteirização inteligente
