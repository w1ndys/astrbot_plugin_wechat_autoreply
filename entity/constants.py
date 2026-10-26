# 实体层：固定值。改这里会同时影响存储、匹配与页面展示，所以集中放一处。

# 插件名既用于 WebUI 路由前缀，也用于数据目录，必须与 metadata.yaml 的 name 一致。
PLUGIN_NAME = "astrbot_plugin_wechat_autoreply"

# 业务库文件名。放在 AstrBot 的 data/plugin_data/<插件名>/ 下。
DB_FILENAME = "wechat_autoreply.db"

# 三种匹配方式。页面下拉框直接展示这三个值，所以是稳定的对外字符串。
MATCH_EXACT = "exact"
MATCH_CONTAINS = "contains"
MATCH_REGEX = "regex"

# 允许写进库的匹配方式集合。写入前用它校验，防止页面传来未知值。
MATCH_TYPES = (MATCH_EXACT, MATCH_CONTAINS, MATCH_REGEX)
