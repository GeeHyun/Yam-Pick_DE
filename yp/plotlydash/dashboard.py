# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine 
import pandas as pd
from functions import func_user__nutrient

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=280)

def calorie():
    foods = pd.read_sql_query("select * from tb_user_img;", engine)

    if len(foods):
        food = foods.iloc[-1]

        user_email = food['upload_user']
        user = pd.read_sql_query(f"select * from tb_user_info where user_email == '{user_email}';", engine).iloc[-1]

        user_age = func_user__nutrient.user_age(user['user_birth'])
        weight_s = func_user__nutrient.standard_weight(user['user_sex'], user['user_height'])
        weight_a = func_user__nutrient.adjusted_weight(user['user_weight'], weight_s)
        user_calorie = func_user__nutrient.calorie_counting(user['user_sex'], user_age, user['user_height'], weight_a, str(user['user_pa']))
        user_nutrient_dic = func_user__nutrient.necessary_nutrients(user['user_sex'], user_age, user['user_weight'], user_calorie)

        food_calorie = pd.read_sql_query(f"select energy from tb_food_img where food_name == '{food['upload_foodname']}';", engine).iloc[0, 0]
        food_percent = food['upload_percent']

        return user_calorie -  food_calorie * food_percent

    else:
        return 0



# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [
            'hi',
        ],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }

# Build Dash layout
def create_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        url_base_pathname='/dashboard/',
       assets_folder='plotlydash/assets'
        )

    def serve_layout():
        return  html.Div(
        children=[
            html.Div(
                children=[
                    html.H1(
                        [
                            "Yam-Pick",
                            html.A(
                                html.Img(
                                    src="logo.png",
                                    style={"float": "right", "height": "50px"},
                                ),
                            ),
                        ],
                        style={"text-align": "left"},
                    ),
                ]
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.H4(
                                [
                                    "Daily Calorie"
                                ],
                                className="container_title"
                            ),
                            dcc.Graph(
                                id="indicator-graph",
                                figure={
                                    "data": [
                                        {
                                            "type": "indicator",
                                            "value": calorie(),
                                            "number": {"font": {"color": "#263238"}},
                                        }
                                    ],
                                    "layout": {
                                        "template": template,
                                        "height": 150,
                                        "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
                                    },
                                },
                                config={"displayModeBar": False},
                                className="svg-container",
                            )
                        ]
                    ),
                ],
                className="six columns pretty_container",
                id="indicator-div",
            ),
        ]
    )


    dash_app.layout = serve_layout

    init_callbacks(dash_app)

    return dash_app.server


def init_callbacks(dash_app):
    @dash_app.callback(
        Output(component_id='my-output', component_property='children'),
        Input(component_id='my-input', component_property='value')
    )
    def update_graph(rows):
        pass


