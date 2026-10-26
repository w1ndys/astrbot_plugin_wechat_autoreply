// 页面层：关键词规则的增删改查。规则表在后端 SQLite 里，这里只做展示与提交。

import { useCallback, useEffect, useState } from "react";
import {
  App as AntApp,
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
} from "antd";
import type { TableProps } from "antd";
import { apiGet, apiPost, readError } from "./bridge";
import { MATCH_LABELS, type MatchType, type Rule, type RuleListResponse } from "./types";

// 编辑弹窗里的表单值。id 为 0 表示新增。
interface RuleFormValues {
  id?: number;
  keyword: string;
  match_type: MatchType;
  reply: string;
  enabled: boolean;
  sort_order: number;
}

const MATCH_OPTIONS = (Object.keys(MATCH_LABELS) as MatchType[]).map((value) => ({
  value,
  label: MATCH_LABELS[value],
}));

export default function RulesView() {
  const { message } = AntApp.useApp();
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm<RuleFormValues>();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // 后端返回 { rules: [...] }，按 id 升序给出
      const data = await apiGet<RuleListResponse>("rules");
      setRules(data.rules ?? []);
    } catch (error) {
      message.error(readError(error));
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => {
    void load();
  }, [load]);

  const openCreate = () => {
    // 新增时把排序放在末尾，避免同序号时和已有规则抢
    form.setFieldsValue({
      id: 0,
      keyword: "",
      match_type: "contains",
      reply: "",
      enabled: true,
      sort_order: rules.length,
    });
    setOpen(true);
  };

  const openEdit = (rule: Rule) => {
    form.setFieldsValue({ ...rule, id: rule.id });
    setOpen(true);
  };

  const submit = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      await apiPost("rules/save", values);
      message.success("已保存");
      setOpen(false);
      await load();
    } catch (error) {
      message.error(readError(error));
    } finally {
      setSaving(false);
    }
  };

  const remove = async (rule: Rule) => {
    try {
      await apiPost("rules/delete", { id: rule.id });
      message.success("已删除");
      await load();
    } catch (error) {
      message.error(readError(error));
    }
  };

  const columns: TableProps<Rule>["columns"] = [
    {
      title: "关键词",
      dataIndex: "keyword",
      // 关键词可能很长，截断显示，完整值在编辑弹窗里看
      render: (value: string) => <code className="keyword-cell">{value}</code>,
    },
    {
      title: "匹配方式",
      dataIndex: "match_type",
      width: 110,
      render: (value: MatchType) => <Tag>{MATCH_LABELS[value] ?? value}</Tag>,
    },
    {
      title: "回复内容",
      dataIndex: "reply",
      // 回复可能带换行和多行链接，表格里只给单行预览
      render: (value: string) => (
        <span className="reply-cell">{value.replace(/\s+/g, " ")}</span>
      ),
    },
    {
      title: "启用",
      dataIndex: "enabled",
      width: 80,
      render: (value: boolean) => (value ? <Tag color="green">是</Tag> : <Tag>否</Tag>),
    },
    { title: "排序", dataIndex: "sort_order", width: 80 },
    {
      title: "操作",
      width: 140,
      render: (_value, rule) => (
        <Space size="small">
          <Button size="small" onClick={() => openEdit(rule)}>
            编辑
          </Button>
          <Popconfirm title="删除这条规则？" onConfirm={() => remove(rule)}>
            <Button size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space className="toolbar">
        <Button type="primary" onClick={openCreate}>
          新增规则
        </Button>
        <Button onClick={() => void load()} loading={loading}>
          刷新
        </Button>
        <span className="toolbar-hint">
          命中即回复并终止后续处理；排序小的优先，按平台适配器过滤见「全局设置」
        </span>
      </Space>

      <Table<Rule>
        rowKey="id"
        size="small"
        loading={loading}
        dataSource={rules}
        columns={columns}
        pagination={false}
      />

      <Modal
        title={form.getFieldValue("id") ? "编辑规则" : "新增规则"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => void submit()}
        confirmLoading={saving}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" className="rule-form">
          <Form.Item name="id" hidden>
            <InputNumber />
          </Form.Item>
          <Form.Item
            name="keyword"
            label="关键词 / 正则"
            rules={[{ required: true, message: "请填写关键词" }]}
          >
            <Input placeholder="例如：查空教室" />
          </Form.Item>
          <Form.Item name="match_type" label="匹配方式" rules={[{ required: true }]}>
            <Select options={MATCH_OPTIONS} />
          </Form.Item>
          <Form.Item
            name="reply"
            label="回复内容"
            rules={[{ required: true, message: "请填写回复内容" }]}
          >
            <Input.TextArea autoSize={{ minRows: 4, maxRows: 10 }} />
          </Form.Item>
          <Space size="large">
            <Form.Item name="enabled" label="启用" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="sort_order" label="排序">
              <InputNumber min={0} max={9999} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
