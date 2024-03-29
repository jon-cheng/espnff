import os
import datetime as dt
import itertools
import retry
import requests
import numpy as np
import pandas as pd
from espn_api.football import League


def fetch_espn_api(league_id, year, espn_s2, swid):
    """Uses espn_api to fetch league data

    Args:
        league_id (_type_): ESPN League ID
        year (_type_): Year of season of interest
        espn_s2 (_type_): _description_
        swid (_type_): _description_

    Returns: league object on which further data parsing can be applied upon
    """
    return League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)


@retry.retry(tries=10, delay=3)
def get_league_activity(league, n_iter=1000000):
    return league.recent_activity(n_iter)


def try_get_league_activity(league):
    try:
        print("Fetching league data from espn_api ...")
        return get_league_activity(league)
    except requests.exceptions.Timeout:
        raise ConnectionError(
            "The request timed out. Could not fetch league data, try re-running the program."
        )
    # except requests.exceptions.ConnectionError:
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not fetch league data, try re-running the program."
        )
    except requests.exceptions.RequestException:
        raise ConnectionError(
            "An unknown error occurred. Could not fetch league data, try re-running the program."
        )


def get_weeks(league):
    """Constructs a weeks list up to the current week
    # league object has attribute current week, this will always update from the ESPN API
    # construct a reverse dictionary to map to box_score index

    """
    return [i + 1 for i in range(league.current_week)]


def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


# Function handling trade data


def get_trade_data(action, date_of_acq):
    "Function for parsing Recent Activities trade data into ADD and DROP events"

    acq_data_ls = []

    team_transaction_ls = []

    for k in action.actions:
        (team1, action1, _, _) = k
        team_id = team1.team_name
        team_transaction_ls.append(team_id)

        # determine if trade or waiver acquisition type

    # establish other team involved in trade
    teams_in_trade = list(set(team_transaction_ls))

    for k in action.actions:
        (team1, action1, player_name, bid_amount) = k
        team_id = team1.team_name

        if teams_in_trade.index(team_id) == 1:
            team_id_received = teams_in_trade[0]
        else:
            team_id_received = teams_in_trade[1]

        # Build new tuple for TRADE ADDED
        player_id = player_name.name
        ProTeam = player_name.proTeam
        action1 = "TRADE ADDED"

        # Build a second tuple for TRADE DROPPED
        action2 = "TRADE DROPPED"

        acq_data1 = (
            date_of_acq,
            player_id,
            ProTeam,
            team_id_received,
            action1,
            bid_amount,
        )
        drop_data1 = (date_of_acq, player_id, ProTeam, team_id, action2, bid_amount)

        acq_data_ls.append(acq_data1)
        acq_data_ls.append(drop_data1)

    return acq_data_ls


# Function handling waiver data
def get_waiver_data(action, date_of_acq):
    waiver_data_ls = []

    for k in action.actions:
        (team1, action1, player_name, bid_amount) = k
        team_id = team1.team_name
        player_id = player_name.name
        proteam = player_name.proTeam

        waiver_data1 = (date_of_acq, player_id, proteam, team_id, action1, bid_amount)
        waiver_data_ls.append(waiver_data1)

    return waiver_data_ls


def get_acq_ls(activity_ls):
    acq_data_ls = []

    # loop through each activity item
    for idx, action in enumerate(activity_ls):
        date_of_acq = action.date
        team_transaction_ls = []
        for k in action.actions:
            (team1, action1, _, _) = k
            team_id = team1.team_name
            team_transaction_ls.append(team_id)

            # determine if trade or waiver acquisition type
            ls = []
            if action1 == "TRADED":
                ls = get_trade_data(action, date_of_acq)
            else:
                ls = get_waiver_data(action, date_of_acq)
        acq_data_ls.append(ls)

    return flatten_list(acq_data_ls)


def build_df_acq(acq_data_flat_ls):
    df_acq = pd.DataFrame(acq_data_flat_ls)
    df_acq.columns = [
        "Timestamp",
        "Player",
        "ProTeam",
        "Team",
        "Action",
        "Bid Amount ($)",
    ]
    # converts from milliseconds to date
    def convert_to_date(date_of_acq):
        d2 = dt.date.fromtimestamp(date_of_acq / 1000.0)
        return d2

    df_acq["Action Timestamp"] = df_acq["Timestamp"].apply(lambda x: convert_to_date(x))
    df_acq = df_acq.sort_values(by=["Timestamp"], ascending=True)
    return df_acq


def build_df_draft(league):
    """
    Generates Draft DataFrame
    Args:
        league:

    Returns:
        (pd DataFrame):

    """
    draft_ls = [
        (pick.playerName, pick.team.team_name, "DRAFT ADDED", pick.bid_amount)
        for pick in league.draft
    ]
    df_draft = pd.DataFrame(
        draft_ls, columns=["Player", "Acquired by", "Action", "Bid Amount ($)"]
    )

    drafted_players = df_draft["Player"].tolist()

    return df_draft, drafted_players


def build_df_rostered(league):
    """
    Get data of all currently fantasy league rostered players

    Args:
        league:

    Returns: all rostered players dataframeg

    """
    rostered_players_ls = [
        (
            player.name,
            player.position,
            player.proTeam,
            player.total_points,
            team.team_name,
        )
        for team in league.teams
        for player in team.roster
    ]
    df_rostered = pd.DataFrame(
        rostered_players_ls,
        columns=["Player", "Position", "Pro Team", "Total points", "Current Team"],
    )
    return df_rostered


def build_df_FA(league):
    """

    Args:
        league:

    Returns:
        (pd DataFrame): free agents dataframe

    """
    FA_players_ls = [
        (
            free_agent.name,
            free_agent.position,
            free_agent.proTeam,
            free_agent.total_points,
            "Free agent",
        )
        for free_agent in league.free_agents(size=1000000)
    ]

    df_FA = pd.DataFrame(
        FA_players_ls,
        columns=["Player", "Position", "Pro Team", "Total points", "Current Team"],
    )
    return df_FA


def build_df_player_stats(df_rostered, df_FA):
    """Join the rostered and free agent player universes to get all player stats
    If a player is eligible for multiple positions, function ensures de-duplication of player records"""
    df_player_stats = pd.concat([df_rostered, df_FA], axis=0)
    df_player_stats = df_player_stats.sort_values(by='Total points', ascending=False) \
        .drop_duplicates(subset='Player')
    return df_player_stats


def build_df_draft_stats(df_draft, df_player_stats):
    """Merge draft data with player stats fields"""
    df_draft_stats = (
        df_draft.merge(df_player_stats, how="left")
        .dropna(axis=0)
        .rename(columns={"Pro Team": "ProTeam", "Acquired by": "Team"})
    )
    return df_draft_stats


def build_df_acq_stats(df_acq, df_player_stats):
    """Merge acquisitions data with player stats fields"""
    df_acq_stats = df_acq.merge(df_player_stats, how="left").drop(["Pro Team"], axis=1)
    return df_acq_stats


def build_df_acq_final(season_start_date, df_draft_acq, df_acq, drafted_players):
    """Merges draft AND waiver acquisitions dataframe to generate master acquisitions dataframe

    Args:
        season_start_date:
        df_draft_acq:
        df_acq:

    Returns:

    """
    draft_time = dt.datetime.strptime(
        (season_start_date - dt.timedelta(days=1)).strftime("%d %b %Y"), "%d %b %Y"
    )

    df_draft_acq["Action Timestamp"] = draft_time.date()
    df_draft_acq["Timestamp"] = int(draft_time.timestamp() * 1000)

    df_acq_final = pd.concat([df_draft_acq, df_acq], axis=0)

    # df['name'].apply(lambda x: 'John Smith' if x.str.contains('John') else 'Other')

    # df_acq_final.loc[df_acq_final['Action'].str.contains('ADDED'), 'Added_Dropped'] = 'ADDED'
    # df_acq_final.loc[~df_acq_final['Action'].str.contains('ADDED'), 'Added_Dropped'] = 'DROPPED'

    df_acq_final["Added_Dropped"] = df_acq_final["Action"].apply(
        lambda x: "ADDED" if "ADDED" in x else "DROPPED"
    )

    df_acq_final.loc[df_acq_final["Player"].isin(drafted_players), "Drafted"] = True
    df_acq_final.loc[~df_acq_final["Player"].isin(drafted_players), "Drafted"] = False

    # TODO: build a feature to handle real life free agents, example: Derek Carr in 2022
    # can use nfl_py players database for extracting players' last team within season of interest
    # For now, drop players who were rostered, but are not on a ProTeam currently
    # (i.e. players who were waived in a real life team)
    # There can be a next feature to handle these exceptions
    df_acq_final = df_acq_final[~(df_acq_final["ProTeam"] == "None")]

    return df_acq_final


def build_df_player_box_scores(league, wk_ls):
    """

    Args:
        league:
        wk_ls:

    Returns:

    """
    dfs = []
    for wk in wk_ls:
        rows = []
        for matchup in league.box_scores(wk):
            if matchup.away_team == 0:
                team_name_q = matchup.home_team.team_name
                for q in matchup.home_lineup:
                    row = [q.name, q.position, wk, team_name_q, q.points]
                    rows.append(row)
            else:
                team_name_p = matchup.away_team.team_name
                team_name_q = matchup.home_team.team_name
                for p in matchup.away_lineup:
                    row = [p.name, p.position, wk, team_name_p, p.points]
                    rows.append(row)
                for q in matchup.home_lineup:
                    row = [q.name, q.position, wk, team_name_q, q.points]
                    rows.append(row)
        df = pd.DataFrame(
            rows, columns=["Player", "Position", "Week", "Team", "Total points"]
        )
        dfs.append(df)

    df_player_box_scores = pd.concat(dfs, ignore_index=True)
    return df_player_box_scores


def get_df_test_acq_bid(df_test_acq):
    """

    Args:
        df_test_acq:

    Returns:

    """
    df_test_acq_bid = df_test_acq.copy()
    df_test_acq_bid = df_test_acq_bid.rename(columns={"Action Timestamp": "Added"})
    df_test_acq_bid = df_test_acq_bid[["Player", "Team", "Bid Amount ($)", "Added"]]
    return df_test_acq_bid


def pivot_df_acq_oneplayer(df_test_acq):
    """

    Args:
        df_test_acq:

    Returns:

    """
    df_test_acq = df_test_acq.reset_index(drop=True)
    df_test_acq = df_test_acq[
        ["Player", "Team", "Position", "ProTeam", "Total points", "Action Timestamp", "Added_Dropped"]
    ]

    # in corner cases where a player is eligible for multiple positions,
    # then take the max (first) highest Total points,
    # usually the alternative position is 0 as an artifact from espn_api
    df_test_acq_dedup = df_test_acq.groupby(by=['Player', 'Team', 'Action Timestamp']).agg(
        {'Total points': 'first'}).reset_index()
    df_test_acq = df_test_acq_dedup.merge(df_test_acq)
    df_test_acq = df_test_acq.sort_values(by="Action Timestamp", ascending=True)

    index_ls = list(range(df_test_acq.shape[0]))

    df_test_acq["Action_GroupId"] = list(
        itertools.chain(*[2 * [i] for i in list(range(df_test_acq.shape[0]))])
    )[: len(index_ls)]

    df_test_acq = df_test_acq.drop(['Total points', 'Position'], axis=1)

    # TODO: fix pivot error, test on 2019 data, use pivot_table as fix
    df_test_acq = (
        df_test_acq.pivot(
            index=["Player", "Team", "ProTeam", "Action_GroupId"],
            columns="Added_Dropped",
        )
        .reset_index()
        .sort_values(by="Action_GroupId")
    )

    df_test_acq.columns = [
        f"{i}|{j}" if j != "" else f"{i}" for i, j in df_test_acq.columns
    ]

    df_test_acq = df_test_acq.rename(
        columns={
            "Action Timestamp|ADDED": "Added",
            "Action Timestamp|DROPPED": "Dropped",
        }
    )

    return df_test_acq


# get stints on each fantasy team


def get_stints(proteam, added, dropped, df_proteam_schedule):
    """Function that maps add, drop dates, NFL team-specific schedule, to the weeks that the fantasy player was
    on a given fantasy team

    Args:
        proteam:
        added:
        dropped:
        df_proteam_schedule:

    Returns:
        stint_ls (list): weeks on given fantasy team, excluding BYE weeks

    """
    proteam_schedule = df_proteam_schedule[proteam]
    if pd.isna(dropped):
        stint_ls = proteam_schedule[(proteam_schedule >= added)].keys().tolist()
    else:
        stint_ls = (
            proteam_schedule[(proteam_schedule >= added) & (proteam_schedule < dropped)]
            .keys()
            .tolist()
        )
    return stint_ls


def build_df_stints(
    df_acq_final,
    df_proteam_schedule,
    df_player_stats,
    drafted_players,
    df_player_box_scores,
):
    """
    Wrapper to construct master stints dataframe
    Args:
        df_acq_final:
        df_proteam_schedule:

    Returns:

    """
    g = df_acq_final.groupby(by=["Player"])
    df_ls = []
    for key in list(g.groups.keys()):
        df_test_acq = g.get_group(key)
        df_test_acq_bid = get_df_test_acq_bid(df_test_acq)
        df_test_acq = (
            pivot_df_acq_oneplayer(df_test_acq)
            .merge(df_test_acq_bid, how="left")
            .drop(["Action_GroupId"], axis=1)
        )
        df_ls.append(df_test_acq)

    df_stints = pd.concat(df_ls, axis=0)

    df_stints["Added"] = df_stints["Added"].apply(
        lambda x: pd.Timestamp(x) if not pd.isna(x) else x
    )
    df_stints["Dropped"] = df_stints["Dropped"].apply(
        lambda x: pd.Timestamp(x) if not pd.isna(x) else x
    )

    df_stints["Stint (wks)"] = df_stints.apply(
        lambda x: get_stints(
            x["ProTeam"], x["Added"], x["Dropped"], df_proteam_schedule
        ),
        axis=1,
    )

    df_stints["Position"] = df_stints["Player"].map(
        dict(zip(df_player_stats["Player"], df_player_stats["Position"]))
    )

    # set index on each stint event
    df_stints = (
        df_stints.reset_index()
        .reset_index()
        .rename(columns={"level_0": "Stint_id"})
        .drop("index", axis=1)
    )

    df_stints.loc[df_stints["Player"].isin(drafted_players), "Drafted"] = True
    df_stints["Drafted"] = df_stints["Drafted"].fillna(False)

    def adjust_stints_to_fantasy_schedule(stint, df_player_box_scores):
        fantasy_weeks = df_player_box_scores["Week"].unique().tolist()
        return list(set(fantasy_weeks) & set(stint))

    df_stints["Stint (wks)"] = df_stints.apply(
        lambda x: adjust_stints_to_fantasy_schedule(
            x["Stint (wks)"], df_player_box_scores
        ),
        axis=1,
    )

    return df_stints


def build_df_points_scored(df_stints, df_player_box_scores):
    df_stints_long = df_stints.explode(["Stint (wks)"])
    df_stints_long = df_stints_long.rename(columns={"Stint (wks)": "Week"})
    df_points_scored = df_stints_long.merge(df_player_box_scores, how="inner")
    total_pts = pd.DataFrame(
        data=df_points_scored.groupby(by="Stint_id")["Total points"].agg(sum)
    ).reset_index()
    return df_stints_long, total_pts


def merge_total_pts_with_df_stints(df_stints, total_pts):
    df_stints = df_stints.merge(total_pts)
    return df_stints


def build_df_waiver(df_stints):
    df_waiver = df_stints[~df_stints["Drafted"]]
    return df_waiver


def get_total_pts_per_player(player, stint, df_player_box_scores):
    if stint:
        g = df_player_box_scores.groupby(by="Player")
        df = g.get_group(player)
        return df[df["Week"].isin(stint)]["Total points"].sum()


def adjust_stints_to_fantasy_schedule(stint, df_player_box_scores):
    fantasy_weeks = df_player_box_scores["Week"].unique().tolist()
    return list(set(fantasy_weeks) & set(stint))
