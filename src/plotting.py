import pandas as pd
import altair as alt


def scatterplot_acquisitions(df_stints, position, acq_by_draft):
    df = df_stints.groupby(by=['Drafted', 'Position']).get_group((acq_by_draft, position))

    if acq_by_draft:
        status = 'Draft'
    else:
        status = 'Waiver'

    plot_title = f'Position: {position} , Acquired by: {status}'
    selection = alt.selection_multi(fields=['Team'], bind='legend')

    color = alt.condition(selection,
                          alt.Color('Team:N',
                                    scale=alt.Scale(scheme='tableau20'), ),
                          alt.value('lightgray'))

    chart = alt.Chart(df).mark_circle(size=40).encode(
        alt.X('Bid Amount ($)', axis=alt.Axis(grid=False)),
        alt.Y('Total points per stint', axis=alt.Axis(grid=False)),
        color=color,
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        tooltip=['Player', 'Team', 'Bid Amount ($)', 'Total points per stint']
    ).add_selection(selection).properties(
        width=450,
        height=450,
        title=plot_title
    ).configure_axis(
        labelFontSize=18,
        titleFontSize=18
    ).configure_title(fontSize=20).configure_legend(labelFontSize=14, titleFontSize=14)
    return plot_title, chart
