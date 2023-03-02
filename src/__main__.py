import nfl_schedule as ns

if __name__ == "__main__":
    df_final = ns.get_nfl_schedule(2022)
    print(df_final)
