from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "business.db"
DOCS_PATH = DATA_DIR / "business_docs.json"


def connect() -> sqlite3.Connection:
    ensure_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def load_docs() -> list[dict[str, str]]:
    ensure_database()
    return json.loads(DOCS_PATH.read_text(encoding="utf-8"))


def reset_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    create_schema()
    seed_orders()
    seed_docs()


def ensure_database() -> None:
    if DB_PATH.exists() and DOCS_PATH.exists():
        return
    reset_database()


def create_schema() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            create table if not exists orders (
              id integer primary key,
              order_date text not null,
              channel text not null,
              category text not null,
              region text not null,
              amount real not null,
              status text not null
            );

            create table if not exists campaigns (
              id integer primary key,
              name text not null,
              start_date text not null,
              end_date text not null,
              channel text not null,
              cost real not null,
              rule text not null
            );
            """
        )


def seed_orders() -> None:
    channels = ["search", "recommendation", "ads"]
    categories = ["electronics", "home", "beauty"]
    regions = ["east", "south", "north"]
    today = date(2026, 5, 27)
    rows: list[tuple[str, str, str, str, float, str]] = []

    for day_offset in range(60):
        current_day = today - timedelta(days=day_offset)
        is_recent_window = day_offset < 30
        for channel in channels:
            for category in categories:
                base = 1380 + (day_offset % 7) * 35
                if channel == "recommendation":
                    base *= 1.18
                if channel == "ads":
                    base *= 0.92
                if category == "electronics":
                    base *= 1.25
                if category == "beauty":
                    base *= 0.85

                amount = base
                if is_recent_window and channel == "search" and category == "electronics":
                    amount *= 0.58
                if is_recent_window and channel == "ads":
                    amount *= 0.82

                for region in regions:
                    region_factor = {"east": 1.08, "south": 0.97, "north": 0.9}[region]
                    rows.append(
                        (
                            current_day.isoformat(),
                            channel,
                            category,
                            region,
                            round(amount * region_factor, 2),
                            "paid",
                        )
                    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            insert into orders(order_date, channel, category, region, amount, status)
            values (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.executemany(
            """
            insert into campaigns(name, start_date, end_date, channel, cost, rule)
            values (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "spring-search-coupon",
                    "2026-04-20",
                    "2026-05-10",
                    "search",
                    18000,
                    "搜索渠道电子品类满 500 减 40，5 月 10 日结束。",
                ),
                (
                    "ads-new-user",
                    "2026-05-01",
                    "2026-05-27",
                    "ads",
                    24000,
                    "广告渠道新客券预算下调 20%，投放以美妆和家居为主。",
                ),
            ],
        )


def seed_docs() -> None:
    docs = [
        {
            "id": "metric-gmv",
            "title": "GMV 指标口径",
            "text": "GMV 指支付成功订单金额，本教程示例只统计 status=paid 的订单，不扣除退款。",
        },
        {
            "id": "campaign-search-coupon",
            "title": "搜索渠道电子品类活动",
            "text": "搜索渠道电子品类满减券在 2026-05-10 结束，活动结束后搜索渠道转化可能下降。",
        },
        {
            "id": "campaign-ads-budget",
            "title": "广告渠道预算变化",
            "text": "2026-05 广告渠道新客券预算下调 20%，广告渠道 GMV 可能受到投放规模影响。",
        },
        {
            "id": "analysis-policy",
            "title": "经营分析结论要求",
            "text": "经营分析报告必须包含结论、证据、风险和建议，不能只输出指标数字。",
        },
    ]
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
