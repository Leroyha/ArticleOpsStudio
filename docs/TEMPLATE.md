# OpenClaw 模板维护

当前模板在：

```text
src/articleops_studio/templates.py
```

模板支持语言：

```text
zh-CN, zh-TW, ja-JP, ko-KR, en-US, fr-FR, it-IT
```

模板原则：

- 不固定 5 篇，按实际列表渲染。
- 不做固定账号、公司、文章来源、所在地区校验。
- 强调每篇独立 cron、独立验收、独立记账、独立飞书回执。
- 明确 `cron run ok` 不等于文章发布成功。
- 保留正文可见编辑器、字段读回、提交前校验、收尾流程等硬闸门。

模板版本和 hash 会写入 SQLite，便于后续追踪历史批次使用了哪个模板。

多语言规则：

- 模板说明文字随 `locale` 切换。
- 产品名称保持用户输入原文。
- `OpenClaw`、`SQLite`、表名、脚本名、`browser profile=user` 等技术关键字不翻译。
- 保存批次时写入 `template_locale` 和对应语言的 `template_hash`。
