# UI 与资源

软件名：ArticleOps Studio

Logo：

```text
assets/logo/articleops-logo.svg
frontend/public/favicon.svg
```

前端源码：

```text
frontend/src/main.jsx
frontend/src/styles.css
```

设计方向：

- 本地运营工作台，不做营销落地页。
- 左侧配置，中间任务轨道，右侧模板预览，下方统计。
- 使用 GSAP 做面板入场、任务卡片 stagger、复制反馈和统计刷新动效。
- 表单草稿写入 `localStorage`，key 为 `articleops.form.v1`。
- API 请求使用 `cache: "no-store"`，避免统计和模板预览过期。
- 服务端数据库、日志、缓存和临时文件写入 `articleops-runtime/`，前端浏览器缓存仍由浏览器管理。

## 控制面板

顶部状态栏提供“控制面板”入口，不改变主工作台布局。进入后可查看：

- 数据库概览、表结构、表记录。
- 受保护 CRUD，写操作自动备份数据库。
- 语言、主题、颜色设置。
- README 和 `docs/*.md` 内置文档。

## 主题与语言

- 主题：跟随系统、正常浅色、深色。
- 颜色：青色、绿色、紫色、琥珀色。
- 设置写入 `localStorage`，key 为 `articleops.settings.v1`。
- 模板生成请求会携带当前 `locale`。
