"""Multi-Symbol Momentum Strategy

Trades BTC and ETH simultaneously using momentum and range filters.
Implements complex entry/exit rules with dynamic sizing and risk controls.
"""

import datetime
import backtrader as bt
from base_strategy import BaseStrategy


class MultiSymbolMomentumStrategy(BaseStrategy):
    """Momentum strategy operating on BTC and ETH feeds."""

    params = (("printlog", True),)

    def _initialize_indicators(self):
        self.inds = {}
        for data in self.datas:
            # Determine available data length if using PandasData
            data_len = 0
            if hasattr(data, "_dataname") and hasattr(data._dataname, "__len__"):
                try:
                    data_len = len(data._dataname)
                except Exception:
                    data_len = 0

            if data_len > 1:
                atr_period = min(288, data_len - 1)
                sma_period = min(288, data_len - 1)
                weekly_period = min(2016, data_len - 1)
            else:
                atr_period = sma_period = weekly_period = 1

            atr = bt.indicators.ATR(data, period=atr_period)
            weighted = (data.high + data.low + data.close * 2) / 4
            wavg = bt.indicators.SimpleMovingAverage(weighted, period=sma_period)
            weekly_high = bt.indicators.Highest(data.high, period=weekly_period)
            weekly_low = bt.indicators.Lowest(data.low, period=weekly_period)
            vol_avg = bt.indicators.SimpleMovingAverage(data.volume, period=sma_period)
            self.inds[data] = {
                "atr": atr,
                "wavg": wavg,
                "weekly_high": weekly_high,
                "weekly_low": weekly_low,
                "vol_avg": vol_avg,
                "entry_price": None,
                "size": 0.0,
                "highest": None,
                "trailing_stop": None,
                "allocated": 0.0,
                "losses": 0,
                "trade_size_factor": 1.0,
                "halt_until": None,
                "orig_size": 0.0,
            }

    # helper to map data name to config
    def _symbol_config(self, data):
        name = getattr(data, "_name", "") or str(data._dataname)
        if "BTC" in name.upper():
            return {"sizes": [100, 150, 200], "max_alloc": 500, "profit": 0.6}
        if "ETH" in name.upper():
            return {"sizes": [250, 275, 300], "max_alloc": 500, "profit": 0.75}
        # default config
        return {"sizes": [100], "max_alloc": 0, "profit": 0.5}

    def _position_open(self, data):
        return self.getposition(data).size != 0

    def next(self):
        dt = self.datas[0].datetime.datetime(0)
        for data in self.datas:
            ind = self.inds[data]
            cfg = self._symbol_config(data)
            price = data.close[0]
            if not self._position_open(data):
                # Trading halt check
                if ind["halt_until"] and dt < ind["halt_until"]:
                    continue
                # Weekly range filter
                if price < ind["weekly_low"][0] * 1.01:
                    continue
                if price > ind["weekly_high"][0] * 0.995:
                    continue
                # Primary entry conditions
                downtrend_thresh = ind["wavg"][0] - ind["atr"][0]
                if price >= downtrend_thresh:
                    reason = "Stable uptrend"
                elif price < downtrend_thresh and price > data.close[-1]:
                    reason = "Momentary bounce"
                else:
                    continue
                # Position sizing
                remaining = cfg["max_alloc"] - ind["allocated"]
                trade_value = 0
                for s in cfg["sizes"]:
                    adj = s * ind["trade_size_factor"]
                    if adj <= remaining:
                        trade_value = adj
                        break
                if trade_value == 0:
                    continue
                size = trade_value / price
                self.log_buy_signal(price, reason)
                self.log(
                    f"BUY CREATE {data._name}: Price {price:.2f}, Value {trade_value:.2f}"
                )
                self.buy(data=data, size=size)
                ind["entry_price"] = price
                ind["size"] = size
                ind["orig_size"] = size
                ind["highest"] = price
                ind["trailing_stop"] = (
                    price - ind["atr"][0] * 1.8 if ind["atr"][0] else price * 0.99
                )
                ind["allocated"] += trade_value
            else:
                # Manage open position
                ind["highest"] = max(ind["highest"], price)
                ind["trailing_stop"] = max(ind["trailing_stop"], ind["highest"] * 0.999)
                profit_pct = (price - ind["entry_price"]) / ind["entry_price"] * 100
                # Scale-in logic
                if profit_pct >= 0.3 and data.volume[0] > ind["vol_avg"][0] * 2:
                    remaining = cfg["max_alloc"] - ind["allocated"]
                    add_value = min(50, ind["entry_price"] * ind["orig_size"] * 0.5)
                    add_value = min(add_value, remaining)
                    if add_value > 0:
                        add_size = add_value / price
                        new_entry = (
                            ind["entry_price"] * ind["size"] + price * add_size
                        ) / (ind["size"] + add_size)
                        self.log_buy_signal(price, "Scale in")
                        self.buy(data=data, size=add_size)
                        ind["entry_price"] = new_entry
                        ind["size"] += add_size
                        ind["allocated"] += add_value
                # Exit conditions
                sell_reason = None
                if price >= ind["entry_price"] * (1 + cfg["profit"] / 100):
                    sell_reason = "Profit target"
                elif profit_pct > 0 and price < ind["wavg"][0] * 0.999:
                    sell_reason = "Trend reversal"
                elif profit_pct > 0 and price <= ind["trailing_stop"]:
                    sell_reason = "Trailing stop"
                elif price <= ind["entry_price"] - ind["atr"][0] * 1.8:
                    sell_reason = "Stop loss"
                if sell_reason:
                    self.log_sell_signal(price, sell_reason)
                    self.log(f"SELL CREATE {data._name}: Price {price:.2f}")
                    self.sell(data=data, size=self.getposition(data).size)
                    profit = (price - ind["entry_price"]) * ind["size"]
                    if profit > 0:
                        ind["losses"] = 0
                        ind["trade_size_factor"] = min(
                            1.0, ind["trade_size_factor"] * 1.5
                        )
                        ind["halt_until"] = None
                    else:
                        ind["losses"] += 1
                        if ind["losses"] >= 5:
                            ind["halt_until"] = dt + datetime.timedelta(hours=2)
                        if ind["losses"] >= 3:
                            ind["trade_size_factor"] = 0.5
                    ind["allocated"] -= ind["entry_price"] * ind["size"]
                    ind["entry_price"] = None
                    ind["size"] = 0
                    ind["highest"] = None
                    ind["trailing_stop"] = None
