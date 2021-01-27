import warnings

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, State, Input

from classificator_sentiment_analysis import multiply_array
from vk_scrap import VK_TOKEN, ScrapVk

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
                            xaxis={'title': 'Labels'})
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
                            xaxis={'title': 'Labels'})
    }
    plots.append(fig)

    return fig



app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'
], external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'])

app.layout = html.Div([html.Div([
    html.H2('Social portrait App',
            style={'float': 'center',
                   }),
], className='row')] + [html.Div([html.Div([
    html.Div(dcc.Input(id='input-on-submit', type='text',  placeholder="input vk id")),
    html.Button('Submit', id='submit-val', n_clicks=0, className="btn waves-effect waves-light"),
], className='input-field col s3')], className='row')] +[html.Div(
                          [ dcc.Loading(
        id="loading-2",
        children=[html.H5([html.H5(id="loading-output-2")])],
        type="circle",

    )], className='row')] + [html.Div([
    html.H5('Имя пользователя: ', className='col s3'),
    html.H5(id='user_id', style={
        'color': 'green',
    }, className='col s3')], className='row')] + [html.Div([
    html.H5('Активный ли пользователь?: ', className='col s3'),
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
                                              {'x': [0,0], 'y': [0, 0]}
                                          ]
                                      }), ], className='col s12 m12 l13')
                          ], className='row')] +   [html.Div(
                          [
                              html.Div(
                                  [dcc.Graph(
                                      id='sentiment_binary',

                                      config=dict(
                                          displayModeBar=displayModeBar
                                      ),
                                      figure={
                                          'data': [
                                              {'x': [0,0], 'y': [0, 0]}
                                          ]
                                      }), ], className='col s12 m12 l13')
                          ], className='row')],


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
     Output('user_id', 'children'), Output('count_post', 'children'), Output('sentiment_binary', 'figure')],
    [Input('submit-val', 'n_clicks')],
    [State('input-on-submit', 'value')])
def update_output(n_clicks, value):
    vk_scrap = ScrapVk(VK_TOKEN)
    info_data = vk_scrap.get_info(user_id=value)
    if info_data:
        info_data = info_data[0]
        user_id = info_data['id']
        posts, likes, count_posts = vk_scrap.get_post_by_date(user_id=user_id)
        sentiment_data_posts, sentiment_data_binary = multiply_array(posts)
        # multiply_array_class(posts)
        return ['{} {} '.format(
            info_data['first_name'],
            info_data['last_name'],
    ), create_plot(sentiment_data_posts), 'True', str(likes), str(user_id), str(count_posts), create_plot_binary(sentiment_data_binary)]
    else:
        return 'Invalid Id'




if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=True)
