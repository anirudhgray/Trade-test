from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree, Static, Button
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
import os
import json
import backtrader as bt
from strategy import MyStrategy

class TradingApp(App):
    CSS_PATH = "style.css"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Horizontal(
            Vertical(
                Static("Select Data File", id="data_title"),
                DirectoryTree(path="./data", id="data_tree")
            ),
            Vertical(
                Static("Select Strategy File", id="strategy_title"),
                DirectoryTree(path="./sample-inputs", id="strategy_tree")
            )
        )
        yield Button("Run Backtest", id="run_button")

    selected_data_file = reactive("")
    selected_strategy_file = reactive("")

    def on_mount(self):
        self.query_one("#data_tree").focus()

    def on_directory_tree_selected(self, message):
        if "data_tree" in message.widget.id:
            self.selected_data_file = message.path
        elif "strategy_tree" in message.widget.id:
            self.selected_strategy_file = message.path

    def on_button_pressed(self, event):
        if event.button.id == "run_button":
            self.run_backtest()

    def run_backtest(self):
        if not self.selected_data_file or not self.selected_strategy_file:
            self.exit("Please select both data and strategy files.")
            return

        cerebro = bt.Cerebro()

        data = bt.feeds.YahooFinanceCSVData(dataname=self.selected_data_file)
        cerebro.adddata(data)

        with open(self.selected_strategy_file, 'r') as file:
            strategy_json = file.read()

        cerebro.addstrategy(MyStrategy, strategy_json=strategy_json)

        cerebro.broker.set_cash(10000)
        cerebro.run()
        cerebro.plot()

if __name__ == "__main__":
    TradingApp.run()
