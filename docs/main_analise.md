# Documentação extraída de main_analise.ipynb

## Célula 1

## **Bibliotecas**

## Célula 3

## **Carregamento de dados**

## Célula 7

| Numero de vendedores df_ec

## Célula 9

## **Filtragem / Limpeza**

## Célula 10

Remover geolocalizações nulas

## Célula 12

Adicionando coluna de faturamento formatada

## Célula 17

## **Visualização geral**

## Célula 19

## **Limpeza e adição de dados**

## Célula 20

**Frequência de Visitas Mensais**
| Código | Valor Equivalente | Frequência de Visita |
|--------|------------------|----------------------|
| 1      | 0.25            | 1 vez no mês        |
| 2      | 0.5             | 2 vezes no mês      |
| 4      | 1               | Todas as semanas do mês |


## Célula 21

### Diretrizes para Duplicação de Registros  

- **Se a análise for baseada em cada visita individualmente** →  **Sim, duplique os registros.**  
- **Se o foco for análises agregadas** (exemplo: faturamento por cliente) →  **Evite duplicar, crie uma coluna de ponderação.**  

## Célula 23

criando colunas para distribuição semanal

## Célula 29

**Adicionando dias da semana ao dataset**

## Célula 31

**Adicionando "_" a todas os titulos de coluna**

## Célula 33

## **Filtragem por faturamento**

## Célula 35

- **Percentil 90:** POCs que faturam **mais de $1,134.70** mensais estão no **top 10% de faturamento**.
- **Percentil 95:** POCs que faturam **mais de $1,951.00** mensais estão no **top 5% de faturamento**.
- **Faturamento Total:** **$84,666,950** é o faturamento total de todas as POCs analisadas.
- **Número de POCs no Pareto 80/20:** **15,243 POCs** representam **80% do faturamento total**.
- **Número de POCs acima do Percentil 90:** **11,011 POCs** faturam **mais do que 90% das outras**.

## Célula 43

- **Top faturamentos - Mapa**

## Célula 45

- **Contagem de visitas**

## Célula 47

| Numero de Vendedores no dataset original

## Célula 49

| Numero de Vendedores no dataset filtrado por faturamento

## Célula 59

## **Ajuste - Localização, Visitas &  Faturamento**

## Célula 60

- CTRL + K + C = Comentar
- CTRL + K + U = Descomentar

## Célula 62

## **Visualização de faturamento**

## Célula 71

************************************************************************************************************************************************************************************************************************************************************************

## Célula 72

************************************************************************************************************************************************************************************************************************************************************************

## Célula 73

************************************************************************************************************************************************************************************************************************************************************************

