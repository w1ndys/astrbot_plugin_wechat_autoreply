# 匹配与回复决策：三种匹配方式、非法正则、排序优先、欢迎语与兜底组合。

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = str(ROOT.parent)
# 测试从仓库根的上一级导入包名 astrbot_plugin_wechat_autoreply
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

from astrbot_plugin_wechat_autoreply.business.matcher import is_hit, match_rule
from astrbot_plugin_wechat_autoreply.business.reply_plan import build_reply
from astrbot_plugin_wechat_autoreply.data.rule_store import RuleStore
from astrbot_plugin_wechat_autoreply.data.seen_store import SeenStore
from astrbot_plugin_wechat_autoreply.entity.constants import (
    MATCH_CONTAINS,
    MATCH_EXACT,
    MATCH_REGEX,
)
from astrbot_plugin_wechat_autoreply.entity.rule import ReplyRule


def make_rule(keyword, match_type=MATCH_EXACT, reply="r", order=0, enabled=True):
    """构造一条规则，只关心本次断言用到的字段。"""
    return ReplyRule(0, keyword, match_type, reply, enabled, order)


class MatcherTest(unittest.TestCase):
    # 三种匹配方式与大小写行为

    def test_exact(self) -> None:
        # 精确匹配要求整条消息等于关键词
        rule = make_rule("校历")
        self.assertTrue(is_hit(rule, "校历", False))
        self.assertFalse(is_hit(rule, "看校历", False))

    def test_contains(self) -> None:
        # 包含匹配允许消息里夹带别的话
        rule = make_rule("校历", MATCH_CONTAINS)
        self.assertTrue(is_hit(rule, "校历在哪看", False))
        self.assertFalse(is_hit(rule, "课表", False))

    def test_regex(self) -> None:
        # 正则匹配走 re.search
        rule = make_rule(r"^空教室\s*\d*$", MATCH_REGEX)
        self.assertTrue(is_hit(rule, "空教室 302", False))
        self.assertFalse(is_hit(rule, "今天空教室", False))

    def test_case_sensitive(self) -> None:
        # 不区分大小写时两边都折成小写
        rule = make_rule("Qfnu", MATCH_CONTAINS)
        self.assertTrue(is_hit(rule, "qfnu工具", False))
        self.assertFalse(is_hit(rule, "qfnu工具", True))

    def test_bad_regex_does_not_raise(self) -> None:
        # 写错的正则按不命中处理，不能让插件崩
        rule = make_rule("([", MATCH_REGEX)
        self.assertFalse(is_hit(rule, "任意文本", False))

    def test_unknown_match_type(self) -> None:
        # 库里出现未知匹配方式时不猜，按不命中
        rule = make_rule("校历", "fuzzy")
        self.assertFalse(is_hit(rule, "校历", False))

    def test_order_wins(self) -> None:
        # 多条规则都命中时，排在前面的先赢
        rules = [
            make_rule("校历", MATCH_CONTAINS, reply="A", order=0),
            make_rule("校历", MATCH_CONTAINS, reply="B", order=1),
        ]
        hit = match_rule(rules, "校历", False)
        self.assertIsNotNone(hit)
        self.assertEqual(hit.reply, "A")


class ReplyPlanTest(unittest.TestCase):
    # 欢迎语、关键词、兜底三者的优先级

    def build(self, **kwargs):
        """用一份默认参数调用 build_reply，测试里只覆盖关心的项。"""
        params = dict(
            text="校历",
            rules=[make_rule("校历", MATCH_CONTAINS, reply="校历链接")],
            case_sensitive=False,
            first_seen=False,
            welcome_enable=True,
            welcome_reply="欢迎关注",
            fallback_enable=False,
            fallback_reply="兜底",
        )
        params.update(kwargs)
        return build_reply(**params)

    def test_keyword_hit(self) -> None:
        # 命中关键词就回关键词回复
        self.assertEqual(self.build(), "校历链接")

    def test_no_hit_and_fallback_off(self) -> None:
        # 没命中且兜底关闭时返回 None，交还给模型
        self.assertIsNone(self.build(text="随便聊聊"))

    def test_fallback_on(self) -> None:
        # 兜底开启时任何消息都有固定回复
        self.assertEqual(
            self.build(text="随便聊聊", fallback_enable=True), "兜底"
        )

    def test_first_seen_merges_welcome(self) -> None:
        # 首条消息把欢迎语和关键词回复合并成一条
        self.assertEqual(self.build(first_seen=True), "欢迎关注\n\n校历链接")

    def test_first_seen_only_welcome(self) -> None:
        # 首条消息没命中关键词，只发欢迎语
        self.assertEqual(self.build(text="你好", first_seen=True), "欢迎关注")

    def test_welcome_disabled(self) -> None:
        # 关掉欢迎语后首条消息也只看关键词
        self.assertIsNone(
            self.build(text="你好", first_seen=True, welcome_enable=False)
        )


class StoreTest(unittest.IsolatedAsyncioTestCase):
    # 规则表与首见表的最小落库行为

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "wechat_autoreply.db"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    async def test_rule_crud(self) -> None:
        # 新增后能读到，改完快照跟着变，删掉后消失
        store = RuleStore(self.db_path)
        rule_id = await store.save_rule(make_rule("校历", reply="A"))
        self.assertGreater(rule_id, 0)
        self.assertEqual(len(store.list_rules()), 1)

        updated = ReplyRule(rule_id, "校历", MATCH_EXACT, "B", True, 0)
        await store.save_rule(updated)
        self.assertEqual(store.list_rules()[0].reply, "B")
        self.assertTrue(await store.delete_rule(rule_id))
        self.assertEqual(len(store.list_rules()), 0)

    async def test_disabled_rule_not_matched(self) -> None:
        # 关闭的规则仍在表里，但不进匹配集合
        store = RuleStore(self.db_path)
        await store.save_rule(make_rule("校历", reply="A", enabled=False))
        self.assertEqual(len(store.list_rules()), 1)
        self.assertEqual(len(store.enabled_rules()), 0)

    async def test_seen_first_time_only_once(self) -> None:
        # 同一个 umo 只有第一次返回 True
        store = SeenStore(self.db_path)
        self.assertTrue(await store.mark_seen("weixin:FriendMessage:u1"))
        self.assertFalse(await store.mark_seen("weixin:FriendMessage:u1"))
        self.assertTrue(await store.mark_seen("weixin:FriendMessage:u2"))


if __name__ == "__main__":
    unittest.main()
