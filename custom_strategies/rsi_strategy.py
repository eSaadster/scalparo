"""
Custom Strategy: RSI
"""
import backtrader as bt
from strategies import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    Custom RSI trading strategy
    
    Add your strategy description here
    """
    
    params = (
        # Add your custom parameters here
        ('param1', 10),
        ('param2', 20),
        ('printlog', True),
    )
    
    def _initialize_indicators(self):
        """Initialize your custom indicators here"""
        # Example:
        # self.sma = bt.indicators.SimpleMovingAverage(
        #     self.data.close, period=self.params.param1
        # )
        pass
    
    def should_buy(self) -> bool:
        """
        Define your buy condition here
        Return True when you want to buy
        """
        # Example:
        # return self.data.close[0] > self.sma[0]
        return False
    
    def should_sell(self) -> bool:
        """
        Define your sell condition here
        Return True when you want to sell
        """
        # Example:
        # return self.data.close[0] < self.sma[0]
        return False
    
    @classmethod
    def get_params(cls) -> dict:
        """Define parameter metadata for UI"""
        return {
            'param1': {
                'type': 'int',
                'default': 10,
                'min': 1,
                'max': 100,
                'description': 'Description for param1'
            },
            'param2': {
                'type': 'int',
                'default': 20,
                'min': 1,
                'max': 200,
                'description': 'Description for param2'
            }
        }
