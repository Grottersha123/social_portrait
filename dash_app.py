import warnings

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Output, State, Input
from icecream import ic

from app.common.classificator_sentiment_analysis import multiply_array
from app.vk_coomon.vk_scrap import VK_TOKEN, ScrapVk

displayModeBar = True

warnings.filterwarnings('ignore')

def create_plot(result):
    plots = []
    # Use textposition='auto' for direct text
    traces = [go.Bar(
        x=list(result.keys()), y=list(result.values()),
        text=['{} %'.format(i) for i in result.values()],
        textposition='auto',
        marker_color=['#86D898','#E9AD74','#E98074','#3E989C','#4F6AAD']
    )]
    fig = {
        # set data equal to traces
        'data': traces,
        # use string formatting to include all symbols in the chart title
        'layout': go.Layout(title='Тональность текста',
                            autosize=True,
                            yaxis={'autorange': True},
                            xaxis={'title': 'Метки'})
    }
    plots.append(fig)

    return fig


def create_plot_binary(result):
    plots = []
    # Use textposition='auto' for direct text
    traces = [go.Bar(
        x=list(result.keys()), y=list(result.values()),
        text=['{}'.format(i) for i in result.values()],
        textposition='auto',
        marker_color=['#E98074', '#86D898']
    )]
    fig = {
        # set data equal to traces
        'data': traces,
        # use string formatting to include all symbols in the chart title
        'layout': go.Layout(title='Позитивные и негативные сообщения',
                            autosize=True,
                            yaxis={'autorange': True},
                            xaxis={'title': 'Метки'})
    }
    plots.append(fig)

    return fig


def create_table(result):
    pass


style_block = {'background': '#F7F7F7',
               'box-shadow': '5px 8px 15px rgba(0, 0, 0, 0.25)',
               'padding': '10px 10px 10px 10px',
               'border-radius': '20px'}


app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'
], external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'])

app.layout = html.Div([html.Div([
    html.H2('Social portrait App',
            style={'float': 'center',
                   }),
], className='row')] +
                      [html.Div([
                          dcc.Tabs([

                              dcc.Tab(label='Вконтакте', children=
                              [
                                  html.Div(
                                      [html.Div([
                                          html.Div([html.H5("Идентификатор пользователя и количество постов"),
                                                    dcc.Input(id='input-on-submit', type='text',
                                                              placeholder="введите id пользователя"),
                                                    dcc.Input(id="input-on-submit-2", type="number", value=1000,
                                                              max=5000,
                                                              placeholder="введите количество постов",
                                                              style={'width': '60%'})]),
                                          html.Button('Submit', id='submit-val',
                                                      className="btn waves-effect waves-light"),
                                      ], className='input-field col s6')] +

                                      [html.Div([
                                          html.Div([
                                              html.Div([html.H5("Поиск в ")], className='col s4'),
                                              html.Div([dcc.Dropdown(
                                                  id='search-dropdown',
                                                  options=[
                                                      {'label': 'Вконтакте', 'value': 'VK'},
                                                      {'label': 'Google', 'value': 'Google'},
                                                  ],
                                                  value='VK',
                                                  clearable=False,
                                              )], className='col s8'),
                                              dcc.Input(id='input-on-submit-redirect', type='text',
                                                        placeholder="введите Имя и Фамилию для поиска")
                                          ]),
                                          dcc.Link(

                                              html.Button('Submit', id='submit-val-redirect',
                                                          className="btn waves-effect waves-light"), id='url-link',
                                              href='https://vk.com/search', target="_blank"),
                                      ], className='input-field col s4 push-s2')],
                                      className='row', style=style_block)] +
                                  [html.Div(
                                      [dcc.Loading(
                                          id="loading-2",
                                          children=[html.H5([html.H5(id="loading-output-2")])],
                                          type="circle",

                                      )], className='row')] + [html.Div([
                                      html.H5('ID пользователя в ВК: ', className='col s3'),
                                      html.H5(id='user_id', style={
                                          'color': 'green',
                                      }, className='col s3')], className='row')] + [html.Div([
                                      html.H5('Акт ивный ли пользователь?: ', className='col s3'),
                                      html.H5(id='active', style={
                                          'color': 'green',
                                      }, className='col s3')], className='row')] + [html.Div([
                                      html.H5('Количество лайков у всех постов: ', className='col s3'),
                                      html.H5(id='likes', style={
                                          'color': 'green',
                                      }, className='col s3')], className='row')] + [html.Div([
                                      html.H5('Количество проанализированных постов: ', className='col s3'),
                                      html.H5(id='count_post', style={
                                          'color': 'green',
                                      }, className='col s3')], className='row')] +
                                  [html.Div(
                                      [
                                          html.Div(
                                              [dcc.Graph(
                                                  id='sentiment',

                                                  config=dict(
                                                      displayModeBar=displayModeBar
                                                  ),
                                                  figure={
                                                      'data': [
                                                          {'x': [0, 0], 'y': [0, 0]}
                                                      ]
                                                  }), ], className='col s12 m12 l13')
                                      ], className='row')] + [html.Div(
                                      [
                                          html.Div(
                                              [dcc.Graph(
                                                  id='sentiment_binary',

                                                  config=dict(
                                                      displayModeBar=displayModeBar
                                                  ),
                                                  figure={
                                                      'data': [
                                                          {'x': [0, 0], 'y': [0, 0]}
                                                      ]
                                                  }), ], className='col s6')
                                      ] + [
                                          html.Div(
                                              dash_table.DataTable(
                                                  id='table',
                                                  data=[],
                                                  columns=[{'id': c[0], 'name': c[1]} for c in
                                                           [('date', 'Дата'), ('post', 'Пост'),
                                                            ('sentiment', 'Эмоция')]],
                                                  # we have less data in this example, so setting to 20

                                                  style_cell={
                                                      'height': 'auto',
                                                      # all three widths are needed
                                                      'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                                      'whiteSpace': 'normal',
                                                      'textAlign': 'center'
                                                  },
                                                  sort_action='native',
                                                  filter_action='native',
                                                  page_action='none',
                                                  style_table={'width': '600px', 'overflowY': 'auto'},
                                                  editable=False,
                                                  fixed_rows={'headers': True},
                                                  style_data_conditional=[
                                                      {
                                                          'if': {
                                                              'filter_query': '{{sentiment}} = {}'.format(1),
                                                          },
                                                          'backgroundColor': '#C5F3D8',
                                                          'color': '#70BF91'
                                                      },
                                                      {
                                                          'if': {
                                                              'filter_query': '{{sentiment}} = {}'.format(-1),
                                                          },
                                                          'backgroundColor': '#FFE1E8',
                                                          'color': '#EA8299'
                                                      },
                                                  ]
                                              ), className='col s6 push-s1'
                                          )],
                                      className='row')

                              ]),

                              dcc.Tab(label='Твиттер', children=[
                                  dcc.Graph(
                                      figure={
                                          'data': [
                                              {'x': [1, 2, 3], 'y': [1, 4, 1],
                                               'type': 'bar', 'name': 'SF'},
                                              {'x': [1, 2, 3], 'y': [1, 2, 3],
                                               'type': 'bar', 'name': u'Montréal'},
                                          ]
                                      }
                                  )
                              ])
                          ])
                          ])],

                      className="container")

# app.layout = html.Div([
#     html.Div(dcc.Input(id='input-on-submit', type='text')),
#     html.Button('Submit', id='submit-val', n_clicks=0),
#     html.Div(id='container-button-basic',
#              children='Enter a value and press submit')
# ])


@app.callback(
    [Output('loading-output-2', 'children'),
     Output('sentiment', 'figure'), Output('active', 'children'), Output('likes', 'children'),
     Output('user_id', 'children'), Output('count_post', 'children'), Output('sentiment_binary', 'figure'), Output('table', 'data')],
    [Input('submit-val', 'n_clicks')],
    [State('input-on-submit', 'value'), State('input-on-submit-2', 'value')])
def update_output(n_clicks, value, value1):
    vk_scrap = ScrapVk(VK_TOKEN)
    info_data = vk_scrap.get_info(user_id=value)
    ic(info_data)
    if not n_clicks is None and info_data:
        info_data = info_data[0]
        user_id = info_data['id']
        posts, likes, count_posts, post_dict = vk_scrap.get_post_by_date(user_id=user_id, COUNT=value1)
        sentiment_data_posts, sentiment_data_binary, sentiment_data_dict = multiply_array(posts, post_dict)
        # sentiment_data_two_per, sentiment_data_binary_two = multiply_array_predict_two(posts,
        #                                                                                path_model=r'models/1-lstms-dim200Acc0.78.hdf5',
        # multiply_array_class(posts)
        return ['{} {} '.format(
            info_data['first_name'],
            info_data['last_name'],
    ),
            create_plot(sentiment_data_posts), 'True', str(likes), str(user_id), str(count_posts), create_plot_binary(sentiment_data_binary), sentiment_data_dict]
    # else:
    #     return ['', '', '', '', '', '', '']

@app.callback(
    Output('url-link', 'href'),
    [Input('submit-val-redirect', 'n_clicks'), Input('search-dropdown', 'value')],
    [State('input-on-submit-redirect', 'value')])
def update_output(n_clicks, drop_down, value):
    ic(value)
    if n_clicks:
        if drop_down == 'VK':
            print(value)
            return "https://vk.com/search?c[name]=1&c[per_page]=40&c[photo]=1&c[q]={}&c[section]=people".format(value)
        else:
            print(value)
            return "https://www.google.com/search?q={}".format(value)
    else:
        return "https://vk.com/search"

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=True)
