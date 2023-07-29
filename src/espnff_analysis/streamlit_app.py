import os
import pandas as pd
import numpy as np
import streamlit as st
from espnff_analysis.plotting import scatterplot_acquisitions

path = '/Users/jonathancheng/PycharmProjects/espnff/results'

years_of_interest = tuple([str(i) for i in list(range(2019,2023,1))[::-1]])
year = st.selectbox(
    'NFL Season',
    years_of_interest)

df_stints = pd.read_csv(os.path.join(path,f'df_stints_{year}.csv'),index_col=0)

st.header("Draft Return-on-Investment")
positions = ['FLEX','QB','RB','WR','TE','K','D/ST']
tabs = st.tabs(positions)
for position,tab in zip(positions,tabs):
    if position == 'FLEX':
        with tab:
            # st.header('FLEX')
            plot_title, chart = scatterplot_acquisitions(df_stints, select_acq_method=[True])
            st.altair_chart(chart, use_container_width=True)
    else:
        with tab:
            # st.header(position)
            plot_title, chart = scatterplot_acquisitions(df_stints, select_acq_method=[True], select_positions=[position])
            st.altair_chart(chart, use_container_width=True)

st.header("Waiver Return-on-Investment")
tabs = st.tabs(positions)
for position,tab in zip(positions,tabs):
    if position == 'FLEX':
        with tab:
            st.header('FLEX')
            plot_title, chart = scatterplot_acquisitions(df_stints, select_acq_method=[False])
            st.altair_chart(chart, use_container_width=True)
    else:
        with tab:
            st.header(position)
            plot_title, chart = scatterplot_acquisitions(df_stints, select_acq_method=[False], select_positions=[position])
            st.altair_chart(chart, use_container_width=True)

st.write("We wanted to find the best waiver (un-drafted) player from past seasons in order to give the award for Best Waiver Player of the Year.")
st.write(""
         "#Assumptions and methods:"
         "- Only QB, RB, WR, TE are eligible"
         "- Player must not have been drafted "
         "- Since we are comparing across different positions, we need to normalize scoring across positions. For example, in our scoring system, QBs vastly outscore other positions, so that bias must be normalized against. A better metric of value of a given player is how the fantasy player compares against his position. "
         "- One normalization method is z-score, which is mean and standard deviation-dependent. However, z-scores don't work well with non-normal distributions. Here, we've found the scoring data to be skewed."
         "- A better choice for normalization is quantile, which is agnostic to the underlying distribution."
         "- We calculated the quantile of fantasy scoring of the given player versus his position for the given weeks that he was on a particular fantasy team. The accounting for \"stint\" on a given fantasy team then gives an idea of the return-on-investment for a given fantasy team / fantasy player pairing.Note that non-continuous stints for the fantasy team / player pairings are merged.")

st.write("- bullet 1")
st.write(">  - bullet 2")
st.write(">>  - bullet 2")

