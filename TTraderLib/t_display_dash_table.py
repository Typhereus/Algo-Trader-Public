import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import threading
import run_dash


class DisplayDashTable:

    # Takes in nested array to show tables

    name = ""

    table_headers = []

    table_array = []

    # Run from root
    """
    app = dash.Dash(
        __name__,
    )
    """

    app = run_dash.run_and_return_dash()


    @staticmethod
    def update_array(_nested_array):
        DisplayDashTable.table_array = _nested_array

    @staticmethod
    @app.callback(Output('show_table', 'children'),
                  Input('interval-component', 'n_intervals'))
    def show_table(interval):
        #
        _array = DisplayDashTable.table_array

        #
        if len(_array) == 0:
            column = [str(0)]
            _array = [column]

        # Input array of array and get table
        return html.Table \
                (
                [
                    # Header Array
                    html.Thead(html.Tr([html.Th(header) for header in DisplayDashTable.table_headers])),
                    html.Tbody(
                        [
                            html.Tr
                                (
                                [
                                    html.Td(_array[row][column])
                                    for column in range(len(_array[row]))
                                ]
                            )
                            # FOR HOW EVER MANY ROWS THERE ARE DO ABOVE
                            for row in range(len(_array))
                        ]
                    )
                ]
            )

    @staticmethod
    def run_dash_table():
        DisplayDashTable.app.run_server()

    @staticmethod
    def start_dash_table(_name, _header_array):
        #
        DisplayDashTable.name = _name
        DisplayDashTable.table_headers = _header_array

        #
        DisplayDashTable.app.layout = html.Div(
            children=
            [
                html.H4(children=DisplayDashTable.name),
                # html.Img(src='Assets/Typh.png'),
                # html.Div(id="broker_info"),
                html.Div(id='show_table'),
                dcc.Interval(id='interval-component', interval=1 * 999, n_intervals=0)
            ]
        )

        #
        dm_thread = threading.Thread(target=DisplayDashTable.run_dash_table, args=())
        dm_thread.start()
        print('dm_thread = threading.Thread(target=DisplayDashTable.run_dash_table, args=())dm_thread.start()')




