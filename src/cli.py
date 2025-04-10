#!/usr/bin/env python3
# src/cli.py

import os
import typer
import sys
import pyfiglet
import pytz
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
from src.utils.google_calendar import create_event, list_calendars, update_calendar_id

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
    help="同步 toggl 時間條目到 Google 日曆的 CLI 工具", add_completion=False
)
console = Console(theme=cyberpunk_theme, highlight=False)


def return_to_menu(message: str = "按 Enter 返回主選單") -> None:
    """
    顯示提示訊息並返回主選單
    
    Args:
        message: 要顯示的提示訊息，默認為「按 Enter 返回主選單」
    """
    console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]")
    Prompt.ask(f"[bright_green]>>> {message}[/bright_green]", default="")
    display_menu()
    return


def format_time_display(time_str: str) -> str:
    """
    將 ISO 格式的時間字串轉換為更易讀的格式
    格式化為 YYYY-MM-DD hh:mm:ss AM/PM (台灣時間)

    Args:
        time_str: ISO 格式的時間字串

    Returns:
        str: 格式化後的時間字串
    """
    try:
        # 解析 ISO 格式時間
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))

        # 轉換為台灣時區
        taiwan_tz = pytz.timezone("Asia/Taipei")
        dt = dt.astimezone(taiwan_tz)

        # 格式化為所需格式 YYYY-MM-DD hh:mm:ss AM/PM
        return dt.strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception as e:
        # 如果解析失敗，返回原始字串
        return time_str


def calculate_duration(start_time: str, end_time: str) -> str:
    """
    計算兩個時間點之間的持續時間，並以 HH:MM:SS 格式返回

    Args:
        start_time: 開始時間，ISO 格式字串
        end_time: 結束時間，ISO 格式字串

    Returns:
        str: 格式化的持續時間
    """
    try:
        # 解析時間字串
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # 計算差異（秒數）
        duration_seconds = (end_dt - start_dt).total_seconds()

        # 轉換為 HH:MM:SS 格式
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    except Exception as e:
        # 如果計算失敗，返回空字串
        return "--:--:--"


def generate_header(text: str = "toggl Calendar", font: str = "slant") -> str:
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
        {"key": "5", "name": "查看當前 Toggl 計時", "cmd": "current"},
        {"key": "6", "name": "列出並設置 Google 日曆", "cmd": "calendars"},
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
    
    check_duplicate = (
        Prompt.ask(
            "[bright_green]> 檢查並防止重複事件 [y/n][/bright_green]",
            choices=["y", "n"],
            default="y",
            show_choices=False,
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
    table.add_row("檢查重複事件", "ON" if check_duplicate else "OFF")

    console.print(table)
    console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")

    # 使用 rich.prompt.Confirm 而非 Prompt.ask
    continue_process = Confirm.ask(
        "[bright_green]> 確認繼續?[/bright_green]", default=True
    )
    if not continue_process:
        console.print("[bright_green]>>> 操作已取消[/bright_green]")
        return_to_menu()
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
    if not check_duplicate:
        args.append("--no-check-duplicate")

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
    check_duplicate: bool = typer.Option(
        True, "--check-duplicate/--no-check-duplicate", help="檢查並防止重複創建事件"
    ),
) -> None:
    """
    將 toggl 時間條目同步到 Google 日曆。

    如果未指定日期，默認使用今天的日期。
    """
    console.clear()

    # 使用 pyfiglet 生成 ASCII 藝術標題
    header_art = generate_header("Sync Mode", "banner")
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
    
    if check_duplicate:
        console.print(
            f"[bright_green]>>> 檢查重複功能已啟用: 將防止重複創建相同事件[/bright_green]\n"
        )
    else:
        console.print(
            f"[bright_yellow]>>> 警告: 檢查重複功能已關閉，可能會創建重複事件[/bright_yellow]\n"
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
            return_to_menu()
            return

        # 顯示找到的時間條目
        console.print(
            f"[bright_green]>>> 找到 {len(entries)} 個時間條目[/bright_green]\n"
        )

        table = Table(title=f"時間條目清單", box=ASCII, border_style="bright_green")
        table.add_column("事件", style="bright_green")
        table.add_column("開始時間", style="bright_green")
        table.add_column("結束時間", style="bright_green")
        table.add_column("時長", style="bright_green")

        for entry in entries:
            # 格式化時間顯示
            formatted_start = format_time_display(entry["start"])
            formatted_end = format_time_display(entry["end"])

            # 計算時長
            duration = calculate_duration(entry["start"], entry["end"])

            table.add_row(
                entry["description"], formatted_start, formatted_end, duration
            )

        console.print(table)
        console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")

        # 在預覽模式下，不創建事件
        if preview:
            console.print(
                "[bright_yellow]>>> 預覽模式: 不會創建實際事件[/bright_yellow]"
            )
            return_to_menu()
            return

        # 確認是否繼續
        continue_sync = Confirm.ask(
            "[bright_green]>>> 是否要繼續同步到 Google 日曆？[/bright_green]",
            default=True,
        )
        if not continue_sync:
            console.print("[bright_yellow]>>> 同步已取消[/bright_yellow]")
            return_to_menu()
            return

        # 連接 Google Calendar 並創建事件
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
                    check_duplicate=check_duplicate
                )
                
                # 使用自定義標記來判斷是新建還是跳過
                if check_duplicate and result:
                    if result.get('is_existing', False):
                        total_skipped += 1
                    else:
                        total_created += 1
                else:
                    total_created += 1

        if check_duplicate:
            console.print(
                f"\n[bright_green]>>> 成功! 處理 {len(entries)} 個事件[/bright_green]"
            )
            console.print(
                f"[bright_green]>>> - 新建事件: {total_created} 個[/bright_green]"
            )
            console.print(
                f"[bright_green]>>> - 跳過重複: {total_skipped} 個[/bright_green]"
            )
        else:
            console.print(
                f"\n[bright_green]>>> 成功! 同步了 {len(entries)} 個事件到 Google 日曆[/bright_green]"
            )
        
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
        
        return_to_menu()
        return

    except Exception as e:
        console.print(f"[bright_red]>>> 錯誤: {str(e)}[/bright_red]")
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
        
        return_to_menu()
        return


@app.command()
def current():
    """顯示當前正在記錄的 Toggl 時間條目"""
    console.clear()
    
    # 使用 pyfiglet 生成 ASCII 藝術標題
    header_art = generate_header("Current Entry", "small")
    console.print(f"[bright_green]{header_art}[/bright_green]")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    client = TogglClient()
    
    with console.status(
        "[bright_green]>>> 正在獲取當前 Toggl 計時...[/bright_green]",
        spinner="dots",
    ):
        current_entry = client.get_current_time_entry()

    if not current_entry:
        console.print("[bright_yellow]>>> 目前沒有正在記錄的 Toggl 時間條目[/bright_yellow]")
        return_to_menu()
        return

    # 計算當前條目已經運行的時間
    start_time = current_entry["start"]
    formatted_start = format_time_display(start_time)
    
    # 計算已經運行的時間
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    now_dt = datetime.now(start_dt.tzinfo)
    duration_seconds = (now_dt - start_dt).total_seconds()
    
    # 格式化持續時間
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    running_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    # 創建表格顯示當前條目詳情
    table = Table(title="當前時間條目", box=ASCII, border_style="bright_green")
    table.add_column("屬性", style="bold cyan", no_wrap=True)
    table.add_column("值", style="bright_white")

    table.add_row("描述", current_entry["description"] or "[bold red]未設置描述[/bold red]")
    table.add_row("開始時間", formatted_start)
    table.add_row("已運行時間", running_time)
    table.add_row("專案", current_entry["project"] or "無")
    
    # 如果有標籤，將它們顯示為逗號分隔的列表
    tags_str = ", ".join(current_entry["tags"]) if current_entry["tags"] else "無"
    table.add_row("標籤", tags_str)
    
    table.add_row("計費", "是" if current_entry["billable"] else "否")

    console.print(table)
    console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]\n")
    
    # 顯示可用操作
    console.print("[bright_green]>>> 可用操作：[/bright_green]")
    console.print("1. 停止計時")
    console.print("2. 返回主選單")
    
    # 獲取用戶選擇
    choice = Prompt.ask(
        "\n[bright_green]> 選擇操作[/bright_green]",
        choices=["1", "2"],
        default="2",
        show_choices=False
    )
    
    # 處理用戶選擇
    if choice == "1":
        # 停止計時
        confirm = Confirm.ask("[bright_green]>>> 確定要停止當前計時嗎？[/bright_green]")
        if confirm:
            with console.status(
                "[bright_green]>>> 正在停止計時...[/bright_green]",
                spinner="dots",
            ):
                success = client.stop_current_time_entry()
            
            if success:
                console.print("[bright_green]>>> 已成功停止計時[/bright_green]")
            else:
                console.print("[bright_red]>>> 停止計時失敗[/bright_red]")
                console.print("[bright_yellow]>>> 請檢查網絡連接或在 Toggl 網站/應用中停止[/bright_yellow]")
        
        return_to_menu()
    else:
        # 返回主選單
        display_menu()


@app.command()
def calendars():
    """列出所有可用的 Google 日曆和它們的 ID，並允許用戶選擇一個設置為預設日曆"""
    console.clear()

    # 使用 pyfiglet 生成 ASCII 藝術標題
    header_art = generate_header("Calendars", "small")
    console.print(f"[bright_green]{header_art}[/bright_green]")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    try:
        with console.status(
            "[bright_green]>>> 正在連接到 Google Calendar...[/bright_green]",
            spinner="dots",
        ):
            service = get_calendar_service()
            calendars_list = list_calendars(service)

        if not calendars_list:
            console.print("[bright_yellow]>>> 警告: 找不到任何日曆！[/bright_yellow]")
            return_to_menu()
            return

        # 顯示找到的日曆
        console.print(
            f"[bright_green]>>> 找到 {len(calendars_list)} 個日曆[/bright_green]\n"
        )

        table = Table(title="Google 日曆清單", box=ASCII, border_style="bright_green")
        table.add_column("序號", style="bright_green", justify="center")
        table.add_column("日曆名稱", style="bright_green")
        table.add_column("日曆 ID", style="bright_green")
        table.add_column("是否主要日曆", style="bright_green")
        table.add_column("目前使用", style="bright_green")

        # 獲取當前設定的日曆 ID
        import os
        from dotenv import load_dotenv

        load_dotenv()
        current_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

        # 給每個日曆給序號
        calendar_options = {}
        for i, calendar in enumerate(calendars_list, 1):
            calendar_id = calendar.get("id", "")
            is_current = calendar_id == current_calendar_id
            table.add_row(
                str(i),
                calendar.get("summary", "未命名"),
                calendar_id,
                "是" if calendar.get("primary", False) else "否",
                ">>> " if is_current else "",
            )
            calendar_options[str(i)] = calendar_id

        console.print(table)
        console.print("\n[bright_green]" + "-" * 70 + "[/bright_green]")

        # 討論用戶選擇
        choice = Prompt.ask(
            "[bright_green]> 請選擇要設置的日曆序號 (輸入 q 返回主選單)[/bright_green]",
            choices=[*list(calendar_options.keys()), "q"],
            show_choices=False,
        )

        if choice.lower() == "q":
            console.print("[bright_green]>>> 返回主選單[/bright_green]")
            display_menu()
            return

        # 獲取所選日曆的 ID
        selected_calendar_id = calendar_options[choice]
        selected_calendar_name = ""
        for calendar in calendars_list:
            if calendar.get("id") == selected_calendar_id:
                selected_calendar_name = calendar.get("summary", "未命名")
                break

        # 確認是否更新
        confirm_update = Confirm.ask(
            f"[bright_green]>>> 確認將 '{selected_calendar_name}' 設置為預設日曆？[/bright_green]",
            default=True,
        )

        if not confirm_update:
            console.print("[bright_yellow]>>> 取消設置[/bright_yellow]")
            return_to_menu()
            return

        # 更新 .env 文件
        success = update_calendar_id(selected_calendar_id)

        if success:
            console.print(
                f"[bright_green]>>> 成功將 '{selected_calendar_name}' 設置為預設日曆![/bright_green]"
            )
            console.print("[bright_green]>>> 已更新 .env 文件[/bright_green]")
        else:
            console.print("[bright_red]>>> 設置日曆失敗[/bright_red]")
        
        return_to_menu()
        return

    except Exception as e:
        console.print(f"[bright_red]>>> 錯誤: {str(e)}[/bright_red]")
        console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
        
        return_to_menu()
        return


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
        "[bright_green]>>> 將 toggl 時間條目同步到 Google 日曆的工具[/bright_green]\n"
    )

    # 添加類似於示例圖像的標語
    console.print(
        "[bright_green]>>> 控制你的時間. 掌握你的生產力. 奪回你的一天.[/bright_green]"
    )
    console.print(
        "[bright_green]>>> TOGGL CALENDAR CONNECTOR - 賦予你掌控時間的能力[/bright_green]\n"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")
    
    return_to_menu()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """主程序回調函數"""
    # 如果沒有提供子命令且是直接運行，顯示選單
    # 這樣在使用 CLI 參數時不會顯示選單
    if ctx.invoked_subcommand is None and len(sys.argv) <= 2:
        display_menu()


if __name__ == "__main__":
    app()
