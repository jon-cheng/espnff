import os
import datetime
import numpy as np
import pandas as pd
from espn_api.football import League
from espn_api.football import activity


def fetch_espn_api(league_id, year, espn_s2, swid):
    """Uses espn_api to fetch league data

    Args:
        league_id (_type_): ESPN League ID
        year (_type_): Year of season of interest
        espn_s2 (_type_): _description_
        swid (_type_): _description_

    Returns:
    """
    return League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)


# def get_recent_activity(league):
#     """ .recent_activity() argument is arbitrary large number
#     Args:
#         league: League object
#
#     Returns:
#         list: recent activity list generated by espn_api
#     """
#     return league.recent_activity(100000000)


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
        action1 = 'TRADE ADDED'

        # Build a second tuple for TRADE DROPPED
        action2 = 'TRADE DROPPED'

        acq_data1 = (date_of_acq, player_id, ProTeam, team_id_received, action1, bid_amount)
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
            if action1 == 'TRADED':
                ls = get_trade_data(action, date_of_acq)
            else:
                ls = get_waiver_data(action, date_of_acq)
        acq_data_ls.append(ls)

    return flatten_list(acq_data_ls)


def build_df_acq(acq_data_flat_ls):
    df_acq = pd.DataFrame(acq_data_flat_ls)
    df_acq.columns = ['Timestamp', 'Player', 'ProTeam', 'Team', 'Action', 'Bid Amount ($)']
    # converts from milliseconds to date
    def convert_to_date(date_of_acq):
        d2 = datetime.date.fromtimestamp(date_of_acq / 1000.0)
        return d2

    df_acq['Action Timestamp'] = df_acq['Timestamp'].apply(lambda x: convert_to_date(x))

    return df_acq.sort_values(by=['Timestamp'], ascending=True)


def build_df_draft(league):
    """
    Generates Draft DataFrame
    Args:
        league:

    Returns:
        (pd DataFrame):

    """
    draft_ls = [(pick.playerName, pick.team.team_name, 'DRAFT ADDED', pick.bid_amount) for pick in league.draft]
    return pd.DataFrame(draft_ls, columns=['Player', 'Acquired by', 'Action', 'Bid Amount ($)'])


def build_df_rostered(league):
    """
    Get data of all currently fantasy league rostered players

    Args:
        league:

    Returns: all rostered players dataframeg

    """
    rostered_players_ls = [(player.name, player.position, player.proTeam, player.total_points, team.team_name)
                           for team in league.teams
                           for player in team.roster]
    return pd.DataFrame(rostered_players_ls,
                        columns=['Player' , 'Position' , 'Pro Team', 'Total points', 'Current Team'])


def build_df_FA(league):
    """

    Args:
        league:

    Returns:
        (pd DataFrame): free agents dataframe

    """
    FA_players_ls = [(free_agent.name, free_agent.position, free_agent.proTeam, free_agent.total_points, 'Free agent')
                     for free_agent in league.free_agents(size=1000000)
                     ]

    return pd.DataFrame(FA_players_ls,
                         columns=['Player', 'Position', 'Pro Team', 'Total points', 'Current Team'])
