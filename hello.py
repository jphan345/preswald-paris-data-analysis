from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Paris 2024 Olympic Games Track & Field Results")

# Paris 2024 Olympic Games Track & Field Results CSV from:
# https://www.kaggle.com/datasets/laurenainsleyhaines/paris-2024-olympic-games-track-and-field-results
connect()
df = get_df('results_csv')

df = df.drop(["local_time", "startlist_url", "results_url", "summary_url", "points_url", "bib"], axis=1)
df = df.dropna()

# create table for results
text("## Paris 2024 Olympic Games Track & Field Results Table")
table(df)

medals_query = """
SELECT
    country,
    COUNT(CASE WHEN pos = 1.0 THEN 1 END) AS gold,
    COUNT(CASE WHEN pos = 2.0 THEN 1 END) AS silver,
    COUNT(CASE WHEN pos = 3.0 THEN 1 END) AS bronze,
    COUNT(CASE WHEN pos = 1 THEN 1 END) + COUNT(CASE WHEN pos = 2 THEN 1 END) + COUNT(CASE WHEN pos = 3 THEN 1 END) AS total
FROM
    results_csv
GROUP BY
    country;
"""

medals_data = query(medals_query, "results_csv")

# create table for medals
text("## Paris 2024 Olympic Games Track & Field Medals")
table(medals_data)

# plot geographical map
geo_fig = px.scatter_geo(medals_data,
                     locations='country',
                     size='total',
                     hover_name='country',
                     color='total',
                     title='Paris 2024 Olympic Games Track & Field Medals Map',
                     hover_data={
                         'gold': True,
                         'silver': True,
                         'bronze': True,
                         'total': True
                     })

plotly(geo_fig)

# medals_data_filtered = medals_data[medals_data['total'] > 0]
medals_data_sorted = medals_data.sort_values(by='total', ascending=False)

threshold = slider("Minimum Number of Medals to Show", min_val=0, max_val=100, default=20)
# plot stacked bar chart of medals
medals_bar_fig = px.bar(medals_data_sorted[medals_data_sorted['total'] >= threshold],
             x='country',
             y=['gold', 'silver', 'bronze'],
             title='Stacked Medals by Country',
             labels={'gold': 'Gold Medals', 'silver': 'Silver Medals', 'bronze': 'Bronze Medals'})

# fig.update_traces(marker=dict(color=['gold', 'silver', 'brown']))
plotly(medals_bar_fig)


text("## Additional Interesting Data")

# count of athletes per country
athlete_counts_query = """
SELECT
    country,
    COUNT(*) AS country_count
FROM
    results_csv
GROUP BY
    country
ORDER BY
    country_count DESC;
"""

athlete_counts = query(athlete_counts_query, "results_csv")
top_n_athletes = slider("Number of Countries to Display", min_val=5, max_val=athlete_counts.shape[0], default=20)

athlete_counts_bar_fig = px.bar(athlete_counts[:top_n_athletes],
             x='country',
             y="country_count",
             title='Number of Athletes per Country')

plotly(athlete_counts_bar_fig)

# event distribution ratio per country
participation_query = """
WITH country_event_counts AS (
    SELECT
        country,
        event,
        COUNT(*) AS event_count
    FROM
        results_csv
    GROUP BY
        country, event
),
country_total_counts AS (
    SELECT
        country,
        SUM(event_count) AS total_events
    FROM
        country_event_counts
    GROUP BY
        country
)
SELECT
    cec.country,
    cec.event,
    cec.event_count * 1.0 / ctc.total_events AS proportion
FROM
    country_event_counts cec
JOIN
    country_total_counts ctc
    ON cec.country = ctc.country
ORDER BY
    ctc.total_events DESC,
    cec.event;
"""

participation_data = query(participation_query, "results_csv")
num_events = participation_data['event'].nunique()
num_countries = participation_data['country'].nunique()

# table(participation_data)

# the dataframe consists of multiple entries of each country for each event but it is sorted from most popular country to least
# therefore get the top n unique countries instead of the top n rows
top_n_participation = slider("Number of Countries to Display", min_val=5, max_val=num_countries, default=20)
country_counts = participation_data['country'].value_counts()

top_countries = country_counts.head(top_n_participation).index
filtered_participation_data = participation_data[participation_data['country'].isin(top_countries)]

participation_bar_fig = px.bar(filtered_participation_data,
             x='country',
             y="proportion",
             color="event", 
             title='Event Distribution per Country (Ordered by amount of athletes)')
plotly(participation_bar_fig)













