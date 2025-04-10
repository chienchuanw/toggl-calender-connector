from rich.console import Console
from rich.theme import Theme

# 定義自訂主題
cyberpunk_theme = Theme(
    {
        "success": "bright_green",
        "error": "bright_red",
        "warning": "bright_yellow",
        "info": "bright_green",
        "panel.border": "bright_green",
        "panel.title": "bright_green",
        "prompt": "bright_green",
        "title": "bright_green on black",
        "subtitle": "bright_green",
        "menu.item": "bright_green",
        "menu.number": "bright_green",
        "menu.border": "bright_green",
        "table.border": "bright_green",
        "progress.bar": "bright_green",
    }
)

# 初始化 Console 實例，整個 CLI 專案都可以 import 使用這個 console
console = Console(theme=cyberpunk_theme, highlight=False)
