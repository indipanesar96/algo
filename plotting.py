import plotly.graph_objs as go
from plotly.subplots import make_subplots

import util
from portfolio import ResultSet


class Plotter:
    def __init__(self, resultSet: ResultSet):
        self.res = resultSet
        self.data = self.res.data

    def plotBlotterTables(self):
        blotterTables = [go.Figure() for _ in range(len(self.res.blotters))]
        for idx, (strat, blot) in enumerate(self.res.blotters.items()):
            blotterTables[idx].add_trace(
                go.Table(
                    header=dict(
                        values=blot.columns,
                        fill_color='paleturquoise',
                        align='center'
                    ),
                    cells=dict(
                        values=[blot[i] for i in blot.columns],
                        fill_color='lavender',
                        align='center'
                    ),
                    name=strat.name
                )
            )

        for f in blotterTables:
            f.show()

    def plotPortfolios(self):
        fig = make_subplots(rows=1, cols=1)

        for strat, blot in self.res.blotters.items():
            pflValue = blot.groupby(['dt'])['holdingsValue'].sum()
            fig.add_trace(
                go.Scatter(
                    x=pflValue.index,
                    y=pflValue.values,
                    name=strat.name,
                    mode='lines'
                ), row=1, col=1
            )
            trades = self.res.portfolios[strat].trades

            for tr in trades:
                fig.add_trace(
                    go.Scatter(
                        x=[tr.dt],
                        y=[0],
                        name=tr.asset,
                        showlegend=False,
                        mode='markers',
                        marker=dict(
                            color='red' if tr.action == util.Action.SELL.value else 'blue',
                            symbol='triangle-down' if tr.action == util.Action.SELL.value else 'triangle-up',
                            size=15
                        )
                    ), row=1, col=1
                )

        fig.show()
