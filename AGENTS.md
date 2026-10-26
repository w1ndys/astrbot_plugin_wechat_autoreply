# AGENTS.md

本仓库是 AstrBot 插件 `astrbot_plugin_wechat_autoreply`，面向微信公众号补回后台那套自动回复。

## 默认启用的契约

本仓开发默认启用 `.agents/skills/human-coding-contract/SKILL.md`（人话编码契约 / 土法编码 / 分层交付），不必每次喊触发词。规则见该文件，要点：

- 朴素语法优先，一层只做一件事，不额外加抽象层
- 依赖单向：`main.py` → `business/` → `data/`，`entity/` 不依赖 AstrBot 也不访问数据库
- 单函数不超过 50 行（不含空行与注释）
- 每个文件、函数、声明及其字段、每个 `if`/`else` 分支都要有简短中文注释，条件注释写清"为什么这样判、后果是什么"
- 提交前跑 `python3 -m unittest`（在 `tests/` 下执行）与 `ruff check .`（在仓库根执行）

## 目录

```
entity/     固定值与数据形状
data/       SQLite 连接、建表、规则表与首见表
business/   匹配与回复决策（纯逻辑，可单测）
main.py     插件类：注册 WebUI API + 私聊消息拦截
dashboard/  Pages 前端源码（Vite + React + antd）
views/      Pages 构建产物，AstrBot 只扫 views/<view>/index.html
tests/      纯逻辑与存储的 unittest
```

## 几条不动的约定

- 改动 `_conf_schema.json` 的字段要同步更新 Pages 的「全局设置」页，反之亦然
- 关键词规则表不进 schema，只进 SQLite；schema 只放标量开关与短文本
- 消息命中后一定 `event.stop_event()`：公众号被动回复一次只能回一条，不能让模型再回一条覆盖它
- 测试不 import `astrbot`，只测 `entity/`、`business/`、`data/` 三层
