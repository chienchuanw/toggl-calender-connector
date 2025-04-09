#!/usr/bin/env python3
# src/cli.py

import typer
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.box import ROUNDED
from src.clients.toggl_client import TogglClient
from src.clients.google_client import get_calendar_service
from src.utils.google_calendar import create_event

app = typer.Typer(help="同步 Toggl 時間條目到 Google 日曆的 CLI 工具", add_completion=False)
console = Console()


@app.command()
def sync(
    start_date: Optional[str] = typer.Option(
        None, "--start-date", "-s", help="開始日期，格式為 YYYY-MM-DD"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end-date", "-e", help="結束日期，格式為 YYYY-MM-DD"
    ),
    days: int = typer.Option(0, "--days", "-d", help="過去 N 天（與 start_date/end_date 互斥）"),
    preview: bool = typer.Option(False, "--preview", "-p", help="預覽模式，不實際創建事件"),
) -> None:
    """
    將 Toggl 時間條目同步到 Google 日曆。
    
    如果未指定日期，默認使用今天的日期。
    """
    # 處理日期參數
    today = datetime.today().date()
    
    if days > 0:
        if start_date or end_date:
            console.print("[bold red]錯誤：不能同時指定 days 和 start_date/end_date[/]")
            raise typer.Exit(code=1)
        
        calculated_start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    else:
        calculated_start_date = start_date if start_date else today.strftime("%Y-%m-%d")
        end_date_str = end_date if end_date else calculated_start_date
    
    # 顯示同步信息
    console.print(f"[bold green]從 {calculated_start_date} 到 {end_date_str} 同步 Toggl 時間條目到 Google 日曆[/]")
    
    try:
        client = TogglClient()
        entries = client.get_time_entries(calculated_start_date, end_date_str)
        
        if not entries:
            console.print("[yellow]找不到時間條目！[/]")
            return
            
        # 顯示找到的時間條目
        table = Table(title=f"找到 {len(entries)} 個時間條目")
        table.add_column("描述", style="cyan")
        table.add_column("開始時間", style="green")
        table.add_column("結束時間", style="green")
        
        for entry in entries:
            table.add_row(
                entry["description"], 
                entry["start"], 
                entry["end"]
            )
            
        console.print(table)
        
        # 在預覽模式下，不創建事件
        if preview:
            console.print("[bold yellow]預覽模式：不會創建實際事件[/]")
            return
            
        # 確認是否繼續
        if not typer.confirm("是否要繼續同步到 Google 日曆？"):
            console.print("[yellow]同步已取消[/]")
            return
            
        # 連接 Google Calendar 並創建事件
        with console.status("[bold green]連接到 Google Calendar...") as status:
            service = get_calendar_service()
            
            for i, entry in enumerate(entries, 1):
                status.update(f"[bold green]正在創建事件 {i}/{len(entries)}...")
                
                create_event(
                    service,
                    entry["description"],
                    entry["start"],
                    entry["end"]
                )
                
        console.print(f"[bold green]成功同步 {len(entries)} 個事件到 Google 日曆！[/]")
        
    except Exception as e:
        console.print(f"[bold red]錯誤：{str(e)}[/]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """顯示版本信息"""
    console.print("[bold]Toggl Calendar Connector[/] [cyan]v0.1.0[/]")
    console.print("將 Toggl 時間條目同步到 Google 日曆的工具")


def display_menu() -> None:
    """顯示交互式選單"""
    console.clear()
    text = Text()
    text.append("\n Toggl Calendar Connector ", style="bold white on blue")
    text.append(" v0.1.0\n", style="bold cyan")
    
    console.print(Panel.fit(
        text,
        title="歡迎",
        border_style="blue",
        box=ROUNDED
    ))
    
    menu_items = [
        {"key": "1", "name": "同步今天的時間條目", "cmd": "sync"},
        {"key": "2", "name": "同步過去 7 天的時間條目", "cmd": "sync --days 7"},
        {"key": "3", "name": "預覽模式（不實際創建事件）", "cmd": "sync --preview"},
        {"key": "4", "name": "自定義同步選項", "cmd": "custom"},
        {"key": "v", "name": "查看版本信息", "cmd": "version"},
        {"key": "q", "name": "退出程序", "cmd": "exit"}
    ]
    
    table = Table(show_header=False, box=ROUNDED, border_style="blue")
    table.add_column("選項", style="cyan", justify="center")
    table.add_column("描述", style="white")
    
    for item in menu_items:
        table.add_row(f"[bold]{item['key']}[/bold]", item["name"])
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("請選擇一個選項", choices=[item["key"] for item in menu_items])
    
    # 處理用戶選擇
    for item in menu_items:
        if item["key"] == choice:
            if item["cmd"] == "exit":
                console.print("[bold]感謝使用！再見！[/bold]")
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
    console.print(Panel.fit(
        "自定義同步選項",
        title="設定", 
        border_style="green",
        box=ROUNDED
    ))
    
    # 詢問參數
    start_date = Prompt.ask(
        "開始日期 (YYYY-MM-DD)", 
        default=datetime.today().strftime("%Y-%m-%d")
    )
    
    end_date = Prompt.ask(
        "結束日期 (YYYY-MM-DD)", 
        default=start_date
    )
    
    preview = Prompt.ask(
        "預覽模式 (只顯示不創建事件)", 
        choices=["y", "n"], 
        default="n"
    ) == "y"
    
    # 構建參數
    args = ["toggl-calendar", "sync", "--start-date", start_date, "--end-date", end_date]
    if preview:
        args.append("--preview")
    
    # 執行命令
    console.clear()
    sys.argv = args
    app()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """主程序回調函數"""
    # 如果沒有提供子命令且是直接運行，顯示選單
    # 這樣在使用 CLI 參數時不會顯示選單
    if ctx.invoked_subcommand is None and len(sys.argv) <= 2:
        display_menu()


if __name__ == "__main__":
    app()
