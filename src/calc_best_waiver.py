import pandas as pd
from scipy import stats


def calculate_scoring_quantile_per_stint(stint, position, total_points_oneplayer, df_player_box_scores):
    df_allplayers_stint = df_player_box_scores[
        (df_player_box_scores['Position'] == position) & (df_player_box_scores['Week'].isin(stint))]
    total_position_stint = df_allplayers_stint.groupby(by=['Player']).agg({'Total points': 'sum'}).reset_index()[
        'Total points']
    quantile = stats.percentileofscore(total_position_stint.values, total_points_oneplayer)
    return quantile