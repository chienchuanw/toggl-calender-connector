import sys
import typer
from datetime import datetime, timedelta
from typing import Optional
from rich.prompt import Confirm
from rich.table import Table
from rich.box import ASCII

from src.clients.toggl_client import TogglClient
from src.clients.google_client import get_calendar_service
from src.utils.google_calendar import create_event
from utils.formatter import format_time_display, calculate_duration, generate_header
from handlers.menu import return_to_menu
from theme.cyberpunk import console


def sync(
    start_date: Optional[str] = typer.Option(None, "--start-date", "-s"),
    end_date: Optional[str] = typer.Option(None, "--end-date", "-e"),
    days: int = typer.Option(0, "--days", "-d"),
    preview: bool = typer.Option(False, "--preview", "-p"),
    check_duplicate: bool = typer.Option(
        True, "--check-duplicate/--no-check-duplicate"
    ),
):
    """
    同步 Toggl 時間條目到 Google Calendar。
    """
    console.clear()
    console.print(
        f"[bright_green]{generate_header('Sync Mode', 'banner')}[/bright_green]"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    today = datetime.today().date()

    if days > 0:
        if start_date or end_date:
            console.print(
                "[bright_red]>>> 錯誤：不能同時指定 days 和 start_date/end_date[/bright_red]"
            )
            raise typer.Exit(code=1)
        calculated_start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    else:
        calculated_start_date = start_date if start_date else today.strftime("%Y-%m-%d")
        end_date_str = end_date if end_date else calculated_start_date

    console.print(
        f"[bright_green]>>> 準備同步: {calculated_start_date} 到 {end_date_str}[/bright_green]\n"
    )

    try:
        client = TogglClient()
        with console.status(
            "[bright_green]>>> 正在取得 toggl 時間條目...[/bright_green]",
            spinner="dots",
        ):
            entries = client.get_time_entries(calculated_start_date, end_date_str)

        if not entries:
            console.print("[bright_yellow]>>> 警告: 找不到時間條目！[/bright_yellow]")
            return return_to_menu()

        console.print(
            f"[bright_green]>>> 找到 {len(entries)} 個時間條目[/bright_green]\n"
        )

        table = Table(title="時間條目清單", box=ASCII, border_style="bright_green")
        table.add_column("事件", style="bright_green")
        table.add_column("開始時間", style="bright_green")
        table.add_column("結束時間", style="bright_green")
        table.add_column("時長", style="bright_green")

        for entry in entries:
            table.add_row(
                entry["description"],
                format_time_display(entry["start"]),
                format_time_display(entry["end"]),
                calculate_duration(entry["start"], entry["end"]),
            )
        console.print(table)
        console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")

        if preview:
            console.print(
                "[bright_yellow]>>> 預覽模式: 不會創建實際事件[/bright_yellow]"
            )
            return return_to_menu()

        if not Confirm.ask(
            "[bright_green]>>> 是否要繼續同步到 Google 日曆？[/bright_green]",
            default=True,
        ):
            console.print("[bright_yellow]>>> 同步已取消[/bright_yellow]")
            return return_to_menu()

        with console.status(
            "[bright_green]>>> 連接到 Google Calendar...[/bright_green]", spinner="dots"
        ) as status:
            service = get_calendar_service()
            total_created = 0
            total_skipped = 0

            for i, entry in enumerate(entries, 1):
                status.update(
                    f"[bright_green]>>> 處理事件 {i}/{len(entries)}...[/bright_green]"
                )
                result = create_event(
                    service,
                    entry["description"],
                    entry["start"],
                    entry["end"],
                    check_duplicate=check_duplicate,
                )
                if check_duplicate and result and result.get("is_existing", False):
                    total_skipped += 1
                else:
                    total_created += 1

        console.print(
            f"\n[bright_green]>>> 成功! 新建事件: {total_created}, 跳過重複: {total_skipped}[/bright_green]"
        )
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
        return return_to_menu()

    except Exception as e:
        console.print(f"[bright_red]>>> 錯誤: {e}[/bright_red]")
        return return_to_menu()
