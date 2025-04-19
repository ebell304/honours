# Importing libraries
import pandas as pd                 # For data structuring & manipulation
import plotly.express as px
import plotly.colors as pc
import ast
import re

# Loading in .csv files for visualisation
df_genres = pd.read_csv('df_genres.csv')
df_themes = pd.read_csv('df_themes.csv')
df_reviews = pd.read_csv('df_reviews.csv')
rules = pd.read_csv('rules.csv')

# Creating new column: Occurrences
# This is because the results of the support metric were too difficult to interpret
rules["occurrences"] = (rules["support"] * 31752).round() - 1



# Removing frozen string from antecedents & consequents to iterate over variables
# The values are stored as both strings & python objects (for frontend displaying & backend processing)
def remove_frozen_string(string):
    return frozenset(ast.literal_eval(string.replace("frozenset(", "").replace(")", "")))

rules['antecedents'] = rules['antecedents'].apply(remove_frozen_string)
rules['consequents'] = rules['consequents'].apply(remove_frozen_string)



# Initialising sets for themes & genres to import later in app.py & scatter.py
genres = set(df_genres.columns)
themes = set(df_themes.columns)




# Method to reformat review score using regex statement
# FROM: review_score_bin_80-85      TO: Review Score: 80-85
def reformat_review_score(antecedent):
    match = re.match(r'review_bin_(\d+-\d+)', antecedent)
    if match:
        return f"Review Score: {match.group(1)}"    # Reformatting if antecedent contains review score
    return antecedent

# Applying method to string value of antecedents
rules['antecedents_str'] = rules['antecedents_str'].apply(lambda x: ', '.join(map(reformat_review_score, x.split(', '))))



# Plotting association rules as a scatter graph, specifying variables to display with hoverdata 
# X: Support (modified to occurrences for interpretability)
# Y: Confidence
# Z: Lift (colour)
fig = px.scatter(rules, x='occurrences', y='confidence', color='lift',
                hover_data={"antecedents_str": True, "consequents_str": True, "lift": True, "occurrences": True},
                render_mode='auto',
                color_continuous_scale=px.colors.sequential.Plasma
)


# Custom hoverdata template (displaying occurrences instead of support)
fig.update_traces(
    
    hovertemplate="<b>Antecedents:</b> %{customdata[0]}<br>" +
                  "<b>Consequents:</b> %{customdata[1]}<br>" +
                  "<b>Confidence:</b> %{y:.0%}<br>" +
                  "<b>Occurrences:</b> %{customdata[3]}<br>" +
                  "<b>Lift:</b> %{customdata[2]:.2f}<br>"                  
)



# Setting plotly graph controls
fig.update_layout(dragmode='pan',
                  uirevision='scatter'
)


# Setting plot background/container colours & x/y-axis labels
fig.update_layout(
    plot_bgcolor='#eeede7',
    paper_bgcolor='#eeede7',
    xaxis=dict(title='Occurrences'),
    yaxis=dict(title='Confidence')
)


# Setting markers to diamond shape with yellow outline
fig.update_traces(marker=dict(
    symbol='diamond',
    line=dict(
        width=0.5,
        color=('rgba(255,255,0,0.8)')
    ),
    size=8,
    opacity=1
))


# Setting margins and x-axis label position to top
fig.update_layout(
    xaxis=dict(
        side='top'
    ),
    margin=dict(
        l=0,
        r=0,
        t=10,
        b=10
    )
)


# Displaying custom axis zoom for scatter graph (to show 50% to 100% confidence in full)
fig.update_layout(
    yaxis=dict(range=[0.49, 1.01]),
    yaxis_tickformat=".0%"
)


# This sets the background colour of the hoverlabel to match colour of 'lift' based off the maximum value of lift within rules.
max_lift = rules['lift'].max()
fig.update_traces(
    hoverlabel=dict(
        bgcolor=[
            pc.sample_colorscale('Plasma', [lift / max_lift])[0]  
                for lift in rules['lift']
        ]
    )
)








