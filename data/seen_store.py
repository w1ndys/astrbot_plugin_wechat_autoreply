# 数据层：见过哪些会话。只用来判断「这是不是这个用户的第一条消息」。
#
# 微信的关注事件（subscribe）不会被 AstrBot 的公众号适配器转成消息事件，
# 所以「被关注回复」只能用「首次发消息」近似。

import asyncio
from datetime import datetime
from pathlib import Path

from .db import connect, create_table

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS seen_session (
    umo TEXT PRIMARY KEY,
    first_seen_at TEXT NOT NULL
)
"""


class SeenStore:
    """首见会话表。落在 SQLite 里，进程重启后不会被当成新用户。"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        # 同一用户连发两条时，避免并发插入同一主键。
        self._lock = asyncio.Lock()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = connect(db_path)
        try:
            create_table(conn, CREATE_TABLE_SQL)
        finally:
            conn.close()

    async def mark_seen(self, umo: str) -> bool:
        """记录会话已见过，返回这次是不是第一次。"""
        async with self._lock:
            conn = connect(self.db_path)
            try:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO seen_session (umo, first_seen_at) VALUES (?, ?)",
                    (umo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                )
                conn.commit()
                # rowcount 为 1 说明插进去了，即这次是首见。
                return cur.rowcount > 0
            finally:
                conn.close()
