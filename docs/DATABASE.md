# SQLite 数据库

默认路径：

```text
articleops-runtime/data/articleops.sqlite
```

可通过环境变量覆盖运行目录：

```powershell
$env:ARTICLEOPS_RUNTIME_DIR="D:\ArticleOpsRuntime"
uv run articleops
```

## 表

`template_versions`：模板版本、内容 hash、激活状态。

`schedule_batches`：一次生成/保存的任务批次。

- `template_locale`：本批次生成模板时使用的语言。
- `template_hash`：对应语言模板内容 hash。

`schedule_items`：批次中的单篇任务，保存时间、产品、顺序。

`product_usage`：产品累计计划次数、首次和最近使用时间。

## 统计口径

当前数据库统计的是 ArticleOps Studio 中“保存过的发文计划”，不是目标平台真实发布成功数。真实发布结果仍以 OpenClaw 执行流程产生的发布记录为准。

## 备份

退出应用后复制 `articleops-runtime/data/articleops.sqlite` 即可备份。恢复时覆盖同名文件。

控制面板执行新增、更新、删除前，会自动复制当前数据库到：

```text
articleops-runtime/backups/
```

## 控制面板写入规则

- 所有表都允许受保护 CRUD。
- API 不接受任意 SQL，只允许访问内置 allowlist 表。
- 删除和更新需要确认令牌 `CONFIRM`。
- 修改 `template_versions.content` 时，`content_hash` 会自动按内容重新计算。
