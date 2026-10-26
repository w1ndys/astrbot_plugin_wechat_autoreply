# 实体层：一条关键词回复规则。只描述数据形状，不负责存取。


class ReplyRule:
    """一条关键词规则：消息命中 keyword 时，原样回复 reply。"""

    def __init__(
        self,
        rule_id: int,
        keyword: str,
        match_type: str,
        reply: str,
        enabled: bool,
        sort_order: int,
    ) -> None:
        # 数据库主键。页面改、删都靠它定位，新建时为 0。
        self.rule_id = rule_id
        # 参与匹配的关键词或正则表达式。
        self.keyword = keyword
        # 匹配方式，取值来自 entity/constants 的 MATCH_TYPES。
        self.match_type = match_type
        # 命中后原样发出去的文本，允许换行。
        self.reply = reply
        # 关掉的规则保留在库里但不参与匹配。
        self.enabled = enabled
        # 排序决定多条规则同时命中时谁先赢，小的优先。
        self.sort_order = sort_order

    def to_dict(self) -> dict:
        """给页面用的纯字典。字段名与前端 types.ts 保持一致。"""
        return {
            "id": self.rule_id,
            "keyword": self.keyword,
            "match_type": self.match_type,
            "reply": self.reply,
            "enabled": self.enabled,
            "sort_order": self.sort_order,
        }
