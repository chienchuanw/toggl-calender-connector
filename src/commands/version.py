from utils.formatter import generate_header
from handlers.menu import return_to_menu
from theme.cyberpunk import console


def version():
    """顯示版本資訊與標語"""
    console.clear()
    console.print(
        f"[bright_green]{generate_header('Version Info', 'small')}[/bright_green]"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]\n")

    console.print("[bright_green]>>> TOGGL CALENDAR CONNECTOR v0.1.0[/bright_green]")
    console.print(
        "[bright_green]>>> 將 Toggl 時間條目同步到 Google 日曆的工具[/bright_green]\n"
    )
    console.print(
        "[bright_green]>>> 控制你的時間. 掌握你的生產力. 奪回你的一天.[/bright_green]"
    )
    console.print(
        "[bright_green]>>> TOGGL CALENDAR CONNECTOR - 賦予你掌控時間的能力[/bright_green]\n"
    )
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")

    return return_to_menu()
