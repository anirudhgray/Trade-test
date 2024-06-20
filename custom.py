import backtrader as bt
import json
import pandas as pd

class CustomStrategy(bt.Strategy):
    params = (
        ('strategy', None),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.indicators = {}
        self.entry_conditions = self.params.strategy.get('entry_conditions', [])
        self.exit_conditions = self.params.strategy.get('exit_conditions', [])
        
        self._initialize_indicators()
    
    def _initialize_indicators(self):
        # Initialize indicators based on the strategy schema
        for cond in self.entry_conditions + self.exit_conditions:
            indicator_info = cond.get('indicator') or cond.get('left_operand')
            if indicator_info:
                self._initialize_indicator(indicator_info)
            value_info = cond.get('value') or cond.get('right_operand')
            if isinstance(value_info, dict):
                self._initialize_indicator(value_info)

    def _initialize_indicator(self, indicator_info):
        name = indicator_info['indicator']
        params = indicator_info['params']
        if name == 'MVA':
            period = params['period']
            self.indicators[(name, period)] = bt.indicators.SimpleMovingAverage(self.datas[0], period=period)
        elif name == 'RSI':
            period = params['period']
            self.indicators[(name, period)] = bt.indicators.RelativeStrengthIndex(self.datas[0], period=period)
        elif name == 'Price':
            self.indicators[(name, params['type'])] = self.dataclose

    def _evaluate_condition(self, cond):
        left = cond.get('left_operand', cond['indicator'])
        right = cond.get('right_operand', cond['value'])
        comparator = cond['comparator']
        
        left_value = self._get_indicator_value(left)
        right_value = self._get_indicator_value(right)

        if cond.get('operator'):
            operator = cond['operator']
            if operator == '+':
                left_value += right_value
            elif operator == '-':
                left_value -= right_value
            elif operator == '*':
                left_value *= right_value
            elif operator == '/':
                left_value /= right_value

        if comparator == '>':
            return left_value > right_value
        elif comparator == '<':
            return left_value < right_value
        elif comparator == '==':
            return left_value == right_value
        elif comparator == 'crosses_above':
            return bt.ind.CrossOver(left_value, right_value) > 0
        elif comparator == 'crosses_below':
            return bt.ind.CrossOver(left_value, right_value) < 0
        elif comparator == 'rises':
            return self.dataclose > self.dataclose(-1) > self.dataclose(-2) and (len(self) > 2)
        elif comparator == 'falls':
            return self.dataclose < self.dataclose(-1) < self.dataclose(-2) and (len(self) > 2)

    def _get_indicator_value(self, indicator_info):
        if isinstance(indicator_info, dict):
            name = indicator_info['indicator']
            params = indicator_info['params']
            return self.indicators[(name, params['period'])]
        else:
            return indicator_info

    def next(self):
        if self.position.size == 0:
            if all(self._evaluate_condition(cond) for cond in self.entry_conditions):
                self.buy()
        else:
            if all(self._evaluate_condition(cond) for cond in self.exit_conditions):
                self.sell()

# Example usage
def get_ticker_data(ticker, start_date, end_date):
    # Replace this with actual data fetching logic
    data = pd.read_csv(f'{ticker}.csv', parse_dates=True, index_col='Date')
    data = data[(data.index >= start_date) & (data.index <= end_date)]
    return data

if __name__ == '__main__':
    strategy_json = '''
    {
      "entry_conditions": [
        {"indicator": "Price", "params": {"type": "Close"}, "comparator": "rises", "value": 3}
      ],
      "exit_conditions": [
        {"indicator": "Price", "params": {"type": "Close"}, "comparator": "falls", "value": 2}
      ]
    }
    '''
    strategy = json.loads(strategy_json)
    data = get_ticker_data('AAPL', '2020-01-01', '2021-01-01')

    # Create a Backtrader data feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Initialize the cerebro engine
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(CustomStrategy, strategy=strategy)
    cerebro.broker.setcash(10000.0)

    # Run the backtest
    cerebro.run()
    cerebro.plot()
