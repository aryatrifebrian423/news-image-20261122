# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/aryatrifebrian423/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/aryatrifebrian423/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

22 November 2026: 46 stories, a UTC timeline and a date check

A one-page newspaper front page summing up the world news of Sunday
22 November 2026: 46 stories, each checked against 2 sources reported
that day, a UTC timeline of the day's events, and a date check. The
image is drawn by a pure Python standard-library program (a hand-built
5x7 bitmap font and a hand-built PNG encoder), so it runs with no
network and no dependencies and writes byte-identical output on every
run.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB).

## Sources

See [SOURCES.md](SOURCES.md) for the two reports behind every story.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x9vj0gh6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
