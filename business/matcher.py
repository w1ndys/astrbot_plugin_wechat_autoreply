# 业务层：关键词匹配。纯函数，不碰数据库、不碰 AstrBot，方便单测。

import re

from ..entity.constants import MATCH_CONTAINS, MATCH_EXACT, MATCH_REGEX
from ..entity.rule import ReplyRule


def match_rule(
    rules: list[ReplyRule], text: str, case_sensitive: bool
) -> ReplyRule | None:
    """按给定顺序遍历规则，返回第一条命中的。没有命中返回 None。"""
    for rule in rules:
        # 命中即返回，所以 sort_order 小的规则优先。
        if is_hit(rule, text, case_sensitive):
            return rule
    return None


def is_hit(rule: ReplyRule, text: str, case_sensitive: bool) -> bool:
    """判断单条规则是否命中这条消息。未知匹配方式一律按不命中处理。"""
    keyword = rule.keyword
    target = text
    # 不区分大小写时先把两边都折成小写，正则也按小写文本跑。
    if not case_sensitive:
        keyword = keyword.lower()
        target = text.lower()

    if rule.match_type == MATCH_EXACT:
        # 完全相等：整条消息就是关键词。
        return target == keyword
    if rule.match_type == MATCH_CONTAINS:
        # 包含：消息里出现关键词即可，适合「校历在哪」这类自然说法。
        return keyword in target
    if rule.match_type == MATCH_REGEX:
        # 正则：写错表达式不该让插件崩，按不命中处理。
        try:
            return re.search(keyword, target) is not None
        except re.error:
            return False
    # 库里存了未知的匹配方式，当作不命中，不猜。
    return False


def validate_match_type(match_type: str) -> bool:
    """页面传来的匹配方式是否在允许集合里。"""
    from ..entity.constants import MATCH_TYPES

    return match_type in MATCH_TYPES
