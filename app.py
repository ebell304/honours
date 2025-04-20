import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from visualise import fig, rules, themes, genres
import plotly.graph_objects as go
import plotly.colors as pc
import re


app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"], suppress_callback_exceptions=True)

# Initializing app layout: page-content is set in a callback below based off the current URL
# By default: '/' will display scatter graph
app.layout = html.Div([
    # NOTE: Below is an implementation for a navigation bar element that links to heatmap.
    # Heatmap is currently not included in current implementation.

    # html.Nav(
    #     children=[
    #         dcc.Link('Home', href='/'),
    #         dcc.Link('Heatmap', href='/heatmap')
    #     ] 
    # ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])



# Using regex statement to extract upper and lower values from a review score bin (in antecedents)
# For example: Review Score 80-85 will return two integers: 80, 85
def get_review_score_range(antecedent_str):
    match = re.search(r'Review Score: (\d+)-(\d+)', antecedent_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None





# Callback functionality to display webpage contents based on current URL
# NOTE: Heatmap is not included in current implementation.
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(path):
    if path == '/heatmap':
        from pages.heatmap import layout
        return layout
    elif path == '/':
        from pages.scatter import layout        # Retrieves scatter graph & layout from /pages/scatter.py
        return layout
    else:
        return html.H1("404 Page Not Found")    # Displays 404 message is page is invalid
    
    
    




# SCATTER PLOT CALLBACK FUNCTIONALITY
# Each input updates the same graph object, inputs can be found as Dash DCC and HTML components within scatter.py layout
@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('slider-occurrences', 'value'),   # Filtering occurrences (min & max values)
        Input('slider-confidence', 'value'),    # Filtering confidence (min & max values)
        Input('slider-lift', 'value'),          # Filtering lift (min & max values)
        Input('slider-review-score', 'value'),  # Filtering review score (min & max values)
        Input('direction-filter', 'value'),     # Filtering rule direction from 'Themes > Genres', 'Genres > Themes', or 'All'
        Input('dropdown-themes', 'value'),      # Filtering graph to only include rules containing selected themes
        Input('dropdown-genres', 'value')       # Filtering graph to only include rules containing selected genres
    ]
)

# Main application callback to update scatter graph, using parameters of sliders outlined above
def filter_scatter(range_occurrences, range_confidence, range_lift, range_review_score, direction_filter, theme_selection, genre_selection):

    # Reassigning fig to avoid shared state
    fig_copy = go.Figure(fig)


    # Creating pairings of minimum & maximum slider values
    min_occurrences, max_occurrences = range_occurrences
    min_confidence, max_confidence = range_confidence
    min_lift, max_lift = range_lift
    min_score, max_score = range_review_score

    # Filtering the rules DataFrame based on min&max slider values (sent from parameters)
    # NOTE: scatter.py imports a 'fresh' unfiltered graph at the start of each callback
    filtered_df = rules[(rules['occurrences'] >= min_occurrences) & (rules['occurrences'] <= max_occurrences) &
                        (rules['confidence'] >= min_confidence) & (rules['confidence'] <= max_confidence) &
                        (rules['lift'] >= min_lift) & (rules['lift'] <= max_lift) &
                        (rules['antecedents_str'].apply(lambda x: min_score <= get_review_score_range(x)[0] <= max_score))
                        ]

    # Theme/Genre selection filters
    # This will filter the scatter graph to ONLY rules containing chosen themes & genres in antecedent OR consequent
    # - Compatible with multiple tag selection & rule direction filtering
    if theme_selection:
        filtered_df = filtered_df[filtered_df['antecedents'].apply(lambda x: all(theme in x for theme in theme_selection)) |
                                  filtered_df['consequents'].apply(lambda x: all(theme in x for theme in theme_selection))]
    
    if genre_selection:
        filtered_df = filtered_df[filtered_df['antecedents'].apply(lambda x: all(genre in x for genre in genre_selection)) |
                                  filtered_df['consequents'].apply(lambda x: all(genre in x for genre in genre_selection))]


    # Method to filter rule direction based off user input
    # Also considers selected themes & genres from above
    def filter_direction(row, theme_selection, genre_selection):
        antecedents = set(row['antecedents'])   # Converted to sets for easier processing
        consequents = set(row['consequents'])

        # Initializes empty list if no themes or genres are selected
        if theme_selection is None:
            theme_selection = []
        if genre_selection is None:
            genre_selection = []

        # Specifying length of themes/genres within antecedents & consequents
        theme_count_antecedent = len(antecedents & themes)
        theme_count_consequent = len(consequents & themes)
        
        genre_count_antecedent = len(antecedents & genres)
        genre_count_consequent = len(consequents & genres)


        # Functionality for base direction filter (no theme_selection or genre_selection arguments applied)
        if not theme_selection and not genre_selection:
            if direction_filter == 'themes>genres':
                return theme_count_antecedent > 0 and theme_count_consequent == 0 and genre_count_consequent > 0
            elif direction_filter == 'genres>themes':
                return genre_count_antecedent > 0 and genre_count_consequent == 0 and theme_count_consequent > 0
            else:
                return True

        # Functionality for compatibility of theme_selection and genre_selection filtering
        if direction_filter == 'themes>genres':
            return (all(theme in antecedents for theme in theme_selection) if theme_selection else True) and \
                (all(genre in consequents for genre in genre_selection) if genre_selection else True)
        elif direction_filter =='genres>themes':
            return (all(genre in antecedents for genre in genre_selection) if genre_selection else True) and \
                (all(theme in consequents for theme in theme_selection) if theme_selection else True)
        else:
            return True
    
    # Applying direction filtering to new DataFrame that will be used to display updated scatter graph
    filtered_df = filtered_df[filtered_df.apply(lambda row: filter_direction(row, theme_selection, genre_selection), axis=1)]

    
    # Re-updating hoverlabel data since it gets lost on callbacks
    fig_copy.update_traces(
        type='scattergl',
        x=filtered_df['occurrences'], 
        y=filtered_df['confidence'],
        marker=dict(color=filtered_df['lift'], coloraxis="coloraxis"),
        customdata=filtered_df[['antecedents_str', 'consequents_str', 'lift', 'occurrences']].values
    )


    # This sets the background colour of the hoverlabel to match colour of 'lift' based off the maximum value of lift within rules.
    # Required for both initial visualisation & figure updates through callbacks.
    colour_min = rules['lift'].min()
    colour_max = rules['lift'].max()
    
    fig_copy.update_layout(
        coloraxis = dict(
            colorscale='Plasma',
            cmin=colour_min,
            cmax=colour_max
        )
    )   

    max_lift = rules['lift'].max()

    # Setting hoverlabel colour to match lift
    fig_copy.update_traces(
        hoverlabel=dict(
            bgcolor=[
                pc.sample_colorscale('Plasma', [lift / max_lift])[0]  
                    for lift in filtered_df['lift']
            ]
        )
    )

    return fig_copy



# NOTE: THIS RUNS THE APPLICATION LOCALLY
#if __name__ == "__main__":
#    app.run(debug=True)

# NOTE: THIS RUNS THE APPLICATION USING A DEPLOYED SERVER
server = app.server 