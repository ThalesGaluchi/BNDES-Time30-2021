import numpy as np
import pandas as pd
from datetime import date, datetime

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ===============================================
#   Descrição: Dashboard com Desembolsos Mensais Indiretos
#       separados por produto e ano, que apresenta o 
#       gráfico por quantidade e valor 

# =========================================
# FUNÇÕES

def carrega_arquivo(item):
    ''' Carrega arquivo conforme numeração no arquivo-índice
        projeto-bndes-dataset.csv  '''
    links = pd.read_csv('./data/sumario.csv', sep=';')
    return pd.read_csv(links['link arquivo'][item], sep=';', decimal=',') 

def siglas_de_estados():
    '''Dicionário de Siglas e Nomes de Estados do Brasil'''
    return {'SANTA CATARINA': 'SC',  'PARANA': 'PR','RIO GRANDE DO SUL': 'RS',
            'SAO PAULO': 'SP', 'MINAS GERAIS': 'MG','ESPIRITO SANTO': 'ES', 'RIO DE JANEIRO': 'RJ',
            'GOIAS': 'GO',  'TOCANTINS': 'TO',  'MATO GROSSO': 'MT','MATO GROSSO DO SUL': 'MS',
            'DISTRITO FEDERAL': 'DF',
            'AMAZONAS': 'AM','PARA': 'PA','RONDONIA': 'RO','RORAIMA': 'RR','AMAPA': 'AP','ACRE': 'AC',
            'BAHIA': 'BA','CEARA': 'CE','ALAGOAS': 'AL','RIO GRANDE DO NORTE': 'RN',
            'PERNAMBUCO': 'PE','MARANHAO': 'MA','PARAIBA': 'PB','PIAUI': 'PI','SERGIPE': 'SE',
              }

# def desembolsos_mensais( forma = 'INDIRETA'):
#     ''' Carrega e agrupa os dados de Desembolsos Mensais Indiretos
#       individualizados a partir da tabela detalhada'''

#     DMIA = carrega_arquivo(7)
#     conds=(DMIA.forma_de_apoio==forma)
#     DMIA = DMIA[conds]
#     siglas = siglas_de_estados()
#     DMIA['UFs'] = [ siglas[item.strip()] for item in DMIA.uf ]
#     cols_drop = ['instrumento_financeiro', 'inovacao' , 'regiao', 'uf' ]
#     DMIA.drop(cols_drop, axis= 1,inplace = True)
#     DMIA.rename(columns={'UFs': 'uf',  'porte_de_empresa': 'porte_do_cliente'}, inplace = True)
#     DMIA['uf'] = DMIA['uf'].str.strip()
#     DMIA['setor_cnae'] = DMIA['setor_cnae'].str.strip()
#     DMIA['setor_bndes'] = DMIA['setor_bndes'].str.strip()
#     cols = ['ano','produto']
#     valores = ['desembolsos_reais']
#     DMIA_gb = DMIA.groupby(cols)['desembolsos_reais'].agg(['count','sum']).unstack(level=1)
#     DMIA_gb.fillna(0,inplace=True)
#     DMIA_gb.rename(columns = {'count':'quantidade', 'sum':'valor'}
#                     , inplace = True)

#     return DMIA_gb


# =========================================
# DADOS

# Dicionário com produtos indiretos BNDES
produtos = {'bndes_finem':'BNDES FINEM',  
            'bndes_exim':'BNDES-EXIM',
            'bndes_automatico':'BNDES AUTOMÁTICO',
            'bndes_finame':'BNDES FINAME' ,
            'cartao_bndes': 'CARTÃO BNDES'}
num_botoes = len(produtos)
botoes_id={ 'btn-'+str(i):item for i,item in enumerate(produtos.keys()) }

inicio, fim = 1995, 2021

obs = '(1) O produto BNDES NÃO REEMBOLSÁVEL não foi utilizado no período.'
obs+= '\t\t\t(2) Não há dados de valores para o produto BNDES CARTÃO '
obs+= 'nos dados agregados (apenas quantidades agregadas). '

# =========================================
# GRÁFICOS

# numero do arquivo de desembolsos agregados por forma indireta
num = 48    # Valores
DI_forma_valor = carrega_arquivo(num).groupby('ano').sum()
cols_drop=['mes','bndes_nao_reembolsavel']
DI_forma_valor.drop(cols_drop,axis=1,inplace=True)

num = 64    # Quantidades
DI_forma_quant = carrega_arquivo(num).groupby('ano').sum()
cols_drop=['bndes_nao_reembolsavel']
DI_forma_quant.drop(cols_drop,axis=1,inplace=True)

# DMIA = desembolsos_mensais()
DMIA = pd.read_csv('./data/desembolsos-mensais/DMIA_gb.csv'
                    , sep=';', decimal='.', header=[0,1])

# dados de valor e quantidade juntos
DI_forma= pd.concat( [DI_forma_quant, DI_forma_valor], axis=1 , keys=['quantidade', 'valor'])

# Gráfico Inicial
prod_inicio = ['bndes_automatico','bndes_finame']

fig=make_subplots( )
fig2=make_subplots( rows=2, cols =1)

# =========================================
# LAYOUT
app = dash.Dash(__name__
        , external_stylesheets= [dbc.themes.CYBORG]
        , update_title='Carregando...')
server = app.server

app.config.suppress_callback_exceptions = True

app.layout = dbc.Container([
    html.Div([
    dbc.Row([
        html.H2 (['PRODUTOS INDIRETOS BNDES'], id='titulo')
        ,html.H6('A posição indica a quantidade de desembolsos realizados e o tamanho da bolha representa o valor total desembolsado (conforme dados agregados).')
    ])
    ,dbc.Row([
        dbc.Col([
            html.Div([
            html.Div(
            [html.Button(produtos[item], id='btn-'+str(i),className='no-click') 
            for i,item in enumerate(produtos.keys()) ] , id='div-buttons' 
            )
             ,html.H5( [f'DE {inicio} ATÉ {fim}'] ,  id='ano-range-container')
                   
            ,dcc.RangeSlider(
                marks={i:'{}'.format(i) for i in range(inicio, fim+1, 2)},
                min=inicio,max=fim,value=[2006, 2020]
                ,id='ano-range-slider'
                )  
            ,dcc.Graph(id="chart-main",figure=fig)                
            ], id='div-button-slider')
           
        ], md=6)
        ,dbc.Col([
            dcc.Loading( id="loading-2", type="default",
                children=[dcc.Graph(id="chart-q",figure=fig2) ])
            # ,dcc.Loading( id="loading-3", type="default",
            #     children=[dcc.Graph(id="chart-v",figure=fig3) ])
        ],md=6)
    ])
    ,dbc.Row([ html.P(obs) ],id='obs-footnote') 
    ] ,id='div-first')
])

# =========================================
# INTERATIVIDADE

# ================================================================
# Mensagem sob slider 
@app.callback(
    Output('ano-range-container', 'children'),
    Input('ano-range-slider', 'value'))
def update_slider_range(value):
    return f'DE {value[0]} ATÉ {value[1]}'

## ===================================================================
# Diversos botões que alteram liga / desliga
@app.callback(
    [Output('btn-'+str(i),'className') for i in range(0,num_botoes)]
    # ,Output('text-but', 'children') 
    ,[Input('btn-'+str(i),'n_clicks') for i in range(0,num_botoes)]
)
def clicked_button_style(*clicks ):
    ''' Altera a formatação de um botão'''
    ctx = dash.callback_context
    
    if not ctx.triggered:
        # Impede a atualização inicial antes de clicar
        # raise PreventUpdate
        return ['no-click','no-click','clicked','clicked','no-click']
    else:
        # Identifica o botão clicado
        # button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        std = ['no-click'] *num_botoes
        # button_num = int(button_id.split('-')[1])
        
        for i,click in enumerate(clicks):
            if (click is None) or (click%2 == 0):
                std[i] = 'no-click'
            else:
                std[i] = 'clicked'
        # std.append(botoes_id[ctx.triggered[0]['prop_id'].split('.')[0]])
        return std

# =========================================
# Atualiza o Gráfico

@app.callback(
    Output('chart-main','figure')
    ,Output('chart-q','figure')
    # ,Output('chart-v','figure')
    ,Input('ano-range-slider', "value")
    ,[Input('btn-'+str(i),'className') for i in range(0,num_botoes)]
)
def plot_chart_selected(slider_range,  *classes ):
    low,high = slider_range
    mask = ((DI_forma.reset_index().ano > low) 
        & (DI_forma.reset_index().ano < high))
    
    df_DI =DI_forma.reset_index()[mask]
    dados = DMIA.reset_index()[mask]   
    year = df_DI.reset_index().ano

    but_id = {'btn-'+str(i):item for i,item in enumerate(produtos.keys()) }
    ativos = [ b for b,cl in zip(but_id.values(),classes) if cl =='clicked']

    # Limpa o gráfico
    fig = make_subplots()

    #Gráfico Principal
    for p in ativos:
        if p == 'cartao_bndes':
            quant = df_DI['quantidade',p]
            fig.add_trace(go.Scatter(x=year , y=quant
                , name=produtos[p], mode='markers') )
        
        else:
            quant = df_DI['quantidade',p]
            valor = df_DI['valor',p]/1000
            fig.add_trace(go.Scatter(x=year , y=quant, name=produtos[p],
                                 mode='markers',marker=dict(size=valor)) )
    
    fig.update_xaxes(title_text='ANO')
    fig.update_yaxes(title_text='Quantidade de desembolsos')
    fig.update_layout(
        title_text='DESEMBOLSOS INDIRETOS (a partir dos dados agregados)'
            ,legend =dict(orientation='h', yanchor='bottom'
            ,y=1.02,xanchor='left',x=1 )
            , legend_x=0  , legend_y=1
    )

    fig.add_annotation(x=2004, y=210000,
            text="O tamanho da bolha <br> indica o valor total <br> desembolsado(R$)"
            ,showarrow=False
            ,yshift=10
            ,bgcolor='white'
            ,width=150
            ,height=80
            ,borderwidth=5
            )

    ##  ==============GRAFICOS LATERAIS =========
    prod_use = [ produtos[item] for item in ativos] 
    fig2 = make_subplots(rows=2, cols=1)
    colors= ['blue', 'red', 'green', 'black','orange']

    for i,p in enumerate(ativos):
        quant = dados['quantidade',produtos[p] ]
        quant_agg = df_DI['quantidade',p]

        fig2.append_trace(go.Scatter(
                    x=year , y=quant
                    , name=produtos[p] 
                    , mode='markers'
                    , marker=dict(color=colors[i], size=12))
                    ,row=1, col=1)

        fig2.append_trace(go.Scatter(
                    x=year , y=quant_agg
                   , name=produtos[p]+'(AGG)' 
                    , mode='lines'
                    , line=dict(color=colors[i]) )
                    ,row=1, col=1)
                                
        valor= dados['valor',produtos[p]]*1e-9

        if p != 'cartao_bndes':
            valor_agg=df_DI['valor',p]*1e-3
            fig2.append_trace(go.Scatter(
                x=year ,y=valor_agg
               , name=produtos[p]+'(AGG)' 
                , mode='lines'
                , line=dict(color=colors[i])
                ,showlegend=False)
                ,row=2, col=1
                )
    
        fig2.append_trace(go.Scatter(
                x=year ,y=valor
                , name=produtos[p]
                , mode='markers' 
                , marker = dict(color=colors[i], size=12)
                ,showlegend=False )
                ,row=2, col=1 )
        
    fig2.update_layout(
        title_text='DESEMBOLSOS INDIRETOS<br>comparativo dados agregados[AGG] X dados específicos'
    )  
   
    fig2.update_xaxes(title_text='ANO')
    fig2.update_yaxes(title_text='Quantidade de desembolsos'
                     ,row=1, col=1)
    fig2.update_yaxes(title_text='Valor Total Desembolsado<br>(milhoes R$)'
                     ,row=2, col=1)
    return fig, fig2 



# =========================================
# INICIAR SERVIDOR

if __name__ == '__main__':
    # app.run_server(debug=True , use_reloader=True)
    app.run_server(host='0.0.0.0', port=8080, debug=False, use_reloader=False)



