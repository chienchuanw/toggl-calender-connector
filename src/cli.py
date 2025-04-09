#!/usr/bin/env python3
# src/cli.py

import os
import typer
import sys
import pyfiglet
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.box import ASCII, SQUARE
from rich.style import Style
from rich.theme import Theme
from src.clients.toggl_client import TogglClient
from src.clients.google_client import get_calendar_service
from src.utils.google_calendar import create_event

# 定義賽博朋克風格的主題
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

app = typer.Typer(
    help="同步 Toggl 時間條目到 Google 日曆的 CLI 工具", add_completion=False
)
console = Console(theme=cyberpunk_theme, highlight=False)


def generate_header(text: str = "Toggl Calendar", font: str = "slant") -> str:
    """
    使用 pyfiglet 生成 ASCII 藝術風格的標題

    Args:
        text: 要呈現的文字
        font: pyfiglet 字體名稱，默認為 'slant'

    Returns:
        str: ASCII 藝術文字
    """
    try:
        return pyfiglet.figlet_format(text, font=font)
    except Exception as e:
        # 如果指定的字體不存在，則使用默認字體
        return pyfiglet.figlet_format(text)


def display_menu() -> None:
    """顯示交互式選單"""
    console.clear()

    # 使用 pyfiglet 生成 ASCII 藝術標題
    header_art = generate_header("sync toggl ", "isometric4")
    console.print(f"[bright_green]{header_art}[/bright_green]")

    # 大標題
    console.print(">>> TOGGL CALENDAR CONNECTOR v0.1.0", style="title")
    console.print(">>> 控制你的時間，管理你的生產力\n", style="subtitle")

    # 清晰的分隔線
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")

    # 選單項目
    menu_items = [
        {"key": "1", "name": "同步今天的時間條目", "cmd": "sync"},
        {"key": "2", "name": "同步過去 7 天的時間條目", "cmd": "sync --days 7"},
        {"key": "3", "name": "預覽模式（不實際創建事件）", "cmd": "sync --preview"},
        {"key": "4", "name": "自定義同步選項", "cmd": "custom"},
        {"key": "v", "name": "查看版本信息", "cmd": "version"},
        {"key": "q", "name": "退出程序", "cmd": "exit"},
    ]

    # 使用 ASCII 框線的表格
    table = Table(show_header=False, box=ASCII, border_style="bright_green")
    table.add_column("選項", style="bright_green", justify="center")
    table.add_column("描述", style="bright_green")

    for item in menu_items:
        # 進階式顯示端口格式
        table.add_row(
            f"[bright_green]>[/bright_green] {item['key']}",
            f"[bright_green]{item['name']}[/bright_green]",
        )

    console.print(table)
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    # 使用屬性清晰的提示
    choice = Prompt.ask(
        "[bright_green]> 請輸入選擇[/bright_green]",
        choices=[item["key"] for item in menu_items],
        show_choices=False,  # 隱藏默認顯示的選項
    )

    # 處理用戶選擇
    for item in menu_items:
        if item["key"] == choice:
            if item["cmd"] == "exit":
                console.print("[bright_green]>>> 退出系統. 再見![/bright_green]")
                sys.exit(0)
            elif item["cmd"] == "custom":
                handle_custom_sync()
            else:
                # 執行指定的命令
                console.clear()
                sys.argv = ["toggl-calendar"] + item["cmd"].split()
                app()
                break


def handle_custom_sync() -> None:
    """處理自定義同步選項"""
    console.clear()

    # 使用 pyfiglet 生成小型標題
    header_art = generate_header("Custom Sync", "small")
    console.print(f"[bright_green]{header_art}[/bright_green]")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    # 詢問參數
    console.print("[bright_green]> 請輸入日期參數[/bright_green]\n")

    start_date = Prompt.ask(
        "[bright_green]> 開始日期 (YYYY-MM-DD)[/bright_green]",
        default=datetime.today().strftime("%Y-%m-%d"),
    )

    end_date = Prompt.ask(
        "[bright_green]> 結束日期 (YYYY-MM-DD)[/bright_green]", default=start_date
    )

    preview = (
        Prompt.ask(
            "[bright_green]> 預覽模式 (只顯示不創建事件) [y/n][/bright_green]",
            choices=["y", "n"],
            default="n",
            show_choices=False,  # 隱藏默認顯示的選項
        )
        == "y"
    )

    console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]")
    console.print("[bright_green]>>> 設定完成，準備執行...[/bright_green]\n")

    # 顯示設定摘要
    table = Table(box=ASCII, border_style="bright_green")
    table.add_column("參數", style="bright_green")
    table.add_column("值", style="bright_green")

    table.add_row("開始日期", start_date)
    table.add_row("結束日期", end_date)
    table.add_row("預覽模式", "ON" if preview else "OFF")

    console.print(table)
    console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")

    # 使用 rich.prompt.Confirm 而非 Prompt.ask
    continue_process = Confirm.ask(
        "[bright_green]> 確認繼續?[/bright_green]", default=True
    )
    if not continue_process:
        console.print("[bright_green]>>> 操作已取消[/bright_green]")
        display_menu()
        return

    # 構建參數
    args = [
        "toggl-calendar",
        "sync",
        "--start-date",
        start_date,
        "--end-date",
        end_date,
    ]
    if preview:
        args.append("--preview")

    # 執行命令
    console.clear()
    sys.argv = args
    app()


# 同步命令
@app.command()
def sync(
    start_date: Optional[str] = typer.Option(
        None, "--start-date", "-s", help="開始日期，格式為 YYYY-MM-DD"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end-date", "-e", help="結束日期，格式為 YYYY-MM-DD"
    ),
    days: int = typer.Option(
        0, "--days", "-d", help="過去 N 天（與 start_date/end_date 互斥）"
    ),
    preview: bool = typer.Option(
        False, "--preview", "-p", help="預覽模式，不實際創建事件"
    ),
) -> None:
    """
    將 Toggl 時間條目同步到 Google 日曆。

    如果未指定日期，默認使用今天的日期。
    """
    console.clear()

    # 使用 pyfiglet 生成 ASCII 藝術標題
    header_art = generate_header("Sync Mode", "small")
    console.print(f"[bright_green]{header_art}[/bright_green]")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    # 處理日期參數
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

    # 顯示同步信息
    console.print(
        f"[bright_green]>>> 準備同步: {calculated_start_date} 到 {end_date_str}[/bright_green]\n"
    )

    try:
        client = TogglClient()

        with console.status(
            "[bright_green]>>> 正在取得 Toggl 時間條目...[/bright_green]",
            spinner="dots",
        ):
            entries = client.get_time_entries(calculated_start_date, end_date_str)

        if not entries:
            console.print("[bright_yellow]>>> 警告: 找不到時間條目！[/bright_yellow]")
            return

        # 顯示找到的時間條目
        console.print(
            f"[bright_green]>>> 找到 {len(entries)} 個時間條目[/bright_green]\n"
        )

        table = Table(title=f"時間條目清單", box=ASCII, border_style="bright_green")
        table.add_column("描述", style="bright_green")
        table.add_column("開始時間", style="bright_green")
        table.add_column("結束時間", style="bright_green")

        for entry in entries:
            table.add_row(entry["description"], entry["start"], entry["end"])

        console.print(table)
        console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")

        # 在預覽模式下，不創建事件
        if preview:
            console.print(
                "[bright_yellow]>>> 預覽模式: 不會創建實際事件[/bright_yellow]"
            )
            return

        # 確認是否繼續
        continue_sync = Confirm.ask(
            "[bright_green]>>> 是否要繼續同步到 Google 日曆？[/bright_green]",
            default=True,
        )
        if not continue_sync:
            console.print("[bright_yellow]>>> 同步已取消[/bright_yellow]")
            return

        # 連接 Google Calendar 並創建事件
        with console.status(
            "[bright_green]>>> 連接到 Google Calendar...[/bright_green]", spinner="dots"
        ) as status:
            service = get_calendar_service()

            for i, entry in enumerate(entries, 1):
                status.update(
                    f"[bright_green]>>> 正在創建事件 {i}/{len(entries)}...[/bright_green]"
                )

                create_event(
                    service, entry["description"], entry["start"], entry["end"]
                )

        console.print(
            f"\n[bright_green]>>> 成功! 同步了 {len(entries)} 個事件到 Google 日曆[/bright_green]"
        )
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")

    except Exception as e:
        console.print(f"[bright_red]>>> 錯誤: {str(e)}[/bright_red]")
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """顯示版本信息"""
    console.clear()

    # 使用 pyfiglet 生成版本標題
    header_art = generate_header("Version Info", "small")
    console.print(f"[bright_green]{header_art}[/bright_green]")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")

    console.print("\n[bright_green]>>> TOGGL CALENDAR CONNECTOR v0.1.0[/bright_green]")
    console.print(
        "[bright_green]>>> 將 Toggl 時間條目同步到 Google 日曆的工具[/bright_green]\n"
    )

    # 添加類似於示例圖像的標語
    console.print(
        "[bright_green]>>> 控制你的時間. 掌握你的生產力. 奪回你的一天.[/bright_green]"
    )
    console.print(
        "[bright_green]>>> TOGGL CALENDAR CONNECTOR - 賦予你掌控時間的能力[/bright_green]\n"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """主程序回調函數"""
    # 如果沒有提供子命令且是直接運行，顯示選單
    # 這樣在使用 CLI 參數時不會顯示選單
    if ctx.invoked_subcommand is None and len(sys.argv) <= 2:
        display_menu()


if __name__ == "__main__":
    app()
