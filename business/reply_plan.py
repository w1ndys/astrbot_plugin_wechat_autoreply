# 业务层：收到一条消息后要回什么。决定优先级，不做 IO。
#
# 公众号的被动回复在一次请求里只能返回一条消息，所以这里始终返回单条文本，
# 需要同时说两件事时用空行拼在一起，而不是返回多段。

from ..entity.rule import ReplyRule
from .matcher import match_rule


def build_reply(
    *,
    text: str,
    rules: list[ReplyRule],
    case_sensitive: bool,
    first_seen: bool,
    welcome_enable: bool,
    welcome_reply: str,
    fallback_enable: bool,
    fallback_reply: str,
) -> str | None:
    """返回要回复的文本；返回 None 表示这条消息交给后续流程（比如模型）。"""
    parts: list[str] = []

    # 首条消息先打招呼。欢迎语和关键词命中会合并成一条发出去。
    if first_seen and welcome_enable and welcome_reply.strip():
        parts.append(welcome_reply.strip())

    hit = match_rule(rules, text, case_sensitive)
    # 命中关键词：关键词回复优先级最高，直接结束，不再看兜底。
    if hit is not None:
        parts.append(hit.reply)
        return "\n\n".join(parts) if parts else None

    # 没命中关键词且开启了兜底：用固定文案接住这条消息。
    # 注意这会终止事件传播，也就是该渠道不再走模型。
    if fallback_enable and fallback_reply.strip():
        parts.append(fallback_reply.strip())
        return "\n\n".join(parts) if parts else None

    # 只有欢迎语（首条消息 + 没命中关键词 + 没开兜底）：照发，但这条也不会
    # 再把同一个问题交给模型，因为被动回复只能发一条。
    if parts:
        return "\n\n".join(parts)
    return None
