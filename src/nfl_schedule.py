import os
import pandas as pd


def mine_nfl_schedule(year_of_interest: int):
    """Mines pro-football

    Args:
        year_of_interest (_type_): _description_

    Returns:
        _type_: _description_
    """
    url = f'https://www.pro-football-reference.com/years/{year_of_interest}/games.htm'
    return pd.read_html(url)[0]


def format_nfl_schedule(df, df_proteam_names):
    """_summary_

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """

    df = df[['Week', 'Date', 'Winner/tie', 'Loser/tie']]
    df = pd.melt(df, id_vars=['Week', 'Date'], value_vars=['Winner/tie', 'Loser/tie'], var_name='Winner_Loser',
                 value_name='Pro_team')
    df['Pro_team_abbrev'] = df['Pro_team'].map(dict(zip(df_proteam_names['Pro Team Name'], df_proteam_names['Abbrev'])))
    df = df[df['Pro_team'].isin(df_proteam_names['Pro Team Name'].tolist())]

    # weeks = [int(i) for i in df['Week'].unique().tolist() if i.isdigit()]
    # games_all_season = max(weeks)

    return df


def get_wideform_nfl_schedule(df):
    """_summary_

    Returns:
        _type_: _description_
    """

    weeks = [int(i) for i in df['Week'].unique().tolist() if i.isdigit()]
    games_all_season = max(weeks)

    df = df[df['Week'].isin([str(i) for i in weeks])]
    df = df.astype({'Week': int})
    # pivot NFL schedule to wideform
    df = df[['Week', 'Date', 'Pro_team_abbrev']]
    df = df.pivot(index='Week', columns='Pro_team_abbrev', values='Date').fillna('BYE')
    df = df.applymap(lambda x: pd.to_datetime(x, format='%Y-%m-%d') if x != 'BYE' else x)
    return df


def get_nfl_schedule(year_of_interest,
                     data_path=r'/Users/jonathancheng/PycharmProjects/espnff/data'):
    """_summary_

    Args:
        year_of_interest (_type_): _description_
        data_path (regexp, optional): _description_. Defaults to r'/Users/jonathancheng/PycharmProjects/espnff/data'.

    Returns:
        _type_: _description_
    """

    df_proteam_names = pd.read_csv(os.path.join(data_path, 'team_abbrev_conversion.csv'))

    return (mine_nfl_schedule(year_of_interest=year_of_interest)
            .pipe(format_nfl_schedule, df_proteam_names)
            .pipe(get_wideform_nfl_schedule))
