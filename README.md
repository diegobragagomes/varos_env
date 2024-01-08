# Mini Projeto - Varos
Projeto de cotação e notícias financeiras baseada na escolha do Ticker 

## Objetivo

O objetivo do projeto era criar um Dashboard simples, dividido em duas colunas. 

A primeira coluna teria dois itens:
- Dropdown com os Tickers
- Gráfico de Candlestick desse Ticker selecionado

A segunda coluna, por sua vez, teria um item dividido em 3 partes. Essa coluna retorna notícias do Brazil Journal (As 3 primeiras) junto com o tema e o hiperlink para a determinada página.

## Execução

Realizou-se um Web Scraping utilizando <b>Beautiful Soup</b> e <b>Requests</b> para retirar os dados referentes aos títulos, matéria e link da matéria. Esses dados foram armazenados em um Dataframe do <b>Pandas</b>.

Na segunda parte, utilizou-se a biblioteca do <b>Yahoo Finance (yfinance)</b> para puxar os dados históricos dos Tickers. Após isso, esses dados foram guardados em um .csv para cada Ticker na pasta <b>historico</b>.

Para a última etapa, criou-se um Dashboard como solicitado inicialmente utilizando as bibliotecas Plotly e Dash, com apoio de um arquivo CSS encontrado na pasta chamada assets.


## Pontos de Melhoria

Para uma implemntação mais robusta e voltado para a produção, seria interessante o uso de um banco de dados como o RDS ou na própria GCP. Além de também colocar os dados das notícias no banco de dados transacional ou em um NOSQL. 

Além disso, há pontos de melhoria no arquivo CSS.

## Conclusão

O projeto é capaz de extrair dados de texto de um site, de cotações, a partir de uma biblioteca que lida com uma API, e unificar os dois em um Dashboard. Os Tickers poderiam ser aumentados em quantidade no código para abarcar outras ações a se observar, sem muitas mudanças adicionais.
