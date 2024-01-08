import pandas as pd
from bs4 import BeautifulSoup
import requests
import yfinance as yf
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
import psycopg2
from sqlalchemy import create_engine, text as sql_text

dict_acoes = {'acoes':['CEAB3', 'WEGE3', 'PETR4'], 'vars_procura' : ['C%26A', 'weg', 'petr4'], 'ticker_yf' : ['CEAB3.SA', 'WEGE3.SA', 'PETR4.SA']}

def database_conn():
    
    db_params = {
    'dbname': 'mini_projeto',
    'user': 'user',
    'password': '21GiT99CqAwiH5z0jjUOB7cGLXJUpZlv',
    'host': 'dpg-cmdkg58l5elc73ci4en0-a.oregon-postgres.render.com',
    'port': '5432'
}
    
    db_url = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

    engine = create_engine(db_url)

    return engine


# ## Web Scrapping no Brazil Journal

def capturar_noticias(acoes: dict):
    df_noticias = pd.DataFrame()
    for ticker, var_procura in zip(acoes.get('acoes'), acoes.get('vars_procura')):
            br_journal = requests.get(f"https://braziljournal.com/?s={var_procura}")
            site = BeautifulSoup(br_journal.text, 'html.parser')
            article = site.find_all('p', class_ = 'boxarticle-infos-tag', limit = 3)
            titulos = [article[idx].find('a').text for idx, item in enumerate(article)]
            link_titulos = [article[idx].find('a').get('href') for idx, item in enumerate(article)]
            materia = site.find_all('h2', class_ = "boxarticle-infos-title", limit = 3)
            titulos_materia = [materia[idx].find('a').text.strip() for idx, item in enumerate(materia)]
            link_materia = [materia[idx].find('a').get('href') for idx, item in enumerate(materia)]
            dict_intermediario = {'titulos':titulos, 'link_titulos': link_titulos, 'titulos_materia': titulos_materia, 'link_materia' : link_materia}
            df_intermediario = pd.DataFrame(data = [dict_intermediario], columns = dict_intermediario.keys())
            df_intermediario['ticker'] = ticker
            df_intermediario.set_index(df_intermediario.columns[-1], inplace=True)
            df_intermediario.reset_index(inplace=True)
            df_noticias = pd.concat([df_noticias, df_intermediario], axis = 0, ignore_index= True)
    
    return df_noticias


df_noticias = capturar_noticias(dict_acoes)

# Conexão com o Database no Render

engine = database_conn()


# ## Cotações no Yahoo Finance

def capturar_cotacoes(acoes:dict):
    for acao_ticker ,ticker in zip(acoes.get('acoes'), acoes.get('ticker_yf')):
        ticker_ = yf.Ticker(ticker)
        last_max_ = ticker_.history(period = 'max')
        last_max_.reset_index(inplace = True)
        last_max_['ticker'] = acao_ticker
        last_max_.to_sql(f'yf_history_{ticker}', engine.connect(),if_exists= 'replace', schema= 'cotacao')
        #last_max_.to_csv(f'.\\historico\\yf_history_{ticker}.csv', index = False)

capturar_cotacoes(dict_acoes)

query_ceab = 'SELECT * FROM cotacao."yf_history_CEAB3.SA"'
query_wege = 'SELECT * FROM cotacao."yf_history_WEGE3.SA"'
query_petr4 = 'SELECT * FROM cotacao."yf_history_PETR4.SA"'


df_ceab = pd.read_sql_query(con=engine.connect(), sql=sql_text(query_ceab))
df_wege = pd.read_sql_query(con=engine.connect(), sql=sql_text(query_wege))
df_petr4 = pd.read_sql_query(con=engine.connect(), sql=sql_text(query_petr4))

engine.dispose()


df_ceab['Date'] = pd.to_datetime(df_ceab['Date'], utc = True).map(lambda x: x.tz_convert('America/Sao_Paulo'))
df_wege['Date'] = pd.to_datetime(df_wege['Date'], utc = True).map(lambda x: x.tz_convert('America/Sao_Paulo'))
df_petr4['Date'] = pd.to_datetime(df_petr4['Date'], utc =  True).map(lambda x: x.tz_convert('America/Sao_Paulo'))

list_dfs = [df_ceab,df_wege,df_petr4]



# ### Dashboard em Dash

app = Dash(__name__,title= 'Mini Projeto',update_title= 'Carregando...')

server = app.server

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children= 
    [html.Div([
         html.Div([
              html.Div(children = '', className ='col_vazia'),
             html.Div([dcc.Dropdown(df_noticias.ticker.unique(), 'PETR4', id='dropdown-selection')], className= 'div_dropdown'),
            html.Div(children = '', className ='col_vazia')], className = 'div_dropdown_container'),
        html.Div([
            html.Div([ dcc.Graph(id='graph-content')], style = {'height': '100%', 'width': '100%'}, className= 'div_grafico')])
], className= 'div_primeira_col'),
html.Div([
   html.H1("Notícias"),
   html.Div([
       html.P(id = 'titulo1'),
       html.Div([
            html.A(children= [html.H3(id = 'texto1')],id = 'link_texto1'),
       ])  
], className= 'bloco1'),
   html.Div([
       html.P(id = 'titulo2'),
         html.Div([
           html.A(children= [html.H3(id = 'texto2')],id = 'link_texto2'),
       ])
], className= 'bloco2'),
   html.Div([
       html.P(id = 'titulo3'),
      html.Div([
            html.A(children= [html.H3(id = 'texto3')],id = 'link_texto3'),          
       ], className= 'bloco3')
    ])], className= 'div_noticias')
], className= 'div_principal')


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)

def update_graph(value):
    graph_df = None
    for df in list_dfs:
        if (df['ticker'].tolist()[0]) == value  :
            min_date = max(df[df.ticker == value]['Date']) - pd.DateOffset(years=1)
            graph_df = df[(df.ticker == value ) & (df.Date >= min_date)]

    if graph_df is not None:
        fig = go.Figure(data=[go.Candlestick(x=graph_df['Date'],
                                             open=graph_df['Open'],
                                             high=graph_df['High'],
                                             low=graph_df['Low'],
                                            close=graph_df['Close'])])
        fig.update_layout(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor='rgb(19, 21, 22)',  # Define a cor de fundo em RGB
    xaxis=dict(showgrid=False,
               showline=False,
               zeroline=False,
               rangeslider=dict(visible=False),
               autorange=True,
               tickfont=dict(color='white')),  # Remove a grade no eixo x
    yaxis=dict(showgrid=False,
               zeroline=False,
                tickfont=dict(color='white')),   # Remove a grade no eixo y
    margin=dict(l=0, r=0, t=0, b=0)
    )
         
        return fig
    else:
        fig = go.Figure()

        fig.update_layout(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor='rgb(19, 21, 22)',  # Define a cor de fundo em RGB
    xaxis=dict(showgrid=False,
               showline=False,
               zeroline=False,
               rangeslider=dict(visible=False),
               autorange=True,
               tickfont=dict(color='white')),  # Remove a grade no eixo x
    yaxis=dict(showgrid=False,
               zeroline=False,
                tickfont=dict(color='white')),   # Remove a grade no eixo y
    margin=dict(l=0, r=0, t=0, b=0))

        return fig

@callback(
    Output('titulo1', 'children'),
    Output('link_texto1', 'href'),
    Output('texto1', 'children'),
    Output('titulo2', 'children'),
    Output('link_texto2', 'href'),
    Output('texto2', 'children'),
    Output('titulo3', 'children'),
    Output('link_texto3', 'href'),
    Output('texto3', 'children'),
    Input('dropdown-selection', 'value')
)

def update_news(value):
    for i in range(0, df_noticias.shape[0]):
        if (df_noticias['ticker'].tolist()[i]) == value  :
            news_df = df_noticias[df_noticias.ticker == value]

            return news_df['titulos'][i][0],news_df['link_materia'][i][0],news_df['titulos_materia'][i][0],news_df['titulos'][i][1],news_df['link_materia'][i][1],news_df['titulos_materia'][i][1],news_df['titulos'][i][2],news_df['link_materia'][i][2],news_df['titulos_materia'][i][2]

        if value is None: 
            return 'Selecione um Ticker', 'Selecione um Ticker', 'Selecione um Ticker', 'Selecione um Ticker', 'Selecione um Ticker', 'Selecione um Ticker', 'Selecione um Ticker','Selecione um Ticker', 'Selecione um Ticker'
if __name__ == '__main__':
    app.run_server(debug=True)
