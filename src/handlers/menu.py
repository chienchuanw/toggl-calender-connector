from rich.prompt import Prompt
from utils.formatter import generate_header
from theme.cyberpunk import console


def display_menu(app, console):
    console.clear()
    console.print(
        f"[bright_green]{generate_header('sync toggl', 'isometric4')}[/bright_green]"
    )
    console.print(">>> TOGGL CALENDAR CONNECTOR v0.1.0", style="title")
    console.print(">>> 控制你的時間，管理你的生產力\n", style="subtitle")
    console.print("[bright_green]" + "-" * 70 + "[/bright_green]")

    items = [
        ("1", "同步今天的時間條目", ["sync"]),
        ("2", "同步過去 7 天的時間條目", ["sync", "--days", "7"]),
        ("3", "預覽模式（不實際創建事件）", ["sync", "--preview"]),
        (
            "4",
            "自定義同步選項",
            ["sync", "--start-date", "YYYY-MM-DD", "--end-date", "YYYY-MM-DD"],
        ),
        ("5", "查看當前 Toggl 計時", ["current"]),
        ("6", "列出並設置 Google 日曆", ["calendars"]),
        ("v", "查看版本信息", ["version"]),
        ("q", "退出程序", None),
    ]

    for key, desc, _ in items:
        console.print(
            f"[bright_green]> {key}[/bright_green] [bright_green]{desc}[/bright_green]"
        )

    choice = Prompt.ask(
        "\n[bright_green]> 請輸入選擇[/bright_green]",
        choices=[i[0] for i in items],
        show_choices=False,
    )

    for key, _, cmd in items:
        if choice == key:
            if cmd is None:
                console.print("[bright_green]>>> 再見！[/bright_green]")
                raise SystemExit
            import sys

            sys.argv = ["toggl-calendar"] + cmd
            app()
            break


def return_to_menu(message: str = "按 Enter 返回主選單") -> None:
    Prompt.ask(f"\n[bright_green]> {message}[/bright_green]", default="")
    from cli import app, console

    display_menu(app, console)
