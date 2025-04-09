#!/usr/bin/env python3
# src/cli.py

import typer
from datetime import datetime, timedelta
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from src.clients.toggl_client import TogglClient
from src.clients.google_client import get_calendar_service
from src.utils.google_calendar import create_event

app = typer.Typer(help="同步 Toggl 時間條目到 Google 日曆的 CLI 工具")
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


if __name__ == "__main__":
    app()
