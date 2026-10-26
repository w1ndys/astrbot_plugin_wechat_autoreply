// 页面层：全局非密钥配置。手写字段，不按 schema 自动生成表单。

import { useCallback, useEffect, useState } from "react";
import { App as AntApp, Button, Divider, Form, Input, Select, Space, Switch } from "antd";
import { apiGet, apiPost, readError } from "./bridge";
import type { Settings } from "./types";

export default function SettingsView() {
  const { message } = AntApp.useApp();
  const [form] = Form.useForm<Settings>();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // 每次打开都取后端当前值，不用过期表单回写
      const data = await apiGet<Settings>("settings");
      form.setFieldsValue(data);
    } catch (error) {
      message.error(readError(error));
    } finally {
      setLoading(false);
    }
  }, [form, message]);

  useEffect(() => {
    void load();
  }, [load]);

  const submit = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      await apiPost("settings/save", values);
      message.success("已保存");
    } catch (error) {
      message.error(readError(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Form form={form} layout="vertical" className="settings-form" disabled={loading}>
      <Form.Item
        name="enable"
        label="启用自动回复"
        valuePropName="checked"
        extra="总开关。关闭时插件不处理任何消息。"
      >
        <Switch />
      </Form.Item>

      <Form.Item
        name="platforms"
        label="生效的平台适配器"
        extra="按平台适配器名过滤，留空表示所有平台。公众号是 weixin_official_account。"
      >
        <Select mode="tags" placeholder="weixin_official_account" />
      </Form.Item>

      <Form.Item
        name="case_sensitive"
        label="关键词区分大小写"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Divider plain />
      <div className="section-title">首条消息欢迎语</div>

      <Form.Item
        name="welcome_enable"
        label="启用欢迎语"
        valuePropName="checked"
        extra="微信的关注事件不会转给插件，所以用「该用户第一次发消息」近似代替后台的「被关注回复」。"
      >
        <Switch />
      </Form.Item>

      <Form.Item name="welcome_reply" label="欢迎语内容">
        <Input.TextArea autoSize={{ minRows: 4, maxRows: 12 }} />
      </Form.Item>

      <Divider plain />
      <div className="section-title">兜底回复</div>

      <Form.Item
        name="fallback_enable"
        label="启用兜底回复"
        valuePropName="checked"
        extra="开启后未命中关键词的消息也会回固定文案，并终止事件传播——这个渠道的模型对话会被完全取代。想保留 AI 对话就保持关闭。"
      >
        <Switch />
      </Form.Item>

      <Form.Item name="fallback_reply" label="兜底回复内容">
        <Input.TextArea autoSize={{ minRows: 3, maxRows: 10 }} />
      </Form.Item>

      <Space>
        <Button type="primary" loading={saving} onClick={() => void submit()}>
          保存设置
        </Button>
        <Button onClick={() => void load()}>重新读取</Button>
      </Space>
    </Form>
  );
}
