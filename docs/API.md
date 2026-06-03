# API

Base URL: `http://127.0.0.1:8000`

## `GET /api/health`

返回应用版本和数据库状态。

## `GET /api/i18n/locales`

返回支持的语言列表。当前支持：

```text
zh-CN, zh-TW, ja-JP, ko-KR, en-US, fr-FR, it-IT
```

## `POST /api/schedules/generate`

生成任务时间和完整 OpenClaw 模板，不写数据库。

```json
{
  "start_time": "15:30",
  "end_time": "16:30",
  "task_count": 3,
  "interval_min": 10,
  "products": ["三丰粗糙度仪SJ-310", "泰勒霍普森 Surtronic S-116粗糙度仪", "MINITEST725 EPK涂层测厚仪"],
  "manual_times": ["15:33", "15:44", "15:55"],
  "locale": "zh-CN"
}
```

## `POST /api/schedules/save`

保存生成批次，并累计产品使用次数。请求字段同 generate，额外需要：

```json
{
  "rendered_text": "完整模板文本",
  "batch_name": "可选批次名称"
}
```

## `GET /api/products/stats`

返回产品计划使用次数，支持 `limit`。

## `GET /api/products/recent`

返回最近保存过的产品名。

## `GET /api/templates/current`

返回当前模板版本、hash 和模板主体。

Query:

```text
locale=zh-CN
```

## `POST /api/templates/preview`

同 `/api/schedules/generate`，用于前端预览。

## `GET /api/docs`

返回 README 和 `docs/*.md` 文档索引。源码运行时读取项目根目录；Windows onedir exe 运行时读取 exe 同目录。

## `GET /api/docs/{slug}`

返回指定 Markdown 文档内容。`slug` 来自 `/api/docs` 的返回值。

## 控制面板数据库接口

所有数据库写操作都需要确认令牌 `CONFIRM`，写入前会自动备份 SQLite 到 `articleops-runtime/backups/`。

```text
GET    /api/admin/database/summary
GET    /api/admin/database/tables
GET    /api/admin/database/tables/{table}/rows
POST   /api/admin/database/tables/{table}/rows
PATCH  /api/admin/database/tables/{table}/rows/{row_id}
DELETE /api/admin/database/tables/{table}/rows/{row_id}?confirm=CONFIRM
```

写入请求：

```json
{
  "confirm": "CONFIRM",
  "values": {
    "product_name": "产品名",
    "usage_count": 1
  }
}
```

允许访问的表：

```text
template_versions
schedule_batches
schedule_items
product_usage
```
