import typer
from cli.commands.voice import app as voice_app
from cli.commands.tts import tts_clone, tts_design
from cli.commands.job import app as job_app
from cli.commands.preset import app as preset_app

app = typer.Typer(
    name="tts",
    help="[bold gold1]TTS CLI[/bold gold1] — 本地音色管理与语音合成工具",
    add_completion=False,
)
app.add_typer(voice_app, name="voice")
app.add_typer(job_app, name="job")
app.add_typer(preset_app, name="preset")
app.command("clone")(tts_clone)
app.command("design")(tts_design)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    tts — TTS CLI

    子命令组：
      voice      音色素材管理（list / add / preview / show / rm / import）
      clone      从已有音色克隆合成
      design     从文字描述设计新音色
      preset     预设管理（list / show / run / batch）
      job        任务历史（list / show / clean）
      ui         启动全屏 TUI 界面
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
