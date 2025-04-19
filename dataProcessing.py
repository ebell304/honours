# Importing libraries
import pandas as pd                 # For data structuring & manipulation
import matplotlib.pyplot as plt     # For initial data visualisations (EDA)
import math                         # For logarithmic calculations 
import re                           # For regex statements
from mlxtend.frequent_patterns import fpgrowth, association_rules # For association rule mining & itemset generation
import plotly.express as px         # For heatmap visualisation
import plotly.graph_objects as go   # For heatmap visualisation



# Loading the dataset into a Pandas DataFrame
# using orient='index' since JSON data is structured as dictionary
df = pd.read_json('games.json', orient='index')


# Used for Exploratory Data Analysis
#print(df.shape)                    # Number of rows/columns
#print(df.head())                   # Previews 5 records
#print(df.columns)                  # Prints all column names
#print(df.isnull().sum())           # Prints number of missing values for each column


# Method to append new columns to the DataFrame
def append_new_columns():

    # Total Reviews: Positive + Negative reviews
    df['total_reviews'] = df.apply(lambda row: row['positive'] + row['negative'], axis=1)
    
    # Percent Positive: Positive / (Positive + Negative) * 100, returns a percentage
    df['percent_positive'] = df.apply(
    lambda row: round((row['positive'] / (row['positive'] + row['negative']) * 100), 3) # rounds percentage to 3 decimal places (e.g. 94.425%) 
    if (row['positive']) > 0 else 0, axis=1) 

    # Log Rating: Logarithmic weighting for percent_positive based on total_reviews.
    # Note: 50 has been added to the total reviews for each game to accommodate smaller titles (possible emerging genres or newly-released games)
    df['log_rating'] = df.apply(lambda row: row['percent_positive'] - (row['percent_positive'] - 0.5) * 2 **(-math.log10(row['total_reviews'] + 50))
    if (row['positive']) > 0 else 0, axis=1)
    

append_new_columns()



# Removing rows with less than 25 total ratings
print("Removing all games with less than 25 ratings")
df = df[df['total_reviews'] > 24]
print(df.shape)


# Displaying 40 rows with highest logarithmic review score
#print(df.nlargest(40, 'log_rating')[['name', 'percent_positive', 'log_rating']])

# Viewing summary statistics of log_rating column
#print(df['log_rating'].describe())



# Test appID to display game information of specific columns
appID = 632470

# Method to print out column information of chosen record using its unique appID
def printGameInfo():
    print("Game: ", df.loc[appID]['name'])
    print("Positive ratings: ", df.loc[appID]['positive'])
    print("Negative ratings: ", df.loc[appID]['negative'])
    print("Score Rank: ", df.loc[appID]['score_rank'])
    print("Average playtime (forever): ", df.loc[appID]['average_playtime_forever'])
    print("Average playtime (2wk): ", df.loc[appID]['average_playtime_2weeks'])
    print("Median playtime (forever): ", df.loc[appID]['median_playtime_forever'])
    print("Median playtime (2wk): ", df.loc[appID]['median_playtime_2weeks'])
    print("Peak concurrent playercount (yesterday): ", df.loc[appID]['peak_ccu'])
    print("% Positive ratings ratings: ", df.loc[appID]['percent_positive'])
    print("LOGARITHMIC RATING: ", df.loc[appID]['log_rating'])

#printGameInfo()





# ----------------------------------------------------------------------------------------------------------------
# TAGS - GENRES & THEMES
# - Genres contain tags from both Genre & Sub-Genre categories
# - Themes contain tags from the Themes & Moods category
# - Documentation can be found at https://partner.steamgames.com/doc/store/tags
# ----------------------------------------------------------------------------------------------------------------

# Creating two separate lists of themes & genres to classify tags
genreList = []
themeList = []

# Method to parse text containing tags into lists
def addToList(tags):
    return tags.splitlines()

# Specifying all genres to include
genreList = addToList("""Action RPG
Action-Adventure
Arcade
Auto Battler
Automobile Sim
Base Building
Baseball
Basketball
Battle Royale
BMX
Board Game
Bowling
Building
Card Game
Character Action Game
Chess
Clicker
Cycling
Diplomacy
eSports
Experimental
Exploration
Farming Sim
Fighting
Football
God Game
Golf
Hacking
Hidden Object
Hockey
Idler
Interactive Fiction
Management
Match 3
Medical Sim
Mini Golf
Mining
MMORPG
MOBA
Motocross
Open World
Outbreak Sim
Party-Based RPG
Pinball
Platformer
Point & Click
Rhythm
Roguelike
RTS
Sandbox
Shooter
Skateboarding
Skating
Skiing
Snowboarding
Soccer
Space Sim
Stealth
Strategy RPG
Survival
Tennis
Tower Defense
Trivia
Turn-Based Strategy
Visual Novel
Walking Simulator
Word Game
Wrestling
2D Fighter
2D Platformer
3D Fighter
3D Platformer
4X
Action Roguelike
Arena Shooter
Beat 'em up
Bullet Hell
Card Battler
Choose Your Own Adventure
City Builder
Collectathon
Colony Sim
Combat Racing
CRPG
Dating Sim
Dungeon Crawler
Education
Flight
FPS
Grand Strategy
Hack and Slash
Heist
Hero Shooter
Horror
Immersive Sim
Investigation
JRPG
Life Sim
Looter Shooter
Metroidvania
Mystery Dungeon
On-Rails Shooter
Open World Survival Craft
Political Sim
Precision Platformer
Programming
Real Time Tactics
Roguelite
Roguevania
Runner
Shoot 'Em Up
Side Scroller
Sokoban
Solitaire
Souls-like
Spectacle fighter
Spelling
Survival Horror
Tactical RPG
Third-Person Shooter
Time Management
Top-Down Shooter
Trading
Trading Card Game
Traditional Roguelike
Turn-Based Tactics
Twin Stick Shooter
Typing
Wargame""")


# Specifying all themes to include
themeList = addToList("""1980s
1990's
Agriculture
Aliens
Alternate History
America
Atmospheric
Assassin
Bikes
Capitalism
Cats
Cold War
Comic Book
Conspiracy
Crime
Cyberpunk
Dark
Dark Fantasy
Demons
Destruction
Detective
Dinosaurs
Diplomacy
Dog
Dragons
Dynamic Narration
Economy
Education
Faith
Family Friendly
Fantasy
Foreign
Futuristic
Gambling
Game Development
Gothic
Heist
Historical
Horses
Illuminati
Investigation
Jet
Lemmings
LGBTQ+
Logic
Loot
Lovecraftian
Magic
Management
Mars
Mechs
Medieval
Memes
Military
Modern
Motorbike
Mystery
Mythology
Nature
Naval
Ninja
Offroad
Old School
Otome
Parkour
Philosophical
Pirates
Political
Politics
Pool
Post-apocalyptic
Programming
Retro
Robots
Romance
Rome
Satire
Science
Sci-fi
Sniper
Snow
Space
Stealth
Steampunk
Submarine
Superhero
Supernatural
Surreal
Survival
Swordplay
Tactical
Tanks
Thriller
Time Travel
Trains
Transhumanism
Transportation
Underground
Underwater
Vampire
War
Werewolves
Western
World War I
World War II""")



# Reformatting original DataFrame's tags from dictionary format to string using regex
# Example: "Casual": 49, "Arcade": 47, becomes "Casual, Arcade",
def processTags(tag):

    if isinstance(tag, dict):
        tag = str(tag)

    tagList = re.findall(r"'([^']+)'", tag)
    return tagList

# Applying reformatting method to df['tags'] column
df['tags'] = df['tags'].apply(lambda x: processTags(x) if isinstance(x, (str, dict)) else [])



# Creating appID column using DataFrame index (index is appID by default - just unnamed)
df['appID'] = df.index

# Creating two new DataFrames of genres and themes - both containing the appID & name field
df_genres = df[['appID', 'name']].copy()
df_themes = df[['appID', 'name']].copy()



# This method will append new columns onto the DataFrames for each theme & genre within their respective list.
# For each appID (game), if a tag is present its column will be set to True - else False
def oneHotEncoding():
    for theme in themeList:
        df_themes[theme] = df['tags'].apply(lambda tags: True if theme in tags else False)


    for genre in genreList:
        df_genres[genre] = df['tags'].apply(lambda tags: True if genre in tags else False)

oneHotEncoding()




# One-hot-encoding logarithmic review score number into categorical review bins - populating df_reviews

# Assigning bin thresholds and labels
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

bin_labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45', 
            '45-50', '50-55', '55-60', '60-65', '65-70', '70-75', '75-80', '80-85', '85-90', '90-95', '95-100']

# Creating a new column 'review_bin' with custom bins list
# pd.cut() will categorize the log rating value into an appropriate bin
# right=True & include_lowest=True match the format of bin labels
df['review_bin'] = pd.cut(df['log_rating'], bins=bins, labels=bin_labels, include_lowest=True, right=True)

# Using get_dummies to create additional columns for every bin in 'review_bin'
# This will one-hot-encode df['log_rating'] into a binary value for its corresponding review bin 
df_reviews = pd.get_dummies(df[['appID', 'name', 'review_bin']], columns=['review_bin'])





# Final DataFrame processing before association rule mining
# df_final will contain one-hot-encoded values for themes, genres, & review bin - required for association rule mining

# 1. df_tags is created, combining the results of one-hot-encoded df_themes & df_genres
df_tags = pd.concat([df_genres, df_themes], axis=1)

# 2. df_final is created, combining df_reviews with df_tags (created in step 1)
df_final = pd.concat([df_tags, df_reviews], axis=1)

# 3. The appID and name columns are dropped as they won't be included in association rule mining
df_final = df_final.drop(columns=['appID', 'name'])






# Generating itemsets for association rule mining using fpgrowth() method (mlxtend library)
print("Generating itemsets...")

# Minimum support of 0.0008 is equal to 25 instances
# total row count: 31752 * 0.008 = 25.4 (rounded down)
itemsets = fpgrowth(df_final, min_support=0.0008, use_colnames=True)

print("Generated itemsets.")




# Generating association rules using itemsets & association_growth*() method (mlxtend library)
print("Generating association rules...")

# Creates a new DataFrame containing association rules
# metric="confidence", min_threshold=0.5 only adds rules with a confidence of 50% or higher
rules = association_rules(itemsets, metric="confidence", min_threshold=0.5)

print("Generated association rules.")




# Creating two columns to build a strings out of each rule's antecedents and consequents
# By default antecedents and consequents are frozenstrings - this converts them into strings
rules['antecedents_str'] = rules['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
rules['consequents_str'] = rules['consequents'].apply(lambda x: ', '.join(sorted(list(x))))


# Creating 3 sets for themes, genres and reviews to determine length
# This allows each rule's antecedent and consequent to be checked for the presence of themes, genres & reviews
genres = set(df_genres.columns)
themes = set(df_themes.columns)
reviews = set(df_reviews.columns)


def contains_review(rule):
    
    # Creating sets of the antecedents and consequents
    antecedents = set(rule['antecedents'])
    consequents = set(rule['consequents'])


    #theme_count_antecedent = len(antecedents & themes)
    #genre_count_antecedent = len(antecedents & genres)
    review_count_antecedent = len(antecedents & reviews)

    #theme_count_consequent = len(consequents & themes)
    #genre_count_consequent = len(consequents & genres)
    #review_count_consequent = len(consequents & reviews)
    

    # Custom filters determining length of theme/review/genres
    # For example, the below if statement allows filtering of exact numbers of theme/genre/review in antecedent or consequent:
    #if theme_count_antecedent == 1 and genre_count_antecedent == 1 and review_count_consequent == 1:
    if review_count_antecedent > 0:
        return True
    return False


# Applying rule filtering to return only rules containing at least 1 review in antecedent
rules = rules[rules.apply(contains_review, axis=1)].reset_index(drop=True)





# Exporting DataFrames to .csv
rules.to_csv('rules.csv', index=False)
df_genres.to_csv('df_genres.csv', index=False)
df_themes.to_csv('df_themes.csv', index=False)
df_reviews.to_csv('df_reviews.csv', index=False)











# NOTE: DEPRECATED FEATURE
# The code below was used to generate the initial scatter graph.
# Scatter graph is now being generated in visualise.py

#fig = px.scatter(rules, x='support', y='confidence', color='lift', hover_data={"antecedents_str": True, "consequents_str": True, "lift": True})

# fig.update_traces(
#     hovertemplate="<b>Support:</b> %{x}<br>" +
#                   "<b>Confidence:</b> %{y}<br>" +
#                   "<b>Lift:</b> %{marker.color}<br>" +
#                   "<b>Antecedents:</b> %{customdata[0]}<br>" +
#                   "<b>Consequents:</b> %{customdata[1]}"
# )

# fig.show()




# NOTE: DEPRECATED FEATURE
# generateCombinations() creates a heatmap visualisation based on the (unprocessed) raw average review scores for each game
# All combinations of theme & genre are generated which are then given values based on the average review score of ALL games containing those themes/genres
def generateCombinations():
    
    # Generating combinations of all themes/genres
    combinations = [(theme, genre) for theme in themeList for genre in genreList]

    # Initializing variables to store results
    results = {}
    df_average_list = []

    # Changing orientation of DataFrames to dictionary for processing
    appID_genre_map = df_genres.set_index('appID').to_dict(orient='index')
    appID_theme_map = df_themes.set_index('appID').to_dict(orient='index')

    
    # Iterates over every existing record in dataset
    for appID in df['appID']:
        
        genres = {genre for genre, value in appID_genre_map.get(appID, {}).items() if value is True}
        themes = {theme for theme, value in appID_theme_map.get(appID, {}).items() if value is True}


        # Calculating the sum of review scores and amount of occurrences (for division to get average)
        rating_sum = df[df['appID'] == appID]['percent_positive'].sum()

        for theme, genre in combinations:
            if theme in themes and genre in genres:
                if (theme, genre) not in results:
                    results[(theme, genre)] = {'review_sum': 0, 'occurrences': 0}

                # Increments review sum & occurrences if a combination is found
                results[(theme, genre)]['review_sum'] += rating_sum
                results[(theme, genre)]['occurrences'] += 1

    # Calculating average review score based on occurrences
    for (theme, genre), data in results.items():
        review_average = data['review_sum'] / data['occurrences'] if data['occurrences'] > 0 else 0
        df_average_list.append({
            'theme': theme,
            'genre': genre,
            'review_average': round(review_average,2),
            'occurrences': data['occurrences']
        })

    
    # Creating df_vis for visulisation - needs to be reshaped to a pivot table
    df_vis = pd.DataFrame(df_average_list)
    pivot_df = df_vis[df_vis['occurrences'] > 10].pivot(index='genre', columns='theme', values='review_average')


    # Filtering occurrences to a minimum of 10 (so that averages aren't skewed by low occurrences)
    df_vis_filtered = df_vis[df_vis['occurrences'] > 10]

    # Re-pivoting table on genre index to display on heatmap
    pivot_df = df_vis_filtered.pivot(index='genre', columns='theme', values='review_average')
    
    
    # Specifying parameters for hover data to show on mouse-hover
    hoverdata = df_vis_filtered.pivot(index='genre', columns='theme', values='occurrences')
    hoverdata = hoverdata.fillna(0).round(0).astype(int)
    hoverdata_str = hoverdata.applymap(str)

    # Sorting heatmap values by highest average review score
    sorted_index = pivot_df.mean(axis=1).sort_values(ascending=True).index
    pivot_df = pivot_df.loc[sorted_index]
    hoverdata_str = hoverdata_str.loc[sorted_index]

    # Generating heatmap using themes, genres, and review count as parameters
    # Additional hover data has been included
    fig = go.Figure(go.Heatmap(
        x=pivot_df.columns,  
        y=pivot_df.index,   
        z=pivot_df.values,  
        hovertemplate=
        '<b>Theme: %{x}</b><br>' +
        'Genre: %{y}<br>' +
        'Average Review Score: %{z}%<br>' +
        'Occurrences: %{text}<br>',
        text=hoverdata_str.values,
        colorscale='rainbow'
    ))

    
    # Setting graph titles & user functionality
    fig.update_layout(title="Heatmap of Review Averages", width=1800, height=1800)
    fig.update_layout(dragmode="pan")
    fig.update_layout(transition={"duration": 0})
    fig.show(config={"scrollZoom": True})


#generateCombinations()