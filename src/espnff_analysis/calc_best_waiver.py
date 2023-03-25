import itertools
import pandas as pd
from scipy import stats


def merge_lists(series):
    return list(set([item for sublist in series for item in sublist]))


def calculate_scoring_quantile_per_stint(
    stint, position, total_points_oneplayer, df_player_box_scores
):
    df_allplayers_stint = df_player_box_scores[
        (df_player_box_scores["Position"] == position)
        & (df_player_box_scores["Week"].isin(stint))
    ]
    total_position_stint = (
        df_allplayers_stint.groupby(by=["Player"])
        .agg({"Total points": "sum"})
        .reset_index()["Total points"]
    )
    quantile = stats.percentileofscore(
        total_position_stint.values, total_points_oneplayer
    )
    return quantile


def get_quantile(df, df_player_box_scores):
    for idx, x in df.iterrows():
        if x["Stint (wks)"]:
            df.loc[idx, "quantile"] = calculate_scoring_quantile_per_stint(
                x["Stint (wks)"],
                x["Position"],
                x["Total points per stint"],
                df_player_box_scores,
            )
        else:
            df.loc[idx, "quantile"] = 0
    return df


def build_df_player_ffteam(df_stints):
    df_agg_stints = (
        df_stints.groupby(by=["Player", "Team"])
        .agg({"Total points per stint": "sum", "Stint (wks)": list})
        .reset_index()
    )
    df_agg_stints["Stint (wks)"] = df_agg_stints["Stint (wks)"].apply(
        lambda x: list(itertools.chain(*x))
    )
    df_player_ffteam = df_agg_stints.merge(
        df_stints[
            ["Player", "Team", "ProTeam", "Position", "Drafted"]
        ].drop_duplicates(),
        how="left",
    )
    return df_player_ffteam


def get_num_weeks_of_stint(df):
    df["Num weeks"] = df["Stint (wks)"].apply(lambda x: len(x))
    return df


def get_quantile_and_weeks(df_stints, df_player_box_scores):
    """

    Args:
        df_stints:
        df_player_box_scores:

    Returns:

    """
    df_player_ffteam = build_df_player_ffteam(df_stints)

    ls = []
    for df in [df_stints, df_player_ffteam]:
        df = get_num_weeks_of_stint(df)
        df = get_quantile(df, df_player_box_scores)
        ls.append(df)

    [df_stints, df_player_ffteam] = ls
    return df_stints, df_player_ffteam


def get_waiver_data(df_player_ffteam, week_threshold=8):
    """Gets stats on players who were undrafted, rank on total performance throughout their per fantasy player-stint"""
    df_waiver = (
        df_player_ffteam[
            (~df_player_ffteam["Drafted"])
            & (df_player_ffteam["Num weeks"] >= week_threshold)
            & (df_player_ffteam["Position"].isin(["QB", "RB", "WR", "TE"]))
        ]
        .sort_values(by="quantile", ascending=False)
        .reset_index(drop=True)
    )
    return df_waiver
