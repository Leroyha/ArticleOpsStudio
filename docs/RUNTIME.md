# 运行目录与打包约定

ArticleOps Studio 的运行期文件统一放在软件同目录下的 `articleops-runtime/`。源码开发时，该目录位于项目根目录；打包成 exe 后，该目录位于 exe 同级目录。

## 目录结构

```text
articleops-runtime/
  data/        # SQLite 数据库
  logs/        # 应用日志
  cache/       # 进程缓存、UV/Python 缓存指向位置
  temp/        # 运行临时文件
  exports/     # 后续导出文件
  evidence/    # 后续运行证据、截图、回执等
  backups/     # 数据库写操作前的自动备份
  docs/        # 可选运行期文档副本
```

## 路径规则

- 默认运行目录：`<软件所在目录>/articleops-runtime`
- 数据库：`articleops-runtime/data/articleops.sqlite`
- 日志：`articleops-runtime/logs/articleops.log`
- 备份：`articleops-runtime/backups/articleops-*.sqlite`
- 临时目录：启动后进程内 `TEMP`、`TMP`、`TMPDIR` 指向 `articleops-runtime/temp`
- 缓存目录：启动后进程内 `XDG_CACHE_HOME`、`UV_CACHE_DIR` 指向 `articleops-runtime/cache`

## 环境变量覆盖

如果需要把运行数据放到其它位置，可以在启动前设置：

```powershell
$env:ARTICLEOPS_RUNTIME_DIR="D:\ArticleOpsRuntime"
uv run articleops
```

打包发布时不建议把 `articleops-runtime/` 放进安装包。首次启动会自动创建结构。

## 开发启动建议

如果希望 `uv run` 自身的缓存也进入 `articleops-runtime/cache/uv`，优先使用项目根目录的 `start.bat` 启动。直接执行 `uv run articleops` 时，UV 进程的缓存可能在应用启动前已经由 UV 自己决定。
