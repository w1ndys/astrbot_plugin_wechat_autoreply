import React from "react";
import { createRoot } from "react-dom/client";
import { App as AntApp, ConfigProvider } from "antd";
import { StyleProvider } from "@ant-design/cssinjs";
import zhCN from "antd/locale/zh_CN";
import App from "./App";
import "./style.css";

const container = document.getElementById("root");
// 宿主挂载点不存在时直接抛错，避免白屏无提示
if (!container) {
  throw new Error("找不到挂载点 #root");
}

// StyleProvider layer 让 antd 样式整体进 @layer antd，页面自己的 CSS 不用 !important 就能覆盖
createRoot(container).render(
  <React.StrictMode>
    <StyleProvider layer>
      <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: "#1677ff" } }}>
        <AntApp>
          <App />
        </AntApp>
      </ConfigProvider>
    </StyleProvider>
  </React.StrictMode>,
);
