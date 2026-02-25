# NEWSFEED

面向中国旅游行业增长/营销团队的资讯自动化产品（周一、周四 08:30 北京时间发送邮件）。

核心能力：
- 抓取多源资讯（政策/监管/公司/媒体）
- 严格可信过滤（无可追溯链接即丢弃）
- 输出 `<=300字` 必读 + 可点击详细网页（GitHub Pages）
- 保留过滤掉的观点与链接（`filtered_items.jsonl`）
- 收集反馈邮件并落库（模板优先，失败走自由文本解析）
- 可扩展：来源、权重、阈值均可配置

## 1. 本地准备

```powershell
.\scripts\bootstrap_env.ps1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

编辑 `.env`，至少填入：
- `OPENAI_API_KEY`
- `SMTP_PASS` (Gmail 应用专用密码)
- `IMAP_PASS` (同上，可与 SMTP 一样)

## 2. 本地运行

```powershell
newsfeed pull-feedback
newsfeed run --page-url http://localhost/
```

产物：
- `reports/digest-YYYY-MM-DD.md`
- `docs/index.html`
- `data/items.jsonl`
- `data/filtered_items.jsonl`
- `data/feedback.jsonl`

## 3. GitHub Actions + Pages（推荐主运行）

1. 新建 private 仓库并推送代码。  
2. 在仓库 `Settings -> Secrets and variables -> Actions` 创建以下 secrets：
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL`（默认 `https://api.openai.com/v1`）
   - `OPENAI_MODEL`（如 `gpt-4o-mini`）
   - `OPENAI_DAILY_CALL_LIMIT`（默认 `10`）
   - `OPENAI_MAX_OUTPUT_TOKENS`（默认 `800`）
   - `SMTP_HOST`=`smtp.gmail.com`
   - `SMTP_PORT`=`587`
   - `SMTP_USER`=`pishikaka1609@gmail.com`
   - `SMTP_PASS`=`你的应用专用密码`
   - `MAIL_FROM`=`pishikaka1609@gmail.com`
   - `MAIL_TO`=`lyuan1609@163.com`
   - `IMAP_HOST`=`imap.gmail.com`
   - `IMAP_PORT`=`993`
   - `IMAP_USER`=`pishikaka1609@gmail.com`
   - `IMAP_PASS`=`你的应用专用密码`
   - `FEEDBACK_SUBJECT_PREFIX`=`[NEWSFEED-FEEDBACK]`
3. 仓库 `Settings -> Pages`，Source 选择 `GitHub Actions`。  
4. 进入 `Actions`，手动运行 `newsfeed-digest` 一次验证。  
5. 之后将按 cron 自动运行：`周一/周四 08:30 (Asia/Shanghai)`。

## 4. Gmail 授权说明

使用 Gmail 两步验证后，创建应用专用密码。该密码填到 `SMTP_PASS` 和 `IMAP_PASS`，不要使用邮箱登录密码。

## 5. 反馈邮件格式

回邮件标题包含前缀：`[NEWSFEED-FEEDBACK]`

模板示例：
```text
保留: 同程与携程的节假日拉新策略对比
删除: 某条纯营销软文
原因: 关注可直接影响拉新与ROI的信息
```

也支持自由文本回复，系统会尽力解析并落库。

## 6. 关键配置入口

- 来源与权重：`config/sources.yaml`
- 严格过滤规则：`src/newsfeed/filtering.py`
- 模型用量限制：`.env` 中的 `OPENAI_DAILY_CALL_LIMIT` 和 `OPENAI_MAX_OUTPUT_TOKENS`

## 7. Windows 本地定时（备用）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_task.ps1
```

如果新开终端找不到 `git` 或 `python`，先执行：
```powershell
.\scripts\bootstrap_env.ps1
```

## 8. 变更审计约定

项目内文件新增或修改后，应同步记录到 `CHANGELOG.md`，包含：
- 变更时间
- 变更文件
- 易懂批注（便于 review）
