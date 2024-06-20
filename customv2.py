import backtrader as bt
from datetime import datetime
import json

class MyStrategy(bt.Strategy):
    params = (('stake', 10),)  # Example stake size for each buy
    
    def __init__(self, strategy_json):
        self.dataclose = self.datas[0].close
        self.strategy_json = json.loads(strategy_json)
        
        # Parse JSON to set entry and exit conditions
        self.entry_conditions = self.strategy_json['entry_conditions']
        self.exit_conditions = self.strategy_json['exit_conditions']
        
        # Store indicators
        self.indicators = {}
        self.crossovers = {}

        # Instantiate indicators based on the parsed conditions
        self._instantiate_indicators(self.entry_conditions)
        self._instantiate_indicators(self.exit_conditions)
    
    def _instantiate_indicators(self, conditions):
        if isinstance(conditions, dict):
            if 'all' in conditions or 'any' in conditions:
                for key in ['all', 'any']:
                    if key in conditions:
                        for cond in conditions[key]:
                            self._instantiate_indicators(cond)
            else:
                indicator_info = conditions['indicator']
                self._instantiate_indicator(indicator_info)
                if isinstance(conditions['value'], dict):
                    self._instantiate_indicator(conditions['value'])
                if conditions['comparator'] in ['crosses_above', 'crosses_below']:
                    self._instantiate_crossover(indicator_info, conditions['value'])
    
    def _instantiate_indicator(self, indicator_info):
        name = indicator_info['indicator']
        params = indicator_info['params']
        
        if name == 'MA':
            period = params['period']
            self.indicators[(name, period)] = bt.indicators.MovingAverageSimple(self.datas[0], period=period)
        elif name == 'RSI':
            period = params['period']
            self.indicators[(name, period)] = bt.indicators.RelativeStrengthIndex(self.datas[0], period=period)
    
    def _instantiate_crossover(self, left_info, right_info):
        left_name = left_info['indicator']
        left_params = left_info['params']
        left_indicator = self._get_indicator_value(left_info)
        
        right_name = right_info['indicator']
        right_params = right_info['params']
        right_indicator = self._get_indicator_value(right_info)
        
        self.crossovers[(left_name, tuple(left_params.items()), right_name, tuple(right_params.items()))] = bt.ind.CrossOver(left_indicator, right_indicator)
    
    def _get_indicator_value(self, indicator_info):
        name = indicator_info['indicator']
        params = indicator_info['params']
        
        if name == 'MA':
            period = params['period']
            return self.indicators[(name, period)]
        elif name == 'RSI':
            period = params['period']
            return self.indicators[(name, period)]
        
        return None
    
    def _evaluate_condition(self, cond):
        if 'all' in cond:
            return all(self._evaluate_condition(sub_cond) for sub_cond in cond['all'])
        elif 'any' in cond:
            return any(self._evaluate_condition(sub_cond) for sub_cond in cond['any'])
        
        indicator = self._get_indicator_value(cond['indicator'])
        comparator = cond['comparator']
        value = cond['value']
        
        if isinstance(value, dict):
            value = self._get_indicator_value(value)
        
        if comparator == 'crosses_above':
            crossover = self.crossovers[(cond['indicator']['indicator'], tuple(cond['indicator']['params'].items()), value['indicator'], tuple(value['params'].items()))]
            return crossover[0] > 0
        elif comparator == 'crosses_below':
            crossover = self.crossovers[(cond['indicator']['indicator'], tuple(cond['indicator']['params'].items()), value['indicator'], tuple(value['params'].items()))]
            return crossover[0] < 0
        elif comparator == 'less_than':
            return indicator[0] < value
        elif comparator == 'greater_than':
            return indicator[0] > value
        
        return False  # Default return if comparator is not recognized or condition not met
    
    def next(self):
        cash = self.broker.get_cash()  # Get available cash
        
        if cash >= self.dataclose[0] * self.params.stake:  # Check if enough cash for another buy
            if self._evaluate_condition(self.entry_conditions):
                self.buy(size=self.params.stake)
        
        if self.position.size > 0:
            if self._evaluate_condition(self.exit_conditions):
                self.sell(size=self.position.size)  # Sell all shares

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Load data (example: Apple stock data)
    data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2023, 1, 1), todate=datetime(2023, 12, 31))
    
    cerebro.adddata(data)
    
    # Define strategy with strategy_json
    strategy_json = '''
    {
      "entry_conditions": {
        "all": [
          {
            "indicator": {"indicator": "MA", "params": {"period": 10}},
            "comparator": "crosses_above",
            "value": {"indicator": "MA", "params": {"period": 50}}
          },
          {
            "any": [
              {
                "indicator": {"indicator": "RSI", "params": {"period": 14}},
                "comparator": "less_than",
                "value": 30
              },
              {
                "indicator": {"indicator": "RSI", "params": {"period": 14}},
                "comparator": "greater_than",
                "value": 70
              }
            ]
          }
        ]
      },
      "exit_conditions": {
        "all": [
          {
            "indicator": {"indicator": "MA", "params": {"period": 10}},
            "comparator": "crosses_below",
            "value": {"indicator": "MA", "params": {"period": 50}}
          },
          {
            "indicator": {"indicator": "RSI", "params": {"period": 14}},
            "comparator": "greater_than",
            "value": 70
          }
        ]
      }
    }
    '''
    
    cerebro.addstrategy(MyStrategy, strategy_json=strategy_json)
    cerebro.run()
    cerebro.plot(style='candlestick')
