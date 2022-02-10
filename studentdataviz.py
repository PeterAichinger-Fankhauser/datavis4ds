import pandas as pd
import numpy as np
import plotly.express as px
# import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

max_semesters_to_display = 8
df_raw = pd.read_csv("student_dummy_data.csv", delimiter=";", encoding="latin-1", decimal=",")
df_reduced = df_raw.loc[df_raw["besuchtesSemester"] <= max_semesters_to_display]
df_by_semester_and_study_grps = df_reduced.groupby(["besuchtesSemester", "STUDBEZ_kompakt"])
df_by_semester_and_study_agg = df_by_semester_and_study_grps["ECTS_Sem"].agg(["mean", "median"])
df_by_semester_and_study_agg = pd.DataFrame(df_by_semester_and_study_agg).reset_index()

def create_lineplot_annotations_y(dataframe, 
                                    max_sem_in_plot,
                                    y_variable="mean", 
                                    group_variable="STUDBEZ_kompakt"):

    """
    This function creates y labels based on 'group_variable' for a line plot. 
    The labels are positioned at the height of the right-most y value.
    """
    y_heights = dataframe.loc[dataframe["besuchtesSemester"]==\
        max_sem_in_plot][[y_variable, group_variable]]
    y_heights = y_heights.sort_values(by=y_variable, ascending=False)

    # todo: if twp labels would overlap they should be shifted vertically

    y_heights_mean = list(y_heights[y_variable])
    y_heights_labs = list(y_heights[group_variable])

    ants = []

    for i in range(0,len(y_heights_labs)):
        ants.append(dict(xref='paper', 
                        x=1, 
                        y=round(y_heights_mean[i]),
                        xanchor='left', yanchor='middle',
                        text=y_heights_labs[i],
                        font={"family": "Arial", 
                        "size": 12},
                        showarrow=False))
    return(y_heights, ants) # list of annotation dicts

    """
current best product
"""
app = Dash(__name__)
server=app.server

df = df_by_semester_and_study_agg.copy()

available_indicators = df["STUDBEZ_kompakt"].unique()


## ----------------------- LAYOUT -----------------------


app.layout = html.Div(
    style={'backgroundColor': 'white'},
    children=[
    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns",
                children=[
                    html.H1("Dash-Versuch für Studierendenstatistik", style={"text-align": "center"}),
                    html.Br(), 
                    html.Br(), 
                    html.B("Auswahl Studiengang"),
                    dcc.Dropdown(id="slct_study",
                                options=[
                                        {"label": i, "value": i} for i in available_indicators],
                                #  options=[
                                #      {"label": "BA; PPP", "value": "BA; PPP"},
                                #      {"label": "MA; PPP", "value": "MA; PPP"},
                                #      {"label": "BA; BI", "value": "BA; BI"},
                                #      {"label": "MA; BI", "value": "MA; BI"}],
                                multi=False,
                                value="BA; PPP",
                                style={"width": "100%"}
                    ),
                    html.Br(),
                    html.Div(id="output_container_1", children=[]),
                    html.Br(),
                    html.Br(),
                    html.B("Auswahl des angezeigten Durchschnittsmaßes"),

                    dcc.RadioItems(
                                    id="measure", # was xaxis-type
                                    options=[{"label": i, 'value': i} for i in ["mean", "median"]],
                                    value="mean",
                                    labelStyle={"display": "inline-block"}, 
                                    #style={"width": "100%"},
                    ),
                    
                    html.Br(),
                    
                    html.B("Auswahl der angezeigten Semester"),

                    dcc.Slider(
                                id="max_semester_slider", # was year--slider
                                min=df["besuchtesSemester"].min(),
                                max=df["besuchtesSemester"].max(),
                                value=df["besuchtesSemester"].max(),
                                marks={i: str(i) for i in range(1, 9)},
                                step=None
                    )
                ],
                style={"width":"50%"}
            )
        ]
    ),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                    html.Div(
                        children=[dcc.Graph(
                            id="output_container_2", 
                            figure={}
                        )]
                    )
                ],
            style={'display': 'inline-block'}
            ),
            html.Div(
                className="six columns",
                children=[
                    html.Div(
                        children=[dcc.Graph(
                            id="output_container_3", 
                            figure={}
                        )]
                    )
                ],
            style={'display': 'inline-block'}
            )
        ],
    )
])


## ----------------------- CALLBACK -----------------------

@app.callback(
    [Output(component_id="output_container_1", component_property="children"),
     Output(component_id="output_container_2", component_property="figure"),
     Output("output_container_3", "figure")],
    [Input(component_id="slct_study", component_property="value"),
     Input("measure", "value"), 
     Input("max_semester_slider", "value")]
    )
    
def update_graph(selected_study, selected_measure, max_sem):

    container = "Es werden Daten für den Studiengang {} angezeigt".format(selected_study)
    
    selected_measure = selected_measure

    dff = df_by_semester_and_study_agg.copy()

    # plot
    fig1 = px.line(dff.loc[(dff["STUDBEZ_kompakt"] == selected_study) & (dff["besuchtesSemester"] <= max_sem)], 
                    x="besuchtesSemester", 
                    y=selected_measure, 
                    color="STUDBEZ_kompakt", 
                    title="<b>ECTS-Punkte nach besuchtem Semester im Studienverlauf: {}</b>".format(selected_study),
                    markers=True)
    # remove decimals from x axis
    fig1.update_xaxes(dtick=1)
    # add anotations and hide legend
    fig1.update_layout(showlegend=False, 
                    yaxis_range=[-1,25])
    
    y_heights, antsis = create_lineplot_annotations_y(dataframe=dff.loc[(dff["besuchtesSemester"] <= max_sem)], 
                                            max_sem_in_plot = max_sem, 
                                            y_variable=selected_measure, 
                                            group_variable="STUDBEZ_kompakt")

    fig2 = px.line(dff.loc[(dff["besuchtesSemester"] <= max_sem)], 
                    x="besuchtesSemester", 
                    y=selected_measure, 
                    color="STUDBEZ_kompakt", 
                    title="<b>ECTS-Punkte nach besuchtem Semester im Studienverlauf - Vergleich",
                    markers=True)
    fig2.update_xaxes(dtick=1)
    # add anotations and hide legend
    fig2.update_layout(annotations=antsis, 
                    showlegend=False,     
                    yaxis_range=[-1,25])

    print("what ")
    return container, fig1, fig2



## ------------------------- RUN -------------------------

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)