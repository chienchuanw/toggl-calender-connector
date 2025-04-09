# toggl Calendar Connector

一個將 toggl 工時追蹤記錄同步到 Google 日曆的命令行工具。

## 功能

- 從 toggl 獲取工時記錄
- 將這些記錄轉換為 Google 日曆事件
- 支持自定義日期範圍
- 提供預覽模式
- 完整的命令行介面

## 安裝

### 先決條件

- Python 3.12 或更高版本
- Poetry 包管理器

### 步驟

1. 克隆此倉庫：

```bash
git clone https://github.com/yourusername/toggl-calendar-connector.git
cd toggl-calendar-connector
```

2. 使用 Poetry 安裝依賴：

```bash
poetry install
```

3. 設置環境變數：

複製 `.env.template` 到 `.env` 並填寫以下信息：

```
TOGGL_API_TOKEN=your_toggl_api_token
TOGGL_WORKSPACE_ID=your_toggl_workspace_id
GOOGLE_CALENDAR_ID=your_google_calendar_id
```

4. 設置 Google 認證：

按照 [Google Calendar API 快速入門](https://developers.google.com/calendar/quickstart/python) 指南獲取 `credentials.json` 文件並將其放在項目根目錄中。

## 使用方法

### 命令行界面

同步今天的時間條目：

```bash
poetry run toggl-calendar sync
```

同步特定日期：

```bash
poetry run toggl-calendar sync --start-date 2025-04-01 --end-date 2025-04-07
```

同步過去 7 天：

```bash
poetry run toggl-calendar sync --days 7
```

預覽模式（不實際創建事件）：

```bash
poetry run toggl-calendar sync --days 3 --preview
```

顯示版本信息：

```bash
poetry run toggl-calendar version
```

### 幫助

獲取更多幫助：

```bash
poetry run toggl-calendar --help
poetry run toggl-calendar sync --help
```

## 許可證

MIT
