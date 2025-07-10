"""
Base Strategy Module
Contains the base class for all trading strategies with signal logging
"""
import backtrader as bt
from abc import abstractmethod
from typing import Dict, Any
from signal_extractor import StrategySignalLogger


class BaseStrategy(bt.Strategy, StrategySignalLogger):
    """Base class for all trading strategies with signal logging"""
    
    params = (
        ('printlog', True),
    )
    
    def __init__(self):
        bt.Strategy.__init__(self)
        StrategySignalLogger.__init__(self)
        self.order = None
        self._execution_log = []  # Log execution prices
        self._initialize_indicators()
    
    @abstractmethod
    def _initialize_indicators(self):
        """Initialize strategy-specific indicators"""
        pass
    
    @abstractmethod
    def should_buy(self) -> bool:
        """Define buy condition"""
        pass
    
    @abstractmethod
    def should_sell(self) -> bool:
        """Define sell condition"""
        pass
    
    @abstractmethod
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        pass
    
    @abstractmethod
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        pass
    
    def log(self, txt: str, dt=None):
        """Logging function"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            # Log execution for extraction later
            execution_record = {
                'side': 'buy' if order.isbuy() else 'sell',
                'price': order.executed.price,
                'size': order.executed.size,
                'value': order.executed.value,
                'commission': order.executed.comm,
                'datetime': self.datas[0].datetime.datetime(0)
            }
            self._execution_log.append(execution_record)
            
            if order.isbuy():
                self.log(f'BUY EXECUTED: Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}, '
                        f'Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED: Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}, '
                        f'Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected - Status: {order.getstatusname()}')

        self.order = None
    
    def next(self):
        """Main strategy logic"""
        # Check if an order is pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not in market, check if we should buy
            if self.should_buy():
                # Calculate position size (use 95% of available cash)
                cash = self.broker.getcash()
                price = self.data.close[0]
                size = (cash * 0.95) / price

                # Log the buy signal
                reason = self.get_buy_reason()
                self.log_buy_signal(price, reason)
                
                self.log(f'BUY CREATE: Price: {price:.2f}, Size: {size:.6f}, Cash: {cash:.2f}')
                self.order = self.buy(size=size)
        else:
            # In market, check if we should sell
            if self.should_sell():
                price = self.data.close[0]
                
                # Log the sell signal
                reason = self.get_sell_reason()
                self.log_sell_signal(price, reason)
                
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """Called when strategy ends"""
        self.log(f'Strategy ended with portfolio value: {self.broker.getvalue():.2f}')