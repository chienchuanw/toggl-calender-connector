import os
from dotenv import load_dotenv
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.box import ASCII

from src.clients.google_client import get_calendar_service
from src.utils.google_calendar import list_calendars, update_calendar_id
from utils.formatter import generate_header
from handlers.menu import return_to_menu
from theme.cyberpunk import console


def calendars():
    """列出並設置預設 Google Calendar"""
    console.clear()
    console.print(
        f"[bright_green]{generate_header('Calendars', 'small')}[/bright_green]"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    try:
        service = get_calendar_service()
        calendars_list = list_calendars(service)
        if not calendars_list:
            console.print("[bright_yellow]>>> 警告: 找不到任何日曆！[/bright_yellow]")
            return return_to_menu()

        load_dotenv()
        current_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

        table = Table(title="Google 日曆清單", box=ASCII, border_style="bright_green")
        table.add_column("序號", justify="center")
        table.add_column("名稱")
        table.add_column("ID")
        table.add_column("主要")
        table.add_column("當前")

        options = {}
        for i, cal in enumerate(calendars_list, 1):
            cid = cal.get("id", "")
            table.add_row(
                str(i),
                cal.get("summary", ""),
                cid,
                "是" if cal.get("primary") else "否",
                ">>>" if cid == current_id else "",
            )
            options[str(i)] = cid

        console.print(table)

        choice = Prompt.ask(
            "[bright_green]> 選擇日曆序號 (q 返回)[/bright_green]",
            choices=[*options.keys(), "q"],
            show_choices=False,
        )
        if choice == "q":
            return return_to_menu()

        selected_id = options[choice]
        selected_name = next(
            cal["summary"] for cal in calendars_list if cal["id"] == selected_id
        )

        if Confirm.ask(
            f"[bright_green]>>> 設定 '{selected_name}' 為預設日曆？[/bright_green]"
        ):
            if update_calendar_id(selected_id):
                console.print(
                    f"[bright_green]>>> 已設為預設日曆：{selected_name}[/bright_green]"
                )
            else:
                console.print("[bright_red]>>> 設定失敗[/bright_red]")

        return return_to_menu()

    except Exception as e:
        console.print(f"[bright_red]>>> 錯誤: {e}[/bright_red]")
        return return_to_menu()
