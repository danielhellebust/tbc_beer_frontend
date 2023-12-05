import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pymongo
import pandas as pd
import plotly.graph_objs as go
from dash_mantine_components import MantineProvider, Container, Grid, Col
import dash_mantine_components
from dash import dcc
import dash_daq as daq
import numpy as np


# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://beer:beer@cluster0.rhshz.mongodb.net/")  # Replace with your MongoDB connection string
db = client['Beer']  # Replace with your database name
collection = db['beer_review']  # Replace with your collection name

# Dash app
app = dash.Dash(__name__)
server = app.server

# Initialize Dash MantineProvider with dark theme
app.layout = MantineProvider(
    theme={"colorScheme": "dark"},
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        Container(
            children=[
                html.H1("TBC Juleøl Smaking 2023 Scoreboard", style={'textAlign': 'center'}),
                Grid(
                    style={'maxWidth': '2200px','maxHeight': '1500px', 'margin': 'auto'},
                    gutter="xl",
                    children=[
                        Col(children=[
                            html.H3("Aroma", style={'textAlign': 'center'}),

                        daq.Gauge(
                            id='aroma-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=5,
                            label='Default',
                            max=100,
                            min=0
                        )],span=4),
                        Col(children=[
                            html.H3("Smak", style={'textAlign': 'center'}),

                            daq.Gauge(
                            id='taste-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=5,
                            label='Default',
                            max=100,
                            min=0
                        )],span=4),
                        Col(children=[
                            html.H3("Navn på øl", style={'textAlign': 'center'}),

                            daq.Gauge(
                            id='name-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=5,
                            label='Default',
                            max=500,
                            min=0
                        )],span=4),
                        Col(children=[
                            html.H3("Øl stil", style={'textAlign': 'center'}),

                            daq.Gauge(
                            id='style-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=5,
                            label='Default',
                            max=500,
                            min=0
                        )],span=4),
                        Col(children=[
                            html.H3("Alkohol prosent", style={'textAlign': 'center'}),

                            daq.Gauge(
                            id='alcohol-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=5,
                            label='Default',
                            max=1000,
                            min=0
                        )],span=4),
                        Col(children=[
                            html.H3("Total Score", style={'textAlign': 'center'}),

                            daq.Gauge(
                            id='total-score-gauge',
                            showCurrentValue=True,
                            units="POENG",
                            value=0,
                            label='Default',
                            max=2000,
                            min=0
                        )],span=4),

                    ]
                ),
                dcc.Checklist(
                    id='trace-toggle',
                    options=['Vis fasit'],
                    value=[],  # Initial value, none of the traces are shown
                    inline=True,
                ),
                dcc.Graph(id='rating-scatterplot'),
                dcc.Graph(id='total-score-scatterplot'),

                dash_mantine_components.Button(
                    id="update-scatterplot-button",
                    children="Update Scatterplot",
                    variant="outline",
                    color="blue",
                    fullWidth=False,
                    size="md",
                    radius="md"),

                dcc.Interval(
                    id='interval-component',
                    interval=10 * 9000,  # in milliseconds
                    n_intervals=0
                ),
            ],
        style={'maxWidth': '2200px','maxHeight': '1500px', 'margin': 'auto'})
    ],
)

# Callback to update scatterplot based on user input
@app.callback(
    [Output('rating-scatterplot', 'figure'),
        Output('total-score-scatterplot', 'figure'),
     Output('aroma-gauge', 'value'),
     Output('taste-gauge', 'value'),
     Output('name-gauge', 'value'),
        Output('style-gauge', 'value'),
     Output('alcohol-gauge', 'value'),
        Output('total-score-gauge', 'value'),
     Output('aroma-gauge', 'label'),
     Output('taste-gauge', 'label'),
     Output('name-gauge', 'label'),
        Output('style-gauge', 'label'),
     Output('alcohol-gauge', 'label'),
        Output('total-score-gauge', 'label'),
     ],
    [Input('update-scatterplot-button', 'n_clicks'),
     Input('trace-toggle', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_rating_scatterplot(n_clicks, fasit, n_intervals):

    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    if fasit == ['Vis fasit']:
        # Determine the range of beer numbers based on the current layout
        # Collect all objects from MongoDB and create a DataFrame
        all_objects_cursor = collection.find()
        all_objects_data = list(all_objects_cursor)
        all_objects_df = pd.DataFrame(all_objects_data)
        all_objects_df = all_objects_df[all_objects_df['Juleøl_nummer'] != 'Register']
        all_objects_df['Juleøl_nummer'] = all_objects_df['Juleøl_nummer'].astype(int)
        all_objects_df = all_objects_df.sort_values('Juleøl_nummer')
        df_sum_score_aroma = all_objects_df.groupby(['Rytter'])['Aroma_Score'].sum().to_frame().reset_index()
        df_sum_score_style = all_objects_df.groupby(['Rytter'])['Style_Score'].sum().to_frame().reset_index()
        df_sum_score_taste = all_objects_df.groupby(['Rytter'])['Taste_Score'].sum().to_frame().reset_index()
        df_sum_score_name = all_objects_df.groupby(['Rytter'])['Name_Score'].sum().to_frame().reset_index()
        df_sum_score_alcohol = all_objects_df.groupby(['Rytter'])['Alcohol_Score'].sum().to_frame().reset_index()
        df_sum_score_total = all_objects_df[all_objects_df['Rytter'] != "Fasit"].groupby(['Rytter'])['Total_Score'].sum().to_frame().reset_index()

        max_score_aroma_name = df_sum_score_aroma[df_sum_score_aroma['Aroma_Score'] == df_sum_score_aroma['Aroma_Score'].max()]['Rytter'].values[0]
        max_score_style_name = df_sum_score_style[df_sum_score_style['Style_Score'] == df_sum_score_style['Style_Score'].max()]['Rytter'].values[0]
        max_score_taste_name = df_sum_score_taste[df_sum_score_taste['Taste_Score'] == df_sum_score_taste['Taste_Score'].max()]['Rytter'].values[0]
        max_score_name_name = df_sum_score_name[df_sum_score_name['Name_Score'] == df_sum_score_name['Name_Score'].max()]['Rytter'].values[0]
        max_score_alcohol_name = df_sum_score_alcohol[df_sum_score_alcohol['Alcohol_Score'] == df_sum_score_alcohol['Alcohol_Score'].max()]['Rytter'].values[0]
        max_score_total_name = df_sum_score_total[df_sum_score_total['Total_Score'] == df_sum_score_total['Total_Score'].max()]['Rytter'].values[0]



        # Create a scatter plot with separate traces for each beer
        fig = go.Figure()
        for name in all_objects_df['Rytter'].unique():
            df_by_name = all_objects_df[all_objects_df['Rytter'] == name]
            fig.add_trace(go.Scatter(
                x=df_by_name['Juleøl_nummer'][0:13],
                y=df_by_name['Rating'],
                mode='lines+markers+text',
                name=name,
                text=df_by_name['Navn_på_øl'],
                textposition='top center',
                line=dict(width=4),  # Set the line thickness
                marker=dict(size=12),  # Set the marker size
            ))

        fig.update_layout(
            title='Rating per øl',
            xaxis_title='Juleøl_nummer',
            yaxis_title='Rating',
            showlegend=True,
            yaxis=dict(
                range=[-1, 6],  # Set the desired y-axis range
            ),
            paper_bgcolor='rgb(34, 34, 34)',  # Dark background color
            plot_bgcolor='white',
            height=700,# Dark background color
            font=dict(
                family='Helvetica',  # You can change the font family
                size=16,  # Adjust the font size as needed
                color='grey',  # Font color
            )

        )

        # Create a horizontal bar chart with separate traces for each rider
        fig2 = go.Figure()

        # Sort by total score in descending order
        sorted_names = df_sum_score_total.sort_values(by='Total_Score', ascending=True)['Rytter'].tolist()

        for name in sorted_names:
            df_by_name = all_objects_df[all_objects_df['Rytter'] == name]
            total_scores = df_by_name['Total_Score'].cumsum()

            # Use a different color for each rider
            color = 'rgba(' + ', '.join(str(c) for c in np.random.randint(0, 256, 3)) + ', 0.6)'

            fig2.add_trace(go.Bar(
                y=[name],
                x=[total_scores.iloc[-1]],
                orientation='h',
                text=[total_scores.iloc[-1]],
                name=name,
                textposition='auto',
                marker=dict(
                    color=color,
                    line=dict(
                        color='rgba(50, 171, 96, 1.0)',
                        width=2,
                    )
                )
            ))

        # Update the layout for the horizontal bar chart
        fig2.update_layout(
            title='Total Score',
            xaxis_title='Total Score',
            yaxis_title='Rytter',
            showlegend=True,
            xaxis=dict(
                range=[-1, 1500],  # Set the desired x-axis range
            ),
            paper_bgcolor='rgb(34, 34, 34)',  # Dark background color
            plot_bgcolor='white',
            height=700,
            font=dict(
                family='Helvetica',
                size=16,
                color='grey',
            )
        )

        return (fig,fig2, df_sum_score_aroma['Aroma_Score'].max(), df_sum_score_taste['Taste_Score'].max(),
                df_sum_score_name['Name_Score'].max(), df_sum_score_style['Style_Score'].max(),
                df_sum_score_alcohol['Alcohol_Score'].max(), df_sum_score_total['Total_Score'].max(),
                max_score_aroma_name, max_score_taste_name,max_score_name_name,max_score_style_name,max_score_alcohol_name,max_score_total_name)

    else:
        # Determine the range of beer numbers based on the current layout
        # Collect all objects from MongoDB and create a DataFrame
        all_objects_cursor = collection.find()
        all_objects_data = list(all_objects_cursor)
        all_objects_df = pd.DataFrame(all_objects_data).sort_values('Juleøl_nummer')
        all_objects_df = all_objects_df[all_objects_df['Juleøl_nummer'] != 'Register']
        all_objects_df['Juleøl_nummer'] = all_objects_df['Juleøl_nummer'].astype(int)
        all_objects_df = all_objects_df.sort_values('Juleøl_nummer')
        df_sum_score_aroma = all_objects_df.groupby(['Rytter'])['Aroma_Score'].sum().to_frame().reset_index()
        df_sum_score_style = all_objects_df.groupby(['Rytter'])['Style_Score'].sum().to_frame().reset_index()
        df_sum_score_taste = all_objects_df.groupby(['Rytter'])['Taste_Score'].sum().to_frame().reset_index()
        df_sum_score_name = all_objects_df.groupby(['Rytter'])['Name_Score'].sum().to_frame().reset_index()
        df_sum_score_alcohol = all_objects_df.groupby(['Rytter'])['Alcohol_Score'].sum().to_frame().reset_index()
        df_sum_score_total = all_objects_df[all_objects_df['Rytter'] != "Fasit"].groupby(['Rytter'])['Total_Score'].sum().to_frame().reset_index()

        max_score_aroma_name = \
        df_sum_score_aroma[df_sum_score_aroma['Aroma_Score'] == df_sum_score_aroma['Aroma_Score'].max()][
            'Rytter'].values[0]
        max_score_style_name = \
        df_sum_score_style[df_sum_score_style['Style_Score'] == df_sum_score_style['Style_Score'].max()][
            'Rytter'].values[0]
        max_score_taste_name = \
        df_sum_score_taste[df_sum_score_taste['Taste_Score'] == df_sum_score_taste['Taste_Score'].max()][
            'Rytter'].values[0]
        max_score_name_name = \
        df_sum_score_name[df_sum_score_name['Name_Score'] == df_sum_score_name['Name_Score'].max()]['Rytter'].values[0]
        max_score_alcohol_name = \
        df_sum_score_alcohol[df_sum_score_alcohol['Alcohol_Score'] == df_sum_score_alcohol['Alcohol_Score'].max()][
            'Rytter'].values[0]
        max_score_total_name = \
        df_sum_score_total[df_sum_score_total['Total_Score'] == df_sum_score_total['Total_Score'].max()][
            'Rytter'].values[0]

        # Create a scatter plot with separate traces for each beer
        fig = go.Figure()
        for name in all_objects_df['Rytter'].unique():
            df_by_name = all_objects_df[all_objects_df['Rytter'] == name]
            fig.add_trace(go.Scatter(
                x=df_by_name['Juleøl_nummer'],
                y=df_by_name['Rating'],
                mode='lines+markers+text',
                name=name,
                line=dict(width=4),  # Set the line thickness
                marker=dict(size=12),  # Set the marker size
                # text=df_by_name['Navn_på_øl'],


            ))

        fig.update_layout(
            title='Rating per øl',
            xaxis_title='Juleøl_nummer',
            yaxis_title='Rating',
            showlegend=True,
            yaxis=dict(
                range=[-1, 6],  # Set the desired y-axis range
            ),
            paper_bgcolor='rgb(34, 34, 34)',  # Dark background color
            plot_bgcolor='white',
            height=700,# Dark background color
            font=dict(
                family='Helvetica',  # You can change the font family
                size=16,  # Adjust the font size as needed
                color='grey',  # Font color
            )
        )


        # Create a horizontal bar chart with separate traces for each rider
        fig2 = go.Figure()

        # Sort by total score in descending order
        sorted_names = df_sum_score_total.sort_values(by='Total_Score', ascending=True)['Rytter'].tolist()

        for name in sorted_names:
            df_by_name = all_objects_df[all_objects_df['Rytter'] == name]
            total_scores = df_by_name['Total_Score'].cumsum()

            # Use a different color for each rider
            color = 'rgba(' + ', '.join(str(c) for c in np.random.randint(0, 256, 3)) + ', 0.6)'

            fig2.add_trace(go.Bar(
                y=[name],
                x=[total_scores.iloc[-1]],
                orientation='h',
                text=[total_scores.iloc[-1]],
                name=name,
                textposition='auto',
                marker=dict(
                    color=color,
                    line=dict(
                        color='rgba(50, 171, 96, 1.0)',
                        width=2,
                    )
                )
            ))

        # Update the layout for the horizontal bar chart
        fig2.update_layout(
            title='Total Score',
            xaxis_title='Total Score',
            yaxis_title='Rytter',
            showlegend=True,
            xaxis=dict(
                range=[-1, 1500],  # Set the desired x-axis range
            ),
            paper_bgcolor='rgb(34, 34, 34)',  # Dark background color
            plot_bgcolor='white',
            height=700,
            font=dict(
                family='Helvetica',
                size=16,
                color='grey',
            )
        )

        return (fig,fig2, df_sum_score_aroma['Aroma_Score'].max(), df_sum_score_taste['Taste_Score'].max(), df_sum_score_name['Name_Score'].max(),df_sum_score_style['Style_Score'].max(), df_sum_score_alcohol['Alcohol_Score'].max(),
                df_sum_score_total['Total_Score'].max(),
                max_score_aroma_name, max_score_taste_name,max_score_name_name,max_score_style_name,max_score_alcohol_name,max_score_total_name)

if __name__ == '__main__':
    app.run_server(debug=True)
