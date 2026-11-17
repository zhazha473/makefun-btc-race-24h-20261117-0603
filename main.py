"""Dip-buyer for cbBTC/USDC on the agent-fun/bars-replay/v1 replay.

Idea
----
One-minute cbBTC prices mean-revert around their slow average much faster
than they trend: a 1-minute move is only ~6 bps of noise, while a dip of
80 bps below the 240-bar (4-hour) simple moving average of closes is a
stretched rubber band that usually snaps back within a few hours. This bot
buys exactly those stretched dips, with its whole cash, and sells as soon as
the price has reverted to the average -- or sooner on a fixed take-profit,
or on a fixed stop-loss if the dip keeps falling.

Rules (all integer arithmetic, so two runs on the same bars answer byte
for byte the same):
  * Keep the last 240 closes of CBBTC and their sum. Until 240 closes have
    been seen, trade nothing.
  * Flat and close * 240 * 10000 < sum * 9920 (close more than 80 bps
    below the 240-bar SMA): buy with all available cash.
  * Long and close * 240 >= sum (price back at or above the SMA): sell
    the whole position.
  * Long and position value >= 10080/10000 of its cost (up 80 bps):
    sell the whole position.
  * Long and position value <= 9920/10000 of its cost (down 80 bps):
    sell the whole position.
  * Every order caps its slippage at 100 bps from the latest close, so a
    fill that jumps far past the close is refused and retried next bar
    instead of chased.
  * At most one order per batch, at most one open position, long only.
    No short, no leverage, no network, no wall clock, no files, no
    randomness: the only inputs are the bars the harness sends.

Why not trend-follow here: on the published 24-hour dev window every
EMA-crossover and momentum variant I graded lost money to whipsaw (the
best, a plain 8/21 EMA cross, lost 106 USDC on 68 trades), while this
dip-buyer made +2.79 USDC on 2 round trips with a 0.7% maximum drawdown.
A full round trip costs ~26 bps in fee, slippage and impact, so an 80 bps
dip has to revert most of the way to pay -- and on the dev window both
dips did (bought the window trough at bar 386, sold back at the average
65 bars later; bought the post-peak dip at bar 1094, sold 182 bars later).
"""

import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"

# 240 one-minute bars = 4 hours of closes for the slow average.
WINDOW = 240
# 80 basis points, in both directions: dip depth, take-profit, stop-loss.
DIP_BPS = 80
TAKE_BPS = 80
STOP_BPS = 80
# Refuse a fill that moved more than 100 bps from the close we decided on.
MAX_SLIPPAGE_BPS = 100

_closes = deque(maxlen=WINDOW)
_sum = 0


def _push(close):
    global _sum
    if len(_closes) == WINDOW:
        _sum -= _closes[0]
    _closes.append(close)
    _sum += close


def on_batch(state, batch):
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            _push(int(bar["c"]))
    if len(_closes) < WINDOW:
        return []
    close = _closes[-1]
    held = state.positions.get(SYMBOL)
    if held is not None:
        value = state.value(SYMBOL, held.qty)
        # Reverted to the average, or take-profit, or stop-loss: exit whole.
        if (
            close * WINDOW >= _sum
            or value * 10000 >= held.cost * (10000 + TAKE_BPS)
            or value * 10000 <= held.cost * (10000 - STOP_BPS)
        ):
            return [
                {
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": held.qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }
            ]
        return []
    # Flat and stretched 80 bps or more below the slow average: buy it all.
    if close * WINDOW * 10000 < _sum * (10000 - DIP_BPS):
        return [
            {
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": state.cash,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }
        ]
    return []


makefun_bars.run(on_batch)
