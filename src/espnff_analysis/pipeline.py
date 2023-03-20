import nfl_schedule as nf
import ff_league_data as ff
# import calc_best_waiver as calc


def get_nfl_schedule_info(year_of_interest):
    df_proteam_schedule = nf.get_nfl_schedule(year_of_interest)
    season_start_date = nf.get_season_start_date(df_proteam_schedule)
    return df_proteam_schedule, season_start_date


def fetch_league_data(league_id, year, espn_s2, swid):
    """
    Fetches ESPN Fantasy Football League data using espn_api

    Args:
        league_id:
        year:
        espn_s2:
        swid:

    Returns:

    """
    league = ff.fetch_espn_api(league_id, year, espn_s2, swid)
    activity_ls = ff.try_get_league_activity(league)
    wk_ls = ff.get_weeks(league)
    return league, activity_ls, wk_ls


def get_acquisitions_data(activity_ls):
    """
    Fetch league data, wrangle into acquisitions DataFrame
    Args:
        activity_ls:

    Returns:

    """
    acq_data_flat_ls = ff.get_acq_ls(activity_ls)
    df_acq = ff.build_df_acq(acq_data_flat_ls)
    return df_acq


def main_pipeline(league_id, year, espn_s2, swid):
    df_proteam_schedule, season_start_date = get_nfl_schedule_info(year)
    league, activity_ls, wk_ls = fetch_league_data(league_id, year, espn_s2, swid)
    df_acq = get_acquisitions_data(activity_ls)
    df_draft, drafted_players = ff.build_df_draft(league)
    df_rostered = ff.build_df_rostered(league)
    df_FA = ff.build_df_FA(league)
    # Generate all player stats dataframe, including all Free Agents
    df_player_stats = ff.build_df_player_stats(df_rostered, df_FA)
    df_draft_stats = ff.build_df_draft_stats(df_draft, df_player_stats)
    df_acq_stats = ff.build_df_acq_stats(df_acq, df_player_stats)
    df_acq_final = ff.build_df_acq_final(season_start_date, df_draft_stats, df_acq_stats, drafted_players)
    # Get player_box_scores from fantasy season
    df_player_box_scores = ff.build_df_player_box_scores(league, wk_ls)
    df_stints = ff.build_df_stints(df_acq_final, df_proteam_schedule, df_player_stats, drafted_players,
                                   df_player_box_scores)
    df_stints['Total points per stint'] = df_stints.apply(
        lambda x: ff.get_total_pts_per_player(x['Player'], x['Stint (wks)'], df_player_box_scores), axis=1).fillna(0)

    return df_stints










