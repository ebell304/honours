from dash import html
from dash import dcc
from visualise import fig, rules, themes, genres


# Filtering dropdown boxes based on existing themes/genres in rules dataset
available_genres = set(
    [item for sublist in rules['antecedents'].dropna() for item in sublist] +
    [item for sublist in rules['consequents'].dropna() for item in sublist]
)
available_themes = set(
    [item for sublist in rules['antecedents'].dropna() for item in sublist] +
    [item for sublist in rules['consequents'].dropna() for item in sublist]
)

# Subtracting available themes & genres from ALL themes & rules
filtered_genres = available_genres.intersection(genres)
filtered_themes = available_themes.intersection(themes)

# Building a list of available themes and genres to display within dropdown boxes
genre_options = [{'label': genre, 'value': genre}
                 for genre in sorted(filtered_genres)]
theme_options = [{'label': theme, 'value': theme}
                 for theme in sorted(filtered_themes)]


layout = html.Div([

    # Page Header
    html.H2("Steam Games Association Rule Mining Scatter Graph",
            style={'textAlign': 'center'}),

    # Scatter Plot (will be filtered by filter_scatter() callback in app.py)
    dcc.Graph(id='scatter-plot',
              figure=fig,
              config={
                  "scrollZoom": True,
                  "displayModeBar": False,
                  "responsive": True
              },
              style={'height': '80vh',
                     'width': 'auto',
                     'margin-left': 'auto',
                     'margin-right': 'auto',
                     'overflow': 'hidden',
                     }),

    html.Footer([

        html.Details([
            # Details/Summary section allows filter menu to pop up from footer
            html.Summary("TOGGLE MENU", style={
                         'cursor': 'pointer', 'padding': '10px', 'justify-self': 'center', 'fontWeight': '500'}),

            # Controls Description
            html.Div([
                html.P(["Double Click: Reset Graph View"], style={'margin-right': '7%'}),
                html.P(["Scroll-wheel: Zoom In/Out"], style={'margin-right': '4%'}),
                html.P(["Drag: Pan Graph"], style={'margin-left': '7%'}),
            ], id="controls", style={
                "display": 'flex', 
                'justify-content': 'center', 
                'fontWeight': '500', 
                'border': '1px solid purple', 
                'padding-top': '5px', 
                'height': '40px',
                'backgroundColor': 'rgba(255, 255, 250, 0.8)'
                }),

            
            html.Div([

                html.Div([

                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='dropdown-themes',
                                options=theme_options,
                                multi=True,
                                placeholder='Select Themes'
                            )], id='container-theme-dropdown', style={'margin-top': '20px', 'margin-left': '20px', 'width': '250px', 'border': '1px solid #834094'}),


                        html.Div([
                            dcc.Dropdown(
                                id='dropdown-genres',
                                options=genre_options,
                                multi=True,
                                placeholder='Select Genres'
                            )], id='container-genre-dropdown', style={'margin-top': '20px', 'margin-left': '20px', 'width': '250px', 'border': '1px solid #834094' }),
                    ], id='container-theme-genres'),

                    html.Div([
                        dcc.RadioItems(
                            id='direction-filter',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': 'Themes > Genres',
                                    'value': 'themes>genres'},
                                {'label': 'Genres > Themes',
                                    'value': 'genres>themes'},
                            ],
                            value='all'
                        )
                    ], id='container-direction-filter', style={'width': '250px', 'margin-right': '10px', 'margin-top': '20px'}),

                ], id='container-selections', style={'backgroundColor': 'rgba(255, 255, 250, 0.8)', 'borderRadius': '30px', 'display': 'flex', 'flexDirection': 'row'}),


                html.Div([
                    html.Div([
                        html.Label("Filter Occurrences", style={'margin-left': '15px', 'margin-top': '5px'}),
                        dcc.RangeSlider(
                            id='slider-occurrences',
                            min=rules['occurrences'].min(),
                            max=rules['occurrences'].max(),
                            value=[rules['occurrences'].min(
                            ), rules['occurrences'].max()],
                        )
                    ], id='container-occurrences'),

                    html.Div([
                        html.Label("Filter Confidence", style={'margin-left': '15px'}),
                        dcc.RangeSlider(
                            id='slider-confidence',
                            min=rules['confidence'].min(),
                            max=rules['confidence'].max(),
                            value=[rules['confidence'].min(
                            ), rules['confidence'].max()],
                            marks={i / 10: f'{i * 10}%' for i in range(5, 11)}

                        )
                    ], id='container-confidence'),

                    html.Div([
                        html.Label("Filter Lift", style={'margin-left': '15px'}),
                        dcc.RangeSlider(
                            id='slider-lift',
                            min=0,
                            max=rules['lift'].max(),
                            value=[0, 71],
                            marks={i: str(i) for i in range(0, 71, 10)}

                        )
                    ], id='container-lift'),


                    html.Div([
                        html.Label("Filter Logarithmic Review Score", style={'margin-left': '15px'}),
                        dcc.RangeSlider(
                            id='slider-review-score',
                            min=0,
                            max=100,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 10)}

                        )
                    ], id='container-review-score')



                ], id='container-sliders', style={'backgroundColor': 'rgba(255, 255, 250, 0.8)', 'borderRadius': '30px'}),


            ], id='container-filters'),

        ])
    ], style={
        'position': 'absolute',
        'bottom': '0',
        'left': '0',
        'width': '100%',
        'backgroundColor': '#f8f9fa',
        'padding': '5px',
        'zIndex': '1000',
        'maxHeight': '400px',
        'overflowY': 'auto',
        'border-top': '1px solid purple',
        'backgroundColor': 'rgba(255, 255, 255, 0.85)',
    })

], className='scatter-plot')
