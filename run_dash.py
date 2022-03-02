import dash
import dash_core_components as dcc
import dash_html_components as html

def run_and_return_dash():
    app = dash.Dash(__name__)
    return app
