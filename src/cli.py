import sys
import typer
from rich.console import Console
from theme.cyberpunk import cyberpunk_theme
from handlers.menu import display_menu

app = typer.Typer(
    help="同步 Toggl 時間條目到 Google 日曆的 CLI 工具", add_completion=False
)
console = Console(theme=cyberpunk_theme, highlight=False)

# 指令導入
from commands.sync import sync
from commands.current import current
from commands.calendars import calendars
from commands.version import version

app.command()(sync)
app.command()(current)
app.command()(calendars)
app.command()(version)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """主程序回調函數"""
    if ctx.invoked_subcommand is None and len(sys.argv) <= 2:
        display_menu(app, console)


if __name__ == "__main__":
    app()
