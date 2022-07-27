from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import dash_bio as dashbio
import pandas as pd
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
import base64
import io

app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

#df = pd.read_csv('https://git.io/manhattan_data.csv')
#df['-log10p'] = -np.log10(df['P'])

#sub_df = df[df['CHR'] == 1]
#table_df = df[df['-log10p'] >= 5]
#drop_down_list = list(set(df['CHR'].to_list()))
df = None
drop_down_list = []

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20rem',
    'padding': '2rem 1rem',
    #'background-color': '#592C98'
}

CONTENT_STYLE = {
    'margin-left': '25rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

error_modal = html.Div([
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Error")),
        dbc.ModalBody("Please upload a csv.")
    ],
    id = 'notcsv_modal',
    size = 'lg')
])

sidebar = html.Div(
    [
        html.H2('manhattanDash', className='display-4'),
        html.Hr(),
        html.P(
            r'Controls for the plots and the table. Example data available at https://git.io/manhattan_data.csv', className='lead'
        ),
        dcc.Upload(html.Button('Upload Data'),id = 'upload_data'),
        html.H4('Chromosome Scatter Plot'),
        dcc.Dropdown(drop_down_list, 1, id='chr_drop_down',
                     style = {'display': 'inline-block', 'width': '12em'}),
        html.Br(),
        html.H4('Manhattan Plot'),
        html.Br(),
        dcc.Slider(2, 8, 1, value = 5, id = 'p_slider'),
        html.H4('Table Settings'),
        dcc.RadioItems(['Display from Scatter Plot', 'Display from Manhattan Plot'], 'Display from Manhattan Plot', id='Table_Radio',
                       labelStyle={'display': 'block'}),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    html.Br(),
    html.Div([
        dcc.Graph(id='partial_scatter', style={'display': 'inline-block', 'width':'55vh'}),
        dcc.Graph(id='full_manhattan',style={'display': 'inline-block', 'width':'83vh'})
    ],style={'display': 'inline-block'}),
    html.Div([
        dash_table.DataTable(id = 'data_table')
    ])
], style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])

@app.callback(
    Output('full_manhattan', 'figure'),
    Input('p_slider', 'value'),
    Input('upload_data', 'contents'),
    Input('upload_data', 'filename')
)

def update_manhattanplot(p_slider, contents, filename):
    return dashbio.ManhattanPlot(
        dataframe=parse_contents(contents, filename) if contents else df,
        genomewideline_value=p_slider,
        suggestiveline_value = False,
        highlight_color = '#20B2AA',
        showlegend = False,
        showgrid = False,
        title = f'{filename} Manhattan Plot'
    )

@app.callback(
    Output('partial_scatter', 'figure'), 
    Input('chr_drop_down', 'value'),
    Input('upload_data', 'contents'),
    Input('upload_data', 'filename'))

def update_scatter_plot(chr_drop_down, contents, filename):
    #if contents:
    #    df = parse_contents(contents, filename)
    #    df['-log10p'] = -np.log10(df['P'])
    #df_to_plot = df[df['CHR'] == chr_drop_down] #THROWING ERROR
    #fig = px.scatter(df_to_plot, x = 'BP', y = '-log10p', color_discrete_sequence=['#20B2AA'], title = f'Chromosome {chr_drop_down}')
    #return fig

    return px.scatter(
        data_frame = filter_df_scatter(df = import_contents(parse_contents(contents, filename)), chr_drop_down = chr_drop_down)if contents else df,
        x = 'BP',
        y='-log10p',
        color_discrete_sequence=['#20B2AA'],
        title = f'Chromosome {chr_drop_down}'
    )


@app.callback(
    Output('data_table', 'data'),
    Input('p_slider', 'value'),
    Input('chr_drop_down', 'value'),
    Input('Table_Radio', 'value'),
    Input('upload_data', 'contents'),
    Input('upload_data', 'filename'))


def update_table(p_slider, chr_drop_down, Table_Radio, contents, filename):
    if contents and Table_Radio == 'Display from Scatter Plot':
        df = parse_contents(contents, filename)
        df['-log10p'] = -np.log10(df['P'])
        table_df = df[df['CHR'] == chr_drop_down]
        return table_df.to_dict('records')
    elif contents and Table_Radio == 'Display from Manhattan Plot':
        df = parse_contents(contents, filename)
        df['-log10p'] = -np.log10(df['P'])
        table_df = df[df['-log10p'] >= p_slider]
        return table_df.to_dict('records')
    elif Table_Radio == 'Display from Scatter Plot':
        table_df = df[df['CHR'] == chr_drop_down]
        return table_df.to_dict('records')
    elif Table_Radio == 'Display from Manhattan Plot':
        table_df = df[df['-log10p'] >= p_slider] #THROWING ERROR
        return table_df.to_dict('records')

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        return error_modal
    return df

def import_contents(df):
    df['-log10p'] = -np.log10(df['P'])
    return df

def filter_df_scatter(df, chr_drop_down):
    return df[df['CHR'] == chr_drop_down] 

@app.callback(
    Output('chr_drop_down', 'options'),
    Input('upload_data', 'contents'),
    Input('upload_data', 'filename')
    )

def update_drop_down(contents, filename):
    df = parse_contents(contents, filename)
    return list(set(df['CHR'].to_list()))


#if __name__ == '__main__':
app.run_server(debug = True)