# makefun-btc-race-24h-20261117-0603

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/zhazha473/makefun-btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/zhazha473/makefun-btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A mean-reversion dip-buyer for Coinbase Wrapped BTC (cbBTC) against USDC on Solana, built for make.fun's "Race a BTC trading bot live for 24 hours" bounty. It buys cbBTC only when the price stretches 80 bps below its 240-bar (4-hour) average and sells when the price reverts to that average, or on a fixed +80 bps take-profit / −80 bps stop-loss. One position, long only, $1,000 of paper money, standard library only.

On the published 24-hour dev window it made **+2.79 USDC net PnL on 2 round trips (4 trades), 0.7% maximum drawdown** — verified with the kit's own replay model, reproduced exactly by running the bot through the real `agent-fun/bars-replay/v1` protocol. For comparison, the kit's EMA-crossover baseline lost 106 USDC on the same window and buy-and-hold made 1.07 USDC.

## Run it

```sh
python3 -P -s main.py
```

The bot speaks `agent-fun/bars-replay/v1` (newline-delimited JSON on stdin/stdout): it reads one 1-minute bar per batch and answers with buy/sell orders. Grade it on the dev window with the kit:

```sh
node cli/makefun.mjs grade-local --kit <kit-dir> --bot . --driver docker
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=2zha-zha&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
