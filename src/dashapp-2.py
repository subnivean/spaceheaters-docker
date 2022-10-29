import dash
from dash import dcc, html, Input, Output, callback
import dash_daq as daq
import pandas as pd

filename = "/ctdata/house_heat_pump_ct_readings.log"
COSTPERKWH = 0.177
REFRESH = 60 * 1000  # In milliseconds

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Heat Pump Analytics",),

        daq.NumericInput(
            id="days-to-show",
            label='Number of Days',
            labelPosition='bottom',
            value=1,
            min=1,
            max=10,
        ),

        html.P(
            id="total-kwh",
            ),

        html.P(
            id="time-to-next-refresh",
            ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="ct3-chart",
                        config={"displayModeBar": True},
                    ),
                    className="card",
                ),

                dcc.Interval(
                    id="interval-component",
                    interval=REFRESH,  # in milliseconds
                    n_intervals=0
                ),

                dcc.Interval(
                    id="countdown-component",
                    interval=10000,  # in milliseconds
                    n_intervals=0
                )
            ],
            className="wrapper",
        ),
    ]
)

@callback(
    Output("ct3-chart", "figure"),
    Output("total-kwh", "children"),
    Input("interval-component", "n_intervals"),
    Input("days-to-show", "value")
)
def update_charts(n, daystoshow):
    """Updates chart data on events.

    Args:
        n: n_intervals from the `dcc.Interval` instance. Only used
          for firing a callback.
        daystoshow: Number of days to show on the chart, counting
          back from now.

    Returns:
        See `Output()`s in callback decorator.
    """

    # Filter data when showing many days' worth to speed up
    # plotting. Also applies to calculations (which don't seem
    # to suffer much in accuracy).
    # Equation from the two (day, nth) points (1, 1) and (5, 3).
    nth = int(0.5 * daystoshow + 0.5)

    data = pd.read_csv(filename, header=None, names="Date ct0 ct1 ct2 ct3".split())
    data = data.iloc[::nth, :]  # Don't need to see everything

    data["Date"] = pd.to_datetime(data["Date"], utc=True)

    # Get the last date
    now = data.iloc[-1]["Date"]
    dt = pd.Timedelta(daystoshow, 'D')
    datemask = data["Date"] >= now - dt
    data = data[datemask]

    data["Date"] = data["Date"].dt.tz_convert("US/Eastern")

    noisemask = data['ct3'] < 150  # Noise when nothing is happening
    data.loc[noisemask, 'ct3'] = 0.0

    incrseconds = (data['Date'] - data['Date'].shift()).fillna(pd.Timedelta(0)).dt.total_seconds()
    totkwh = (incrseconds * data["ct3"] / 1000 / 3600).sum()
    totcost = totkwh * COSTPERKWH

    datastr = f"Total kWh: {totkwh:.2f}  Total Cost: ${totcost:.2f}"

    ct3_chart_figure = {

        "data": [
            {
                "x": data["Date"],
                "y": data["ct3"],
                "type": "lines",
            },
        ],

        "layout": {
            "title": {
                "text": "CT3 readings",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": False},
            "yaxis": {"fixedrange": False},
            "colorway": ["#17B897"],
        },
    }

    return ct3_chart_figure, datastr

@callback(
    Output("time-to-next-refresh", "children"),
    Input("countdown-component", "n_intervals")
)
def update_time_to_next_refresh(n):
    countdown = 60 - ((n * 10) % 60)
    return f"{countdown} seconds to next refresh"

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
