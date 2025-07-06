"""
Strategy Manager
Handles dynamic loading and management of trading strategies
"""
import os
import importlib.util
import inspect
from typing import Dict, List, Any, Type
from strategies import BaseStrategy, get_available_strategies


class StrategyManager:
    """Manages trading strategies including loading custom strategies"""
    
    def __init__(self):
        self.strategies = get_available_strategies().copy()
        self.custom_strategies_path = "custom_strategies"
        
        # Create custom strategies directory if it doesn't exist
        if not os.path.exists(self.custom_strategies_path):
            os.makedirs(self.custom_strategies_path)
    
    def load_custom_strategies(self):
        """Load custom strategies from the custom_strategies directory"""
        if not os.path.exists(self.custom_strategies_path):
            return
        
        for filename in os.listdir(self.custom_strategies_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                filepath = os.path.join(self.custom_strategies_path, filename)
                self._load_strategy_from_file(filepath)
    
    def _load_strategy_from_file(self, filepath: str):
        """Load a strategy from a Python file"""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("custom_strategy", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find all strategy classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseStrategy) and 
                    obj != BaseStrategy):
                    # Add to strategies
                    strategy_name = obj.__name__.replace('Strategy', '')
                    self.strategies[f"Custom: {strategy_name}"] = obj
                    print(f"Loaded custom strategy: {strategy_name}")
        
        except Exception as e:
            print(f"Error loading strategy from {filepath}: {e}")
    
    def get_all_strategies(self) -> Dict[str, Type[BaseStrategy]]:
        """Get all available strategies including custom ones"""
        return self.strategies
    
    def get_strategy(self, name: str) -> Type[BaseStrategy]:
        """Get a specific strategy by name"""
        return self.strategies.get(name)
    
    def get_strategy_params(self, name: str) -> Dict[str, Any]:
        """Get parameters for a specific strategy"""
        strategy_class = self.get_strategy(name)
        if strategy_class and hasattr(strategy_class, 'get_params'):
            return strategy_class.get_params()
        return {}
    
    def validate_strategy(self, strategy_class: Type) -> bool:
        """Validate that a strategy class is properly implemented"""
        required_methods = ['_initialize_indicators', 'should_buy', 'should_sell']
        
        for method in required_methods:
            if not hasattr(strategy_class, method):
                return False
        
        return True
    
    def create_custom_strategy_template(self, name: str) -> str:
        """Create a template for a new custom strategy"""
        template = f'''"""
Custom Strategy: {name}
"""
import backtrader as bt
from strategies import BaseStrategy


class {name}Strategy(BaseStrategy):
    """
    Custom {name} trading strategy
    
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
        return {{
            'param1': {{
                'type': 'int',
                'default': 10,
                'min': 1,
                'max': 100,
                'description': 'Description for param1'
            }},
            'param2': {{
                'type': 'int',
                'default': 20,
                'min': 1,
                'max': 200,
                'description': 'Description for param2'
            }}
        }}
'''
        
        filename = f"{self.custom_strategies_path}/{name.lower()}_strategy.py"
        with open(filename, 'w') as f:
            f.write(template)
        
        return filename