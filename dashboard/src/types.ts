// 页面层：和后端约定的数据形状，字段名与 entity/rule.py 的 to_dict 一致。

export type MatchType = "exact" | "contains" | "regex";

export interface Rule {
  id: number;
  keyword: string;
  match_type: MatchType;
  reply: string;
  enabled: boolean;
  sort_order: number;
}

export interface RuleListResponse {
  rules: Rule[];
}

export interface Settings {
  enable: boolean;
  platforms: string[];
  case_sensitive: boolean;
  welcome_enable: boolean;
  welcome_reply: string;
  fallback_enable: boolean;
  fallback_reply: string;
}

// 匹配方式的中文标签。后端只认英文值，展示用它。
export const MATCH_LABELS: Record<MatchType, string> = {
  exact: "完全相等",
  contains: "包含",
  regex: "正则",
};
