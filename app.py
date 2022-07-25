from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import dash_bio as dashbio
import pandas as pd
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.PULSE])

df = pd.read_csv('https://git.io/manhattan_data.csv')
df['-log10p'] = -np.log10(df['P'])

sub_df = df[df['CHR'] == 1]
table_df = df[df['-log10p'] >= 5]

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

sidebar = html.Div(
    [
        html.H2('Joseph Staniforth Dash Portfolio', className='display-4'),
        html.Hr(),
        html.P(
            r'Controls for the plots and the table. Data taken from https://git.io/manhattan_data.csv', className='lead'
        ),
        html.H4('Chromosome Scatter Plot'),
        dcc.Dropdown([*range(1,24,1)], 1, id='chr_drop_down',
                     style = {'display': 'inline-block', 'width': '12em'}),
        html.Br(),
        html.H4('Manhattan Plot'),
        html.Br(),
        dcc.Slider(1, 9, 1, value = 5, id = 'p_slider'),
        html.H4('Table Settings'),
        dcc.RadioItems(['Display from Scatter Plot', 'Display from Manhattan Plot'], 'Display from Manhattan Plot', id='Table_Radio',
                       labelStyle={'display': 'block'}),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
    html.Br(),
    html.Div([
        dcc.Graph(id='partial_scatter',
                  figure = px.scatter(sub_df, x = 'BP', y = '-log10p', color_discrete_sequence=['#20B2AA'], title = 'Chromosome 1'),
                  style={'display': 'inline-block', 'width':'55vh'}),
        dcc.Graph(
            id='full_manhattan',
            figure=dashbio.ManhattanPlot(
                dataframe=df,
                suggestiveline_value = False,
                highlight_color = '#20B2AA',
                showlegend = False,
            showgrid = False), 
            style={'display': 'inline-block', 'width':'83vh'})
    ],style={'display': 'inline-block'}),
    html.Div([
        dash_table.DataTable(table_df.to_dict('records'), id = 'data_table',)
    ])
], style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])

@app.callback(
    Output('full_manhattan', 'figure'),
    Input('p_slider', 'value'),
)

def update_manhattanplot(p_slider):
    return dashbio.ManhattanPlot(
        dataframe=df,
        genomewideline_value=p_slider,
        suggestiveline_value = False,
        highlight_color = '#20B2AA',
        showlegend = False,
        showgrid = False
    )

@app.callback(
    Output('partial_scatter', 'figure'), 
    Input('chr_drop_down', 'value'))

def update_scatter_plot(chr_drop_down):
    df_to_plot = df[df['CHR'] == chr_drop_down]
    fig = px.scatter(df_to_plot, x = 'BP', y = '-log10p', color_discrete_sequence=['#20B2AA'], title = f'Chromosome {chr_drop_down}')
    return fig

@app.callback(
    Output('data_table', 'data'),
    Input('p_slider', 'value'),
    Input('chr_drop_down', 'value'),
    Input('Table_Radio', 'value')
)

def update_table(p_slider, chr_drop_down, Table_Radio):
    if Table_Radio == 'Display from Scatter Plot':
        table_df = df[df['CHR'] == chr_drop_down]
        return table_df.to_dict('records')
    elif Table_Radio == 'Display from Manhattan Plot':
        table_df = df[df['-log10p'] >= p_slider]
        return table_df.to_dict('records')

if __name__ == '__main__':
    app.run_server()