import pandas as pd
import altair as alt


def scatterplot_acquisitions(df_stints, select_acq_method=None, select_positions=None):
    if select_acq_method is None:
        select_acq_method = [True]

    if select_positions is None:
        select_positions = ['RB', 'WR', 'TE']

    g = df_stints.groupby(by=["Drafted", "Position"])

    df = pd.concat([g.get_group((acq_by_draft, position))
                    for acq_by_draft in select_acq_method
                    for position in select_positions], axis=0)

    if select_acq_method[0]:
        status = "Draft"
    else:
        status = "Waiver"

    positions = ', '.join(select_positions)

    plot_title = f"Position: {positions} , Acquired by: {status}"
    selection = alt.selection_multi(fields=["Team"], bind="legend")

    color = alt.condition(
        selection,
        alt.Color(
            "Team:N",
            scale=alt.Scale(scheme="tableau20"),
        ),
        alt.value("lightgray"),
    )

    chart = (
        alt.Chart(df)
        .mark_circle(size=40)
        .encode(
            alt.X("Bid Amount ($)", axis=alt.Axis(grid=False)),
            alt.Y("Total points per stint", axis=alt.Axis(grid=False)),
            color=color,
            opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
            tooltip=["Player", "Team", "Bid Amount ($)", "Total points per stint"],
        )
        .add_selection(selection)
        .properties(width=450, height=450, title=plot_title)
        .configure_axis(labelFontSize=18, titleFontSize=18)
        .configure_title(fontSize=20)
        .configure_legend(labelFontSize=14, titleFontSize=14)
    )
    return plot_title, chart
