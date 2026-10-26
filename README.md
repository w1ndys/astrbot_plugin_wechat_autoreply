# astrbot_plugin_wechat_autoreply

AstrBot 插件：给微信公众号补回后台那套自动回复。用中文交流。

## 为什么需要它

启用微信「服务器配置」把消息接到 AstrBot 之后，公众平台后台的**自动回复全部失效**，菜单点击事件也收不到——官方文档原话是「用户发送的消息将转发至该地址，网站中设置的自动回复和自定义菜单将失效」。

AstrBot 本身能接消息、能让人格回话，但固定内容（校历链接、工具入口、群号）交给模型回答既慢又不稳：会被改写、会漏字、会编日期，还每条都烧 token。这个插件把这些固定内容搬回代码层。

## 三层职责

| 层 | 谁负责 | 适合什么 |
|---|---|---|
| 固定内容 | 本插件（关键词/欢迎语/兜底） | 校历链接、【查空教室】、菜单说明、群号 |
| 半固定内容 | AstrBot 知识库（RAG） | 政策原文、办事流程这类需要检索理解的长内容 |
| 开放对话 | AstrBot 人格 prompt | 身份、语气、答不了时怎么引导 |

## 功能

- **关键词回复**：完全相等 / 包含 / 正则三种匹配，命中即回复并终止事件传播，不消耗模型
- **首条欢迎语**：某个用户在该平台第一次发消息时回一条欢迎语（关注事件 `subscribe` 不会被 AstrBot 转给插件，所以用首条消息近似代替「被关注回复」）
- **兜底回复**：未命中关键词时的固定文案。默认关闭——开启后该渠道的模型对话会被这条兜底完全取代

规则表存在插件自己的 SQLite（`data/plugin_data/astrbot_plugin_wechat_autoreply/wechat_autoreply.db`），在插件页的「关键词规则」页增删改查。

## 安装

把仓库放到 `AstrBot/data/plugins/astrbot_plugin_wechat_autoreply`，在 WebUI 插件页重载。无第三方依赖。

## 配置

全局开关与文案在插件配置页（`_conf_schema.json`）：

| 键 | 说明 |
|---|---|
| `enable` | 总开关，默认关闭 |
| `platforms` | 生效的平台适配器名，默认 `["weixin_official_account"]`，留空表示所有平台 |
| `case_sensitive` | 关键词是否区分大小写，默认不区分 |
| `welcome_enable` / `welcome_reply` | 首条消息欢迎语开关与内容 |
| `fallback_enable` / `fallback_reply` | 兜底回复开关与内容，默认关闭 |

关键词规则在插件页的「关键词规则」页维护，不进配置文件。

## 已知限制

- 公众号被动回复一次只能返回一条消息，所以欢迎语与关键词回复会合并成一条（空行分隔）发出去
- 图片/语音等非文本消息不参与关键词匹配，直接放行
- 以 `/` 开头的消息放行，留给 AstrBot 指令系统

## 开发

```bash
# 后端测试（在 tests/ 下执行）
cd tests && python3 -m unittest

# 代码检查（在仓库根执行）
ruff check .

# 前端构建：产物直接落到 views/console/
cd dashboard && pnpm install && pnpm build
```

前端技术栈：React 19 + antd 6 + TypeScript 6 + Vite 8，打成一份 IIFE 单文件（AstrBot 只稳定改写 HTML 的 `src`/`href`，运行时不走 CDN）。
