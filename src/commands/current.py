from datetime import datetime
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.box import ASCII

from src.clients.toggl_client import TogglClient
from utils.formatter import format_time_display, generate_header
from handlers.menu import return_to_menu
from theme.cyberpunk import console


def current():
    """顯示當前正在記錄的 Toggl 時間條目"""
    console.clear()
    console.print(
        f"[bright_green]{generate_header('Current Entry', 'small')}[/bright_green]"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    client = TogglClient()
    with console.status(
        "[bright_green]>>> 正在獲取當前 Toggl 計時...[/bright_green]", spinner="dots"
    ):
        entry = client.get_current_time_entry()

    if not entry:
        console.print(
            "[bright_yellow]>>> 目前沒有正在記錄的 Toggl 時間條目[/bright_yellow]"
        )
        return return_to_menu()

    # 計算已運行時間
    start = datetime.fromisoformat(entry["start"].replace("Z", "+00:00"))
    now = datetime.now(start.tzinfo)
    seconds = int((now - start).total_seconds())
    running_time = (
        f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
    )

    table = Table(title="當前時間條目", box=ASCII, border_style="bright_green")
    table.add_column("屬性", style="cyan")
    table.add_column("值", style="white")

    table.add_row("描述", entry["description"] or "[red]未設置描述[/red]")
    table.add_row("開始時間", format_time_display(entry["start"]))
    table.add_row("已運行時間", running_time)
    table.add_row("專案", entry.get("project", "無"))
    table.add_row("標籤", ", ".join(entry.get("tags", [])) or "無")
    table.add_row("計費", "是" if entry.get("billable") else "否")

    console.print(table)

    # 操作選項
    choice = Prompt.ask(
        "\n[bright_green]> 選擇操作[/bright_green]",
        choices=["1", "2"],
        default="2",
        show_choices=False,
    )

    if choice == "1":
        if Confirm.ask("[bright_green]>>> 確定要停止當前計時嗎？[/bright_green]"):
            with console.status(
                "[bright_green]>>> 正在停止計時...[/bright_green]", spinner="dots"
            ):
                if client.stop_current_time_entry():
                    console.print("[bright_green]>>> 已成功停止計時[/bright_green]")
                else:
                    console.print("[bright_red]>>> 停止計時失敗[/bright_red]")
    return return_to_menu()
