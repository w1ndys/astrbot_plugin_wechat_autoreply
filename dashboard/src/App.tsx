// 页面层：一个视图里用 Tabs 装两块业务，不改顶层 hash。

import { Tabs } from "antd";
import RulesView from "./rules-view";
import SettingsView from "./settings-view";

export default function App() {
  return (
    <div className="app-shell">
      <Tabs
        defaultActiveKey="rules"
        destroyOnHidden
        items={[
          { key: "rules", label: "关键词规则", children: <RulesView /> },
          { key: "settings", label: "全局设置", children: <SettingsView /> },
        ]}
      />
    </div>
  );
}
