# 数据层：关键词规则的 SQLite 存取。
#
# 命中判断在热路径上（每条私聊消息都要过一遍），所以启动时把整张表读进内存，
# SQLite 只作为持久化。写的时候先落库、再整表重建快照，所以匹配时要么看到旧
# 快照、要么看到写完之后的新快照，不会看到写了一半的状态。

import asyncio
from pathlib import Path

from ..entity.rule import ReplyRule
from .db import connect, create_table

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reply_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    match_type TEXT NOT NULL,
    reply TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    sort_order INTEGER NOT NULL DEFAULT 0
)
"""


class RuleStore:
    """规则表。SQLite 负责长期保存，内存快照负责每条消息的命中判断。"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        # 写操作串行化，避免页面连点两次保存时落库顺序错乱。
        self._lock = asyncio.Lock()
        # 内存快照：按 sort_order 升序排好的规则列表，匹配时顺序遍历。
        self._snapshot: list[ReplyRule] = []
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()
        self._load_snapshot()

    def _setup(self) -> None:
        """首次启动时建表。已存在就跳过。"""
        conn = connect(self.db_path)
        try:
            create_table(conn, CREATE_TABLE_SQL)
        finally:
            conn.close()

    def _load_snapshot(self) -> None:
        """把整张表读进内存，按 sort_order、id 升序。"""
        conn = connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT id, keyword, match_type, reply, enabled, sort_order "
                "FROM reply_rule ORDER BY sort_order ASC, id ASC"
            ).fetchall()
        finally:
            conn.close()
        # 每行按列顺序还原成实体，enabled 在库里是 0/1，这里转回 bool。
        self._snapshot = [
            ReplyRule(int(row[0]), str(row[1]), str(row[2]), str(row[3]),
                      bool(row[4]), int(row[5]))
            for row in rows
        ]

    def list_rules(self) -> list[ReplyRule]:
        """返回全部规则（含已关闭的），给页面展示用。"""
        return list(self._snapshot)

    def enabled_rules(self) -> list[ReplyRule]:
        """只返回启用的规则，匹配时用这个。"""
        return [rule for rule in self._snapshot if rule.enabled]

    async def save_rule(self, rule: ReplyRule) -> int:
        """新增或更新一条规则，返回规则 id。id 为 0 时按新增处理。"""
        async with self._lock:
            conn = connect(self.db_path)
            try:
                # 已有 id 就走更新，没有就插入并拿到自增 id。
                if rule.rule_id > 0:
                    conn.execute(
                        "UPDATE reply_rule SET keyword=?, match_type=?, reply=?, "
                        "enabled=?, sort_order=? WHERE id=?",
                        (rule.keyword, rule.match_type, rule.reply,
                         int(rule.enabled), rule.sort_order, rule.rule_id),
                    )
                    conn.commit()
                    rule_id = rule.rule_id
                else:
                    cur = conn.execute(
                        "INSERT INTO reply_rule (keyword, match_type, reply, enabled, sort_order) "
                        "VALUES (?,?,?,?,?)",
                        (rule.keyword, rule.match_type, rule.reply,
                         int(rule.enabled), rule.sort_order),
                    )
                    conn.commit()
                    rule_id = int(cur.lastrowid or 0)
            finally:
                conn.close()
            # 落库成功后再重建快照，保证内存里看到的一定是已持久化的数据。
            self._load_snapshot()
            return rule_id

    async def delete_rule(self, rule_id: int) -> bool:
        """按 id 删除规则。返回是否真的删掉了行。"""
        async with self._lock:
            conn = connect(self.db_path)
            try:
                cur = conn.execute("DELETE FROM reply_rule WHERE id=?", (rule_id,))
                conn.commit()
                deleted = cur.rowcount > 0
            finally:
                conn.close()
            # 只有删到行才重建快照，避免无意义的整表读取。
            if deleted:
                self._load_snapshot()
            return deleted
