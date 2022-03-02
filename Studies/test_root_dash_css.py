import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import threading
import sys
import os

path = sys.path[1] + "\Bassets"
path2 = os.getcwd() + '\Bassets'
external_stylesheets = [path2 + "/typography.css"]
external_stylesheets2 = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
print(external_stylesheets)
#print(path2)

dash.Dash(assets_url_path=path)
dash.Dash(assets_folder=path)

app = dash.Dash(__name__)

app.layout = html.Div(
            children=
            [
                html.H4(children="STUFF"),
            ]
        )

app.run_server()
