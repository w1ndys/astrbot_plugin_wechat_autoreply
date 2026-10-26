# 入口层：注册 WebUI API，并在私聊消息上做关键词拦截。
# 依赖方向固定为 main → business → data，这里不直接写 SQL。

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools
from astrbot.api.web import error_response, json_response, request

from .business.matcher import validate_match_type
from .business.reply_plan import build_reply
from .data.rule_store import RuleStore
from .data.seen_store import SeenStore
from .entity.constants import DB_FILENAME, PLUGIN_NAME
from .entity.rule import ReplyRule

# 页面能读写的全局字段。密钥类字段不存在，所以不需要过滤。
SETTING_KEYS = (
    "enable",
    "platforms",
    "case_sensitive",
    "welcome_enable",
    "welcome_reply",
    "fallback_enable",
    "fallback_reply",
)


class Plugin(Star):
    """公众号自动回复：关键词、首条欢迎语、兜底回复。"""

    def __init__(self, context: Context, config=None) -> None:
        super().__init__(context)
        self.config = config or {}
        # 显式传插件名，避免从子模块调用时拿不到数据目录。
        data_dir = StarTools.get_data_dir(PLUGIN_NAME)
        db_path = data_dir / DB_FILENAME
        self.rule_store = RuleStore(db_path)
        self.seen_store = SeenStore(db_path)

        context.register_web_api(
            f"/{PLUGIN_NAME}/rules", self.api_list_rules, ["GET"], "列出关键词规则"
        )
        context.register_web_api(
            f"/{PLUGIN_NAME}/rules/save",
            self.api_save_rule,
            ["POST"],
            "新增或更新关键词规则",
        )
        context.register_web_api(
            f"/{PLUGIN_NAME}/rules/delete",
            self.api_delete_rule,
            ["POST"],
            "删除关键词规则",
        )
        context.register_web_api(
            f"/{PLUGIN_NAME}/settings",
            self.api_get_settings,
            ["GET"],
            "读取全局非密钥配置",
        )
        context.register_web_api(
            f"/{PLUGIN_NAME}/settings/save",
            self.api_save_settings,
            ["POST"],
            "写回全局非密钥配置",
        )

    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def on_private_message(self, event: AstrMessageEvent):
        """私聊消息先过关键词；命中或需要兜底时由本插件负责回复。"""
        # 总开关关闭时完全不动，避免影响其它渠道。
        if not self.config.get("enable"):
            return
        # 平台过滤：留空表示所有平台都生效。
        allowed = self.config.get("platforms") or []
        if allowed and event.get_platform_name() not in allowed:
            return
        text = (event.message_str or "").strip()
        # 没有文本内容（纯图片/语音）或是指令，交给后续流程。
        if not text or text.startswith("/"):
            return

        # 先记录「这个会话见过了」，再判断是不是首条，保证并发下只欢迎一次。
        first_seen = await self.seen_store.mark_seen(event.unified_msg_origin)
        reply = build_reply(
            text=text,
            rules=self.rule_store.enabled_rules(),
            case_sensitive=bool(self.config.get("case_sensitive")),
            first_seen=first_seen,
            welcome_enable=bool(self.config.get("welcome_enable")),
            welcome_reply=str(self.config.get("welcome_reply") or ""),
            fallback_enable=bool(self.config.get("fallback_enable")),
            fallback_reply=str(self.config.get("fallback_reply") or ""),
        )
        # 没有可回的内容就放行，让模型或其它插件接手。
        if not reply:
            return
        logger.info("[autoreply] 命中自动回复 platform=%s", event.get_platform_name())
        yield event.plain_result(reply)
        # 已经给出固定回复，终止传播避免再让模型回一条（公众号一次只能回一条）。
        event.stop_event()

    async def api_list_rules(self):
        """规则列表，给页面表格用。"""
        rules = self.rule_store.list_rules()
        return json_response({"rules": [rule.to_dict() for rule in rules]})

    async def api_save_rule(self):
        """新增或更新一条规则。id 为 0 时新增。"""
        payload = await request.json(default={})
        # 不是对象就写不回去。
        if not isinstance(payload, dict):
            return error_response("请求体必须是 JSON 对象", status_code=400)
        keyword = str(payload.get("keyword") or "").strip()
        reply = str(payload.get("reply") or "")
        match_type = str(payload.get("match_type") or "exact")
        # 关键词与回复都不能为空，否则这条规则永远不会命中或回空消息。
        if not keyword or not reply.strip():
            return error_response("关键词和回复不能为空", status_code=400)
        if not validate_match_type(match_type):
            return error_response("匹配方式不合法", status_code=400)
        rule = ReplyRule(
            rule_id=int(payload.get("id") or 0),
            keyword=keyword,
            match_type=match_type,
            reply=reply,
            enabled=bool(payload.get("enabled", True)),
            sort_order=int(payload.get("sort_order") or 0),
        )
        rule_id = await self.rule_store.save_rule(rule)
        return json_response({"id": rule_id})

    async def api_delete_rule(self):
        """按 id 删除规则。"""
        payload = await request.json(default={})
        if not isinstance(payload, dict):
            return error_response("请求体必须是 JSON 对象", status_code=400)
        rule_id = int(payload.get("id") or 0)
        # 没有合法 id 直接拒绝，避免误删。
        if rule_id <= 0:
            return error_response("缺少规则 id", status_code=400)
        deleted = await self.rule_store.delete_rule(rule_id)
        return json_response({"deleted": deleted})

    async def api_get_settings(self):
        """读取全局非密钥配置。每次打开页面都取当前值，不用过期表单回写。"""
        data = {key: self.config.get(key) for key in SETTING_KEYS}
        return json_response(data)

    async def api_save_settings(self):
        """写回全局非密钥配置，保存后立即生效。"""
        payload = await request.json(default={})
        if not isinstance(payload, dict):
            return error_response("请求体必须是 JSON 对象", status_code=400)
        # 只接受白名单里的键，页面传别的字段一律忽略。
        for key in SETTING_KEYS:
            if key in payload:
                self.config[key] = payload[key]
        self.config.save_config()
        logger.info("[autoreply] 全局配置已保存")
        return json_response({"ok": True})
