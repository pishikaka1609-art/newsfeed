# CHANGELOG

## 2026-02-25 09:10:53 +08:00

- 新增 `requirements.txt` 与 `pyproject.toml`。
批注: 建立可安装 Python 项目，支持 `newsfeed` 命令行入口。

- 新增配置模板 `.env.example` 与来源配置 `config/sources.yaml`。
批注: 固化你的邮箱、调度、模型限额、来源优先级和核心客户名单，便于后续调整。

- 新增核心代码模块 `src/newsfeed/*`。
批注: 包含抓取、打分过滤、严格丢弃日志、摘要生成、报告生成、邮件发送、反馈回收全链路。

- 新增 GitHub Actions 工作流 `.github/workflows/digest.yml`。
批注: 周一/周四 08:30（北京时间）自动执行并发布 GitHub Pages 详细版。

- 新增本地脚本 `scripts/run_local.ps1` 与 `scripts/register_task.ps1`。
批注: 支持 Windows 本地一键执行与任务计划程序备用调度。

- 新增 `README.md` 与 `.gitignore`。
批注: 提供从零部署说明，并控制数据/密钥文件不入库。

## 2026-02-25 09:13:17 +08:00

- 更新 `src/newsfeed/feedback.py`、`src/newsfeed/filtering.py`、`src/newsfeed/pipeline.py`、`src/newsfeed/storage.py`。
批注: 新增“反馈偏好词驱动排序”能力（保留词加分、删除词减分），并将偏好写入状态，支持持续迭代。

- 新增 `docs/index.html` 与 `docs/.nojekyll`。
批注: 保证 GitHub Pages 在首次运行前也有可访问占位页，减少配置歧义。

## 2026-02-25 09:13:45 +08:00

- 更新 `README.md`。
批注: 增加“变更审计约定”章节，明确每次改动都需写入 changelog 供你 review。

## 2026-02-25 09:17:44 +08:00

- Rewrote `src/newsfeed/summarizer.py` and `src/newsfeed/report.py`.
Note: Fixed encoding corruption that could break Python syntax and report rendering.

- Rewrote `config/sources.yaml` with ASCII-safe content and Unicode escapes.
Note: Avoided YAML parsing failures and kept Chinese entity matching support.

- Rewrote `src/newsfeed/filtering.py` and `src/newsfeed/emailer.py`; updated `src/newsfeed/feedback.py`.
Note: Stabilized string handling, kept strict filtering logic, and added bilingual (CN/EN) feedback template parsing.

## 2026-02-25 09:28:46 +08:00

- Added `scripts/bootstrap_env.ps1`; updated `README.md`.
Note: Added a reliable session bootstrap for `git/python` when Windows PATH has not refreshed yet.

## 2026-02-28 23:22:22 +08:00

- Updated `src/newsfeed/summarizer.py`.
Note: Added hard fallback to rule-based summary when model calls fail (429 quota, network error, provider errors), so pipeline no longer crashes.

- Updated `requirements.txt` and `pyproject.toml`.
Note: Added `tzdata` dependency to prevent `ZoneInfoNotFoundError` on Windows/Python environments without system tz database.
