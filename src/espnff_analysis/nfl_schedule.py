import os
import numpy as np
import pandas as pd
import pkg_resources as pkg
import io
import espnff_analysis


def mine_nfl_schedule(year_of_interest: int):
    """Mines pro-football

    Args:
        year_of_interest (_type_): _description_

    Returns:
        _type_: _description_
    """
    url = f"https://www.pro-football-reference.com/years/{year_of_interest}/games.htm"
    try:
        return pd.read_html(url)[0]
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_nfl_schedule(df, df_proteam_names):
    """_summary_

    Args:
        df (_type_): _description_
        df_proteam_names (pd DataFrame)

    Returns:
        _type_: _description_
    """

    df = df[["Week", "Date", "Winner/tie", "Loser/tie"]]
    df = pd.melt(
        df,
        id_vars=["Week", "Date"],
        value_vars=["Winner/tie", "Loser/tie"],
        var_name="Winner_Loser",
        value_name="Pro_team",
    )
    df = df.dropna(subset="Pro_team", axis=0)

    # handle special case of Washington, because the team name has changed over years
    df["Pro_team"] = df["Pro_team"].str.replace(
        pat=r"^Washington.*", repl="Washington", regex=True
    )
    # handle special case of Raiders, which has changed cities over years
    df["Pro_team"] = df["Pro_team"].str.replace(
        pat=r"^.*Raiders", repl="Raiders", regex=True
    )

    df["Pro_team_abbrev"] = df["Pro_team"].map(
        dict(zip(df_proteam_names["Pro Team Name"], df_proteam_names["Abbrev"]))
    )
    df = df[df["Pro_team"].isin(df_proteam_names["Pro Team Name"].tolist())]

    # weeks = [int(i) for i in df['Week'].unique().tolist() if i.isdigit()]
    # games_all_season = max(weeks)

    return df


def get_wideform_nfl_schedule(df):
    """_summary_

    Returns:
        _type_: _description_
    """

    weeks = [int(i) for i in df["Week"].unique().tolist() if i.isdigit()]
    games_all_season = max(weeks)

    df = df[df["Week"].isin([str(i) for i in weeks])]
    df = df.astype({"Week": int})
    # pivot NFL schedule to wideform
    df = df[["Week", "Date", "Pro_team_abbrev"]]
    df = df.rename(columns={"Pro_team_abbrev": "ProTeam"})
    df = df.pivot(index="Week", columns="ProTeam", values="Date")

    df = df.applymap(
        lambda x: pd.to_datetime(x, format="%Y-%m-%d") if not pd.isna(x) else x
    ).applymap(lambda x: pd.Timestamp(x) if not pd.isna(x) else x)

    try:
        assert (len(df.columns) == 32)
    except AssertionError:
        print(
            "All NFL team schedule does not contain 32 teams, check if team names from Pro-Football Reference match to team abbreviations list")

    return df


def get_team_abbrev():
    data_file = pkg.resource_string(
        espnff_analysis.__name__, "data/team_abbrev_conversion.csv"
    ).decode("utf-8")
    df_proteam_names = pd.read_csv(io.StringIO(data_file))
    return df_proteam_names


def get_nfl_schedule(
    year_of_interest,
    data_path=r"/Users/jonathancheng/PycharmProjects/espnff/espnff_analysis/data",
):
    """_summary_

    Args:
        year_of_interest (_type_): _description_
        data_path (regexp, optional): _description_. Defaults to r'/Users/jonathancheng/PycharmProjects/espnff/data'.

    Returns:
        _type_: _description_
    """

    # df_proteam_names = pd.read_csv(
    #     os.path.join(data_path, "team_abbrev_conversion.csv")
    # )
    df_proteam_names = get_team_abbrev()

    for col in df_proteam_names.columns:
        df_proteam_names[col] = df_proteam_names[col].str.strip()

    return (
        mine_nfl_schedule(year_of_interest=year_of_interest)
        .pipe(format_nfl_schedule, df_proteam_names)
        .pipe(get_wideform_nfl_schedule)
    )


def get_season_start_date(df):
    """
    Args:
        df: Wideform NFL schedule dataframe

    Returns: (datetime object) NFL season start date

    """
    return pd.melt(df)[~pd.melt(df)["value"].isin(["BYE"])]["value"].min()
