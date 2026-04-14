import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.engine import TTSBaseEngine
from core.processor import AudioProcessor
from core.modes.designer import DesignMode
from core.modes.cloner import CloneMode
from core.utils import get_persona_map, get_persona_cn

console = Console()


def _init_engine():
    return TTSBaseEngine("Base", "1.7B")


def _init_processor():
    return AudioProcessor(str(BASE_DIR))


def _build_instruct(tone: str, emotion: str) -> str:
    parts = [tone, emotion]
    return " ".join(p.strip() for p in parts if p.strip())


def _default_design_text() -> str:
    return "这是一段用于音色建模的短句，请保持自然呼吸。"


def tts_clone(
    persona: str = typer.Argument(..., help="已注册音色 key（如 shui_yan）"),
    text: str = typer.Argument(..., help="要合成的文本"),
    tone: Optional[str] = typer.Option(
        None, "--tone", "-t", help="语气/音色描述，覆盖基础指令"
    ),
    emotion: Optional[str] = typer.Option(
        None, "--emotion", "-e", help="情绪标签（如 Happy、Sad）"
    ),
    emotion_priority: bool = typer.Option(
        False, "--emotion-priority", help="情绪优先模式（忽略基础音色描述）"
    ),
    reference_audio: Optional[str] = typer.Option(
        None, "--ref", help="直接指定参考音频路径（绝对或相对项目根目录）"
    ),
):
    """从已注册的音色克隆合成语音。"""
    persona_map = get_persona_map()
    if persona not in persona_map:
        console.print(
            f"[red]✗[/red] 音色 key 不存在：{persona}，请先使用 [cyan]tts voice list[/cyan] 查看可用音色"
        )
        raise typer.Exit(1)

    pdata = persona_map[persona]
    pdata = pdata if isinstance(pdata, dict) else {}
    display_name = get_persona_cn(persona)

    ref_path = None

    if reference_audio:
        ref_path = (
            BASE_DIR / reference_audio
            if not os.path.isabs(reference_audio)
            else Path(reference_audio)
        )

    if not ref_path or not ref_path.exists():
        temp_path = BASE_DIR / "assets" / "temp" / f"当前参考_{display_name}.wav"
        if temp_path.exists():
            ref_path = temp_path

    if not ref_path or not ref_path.exists():
        ref_rel = pdata.get("ref", "")
        if ref_rel:
            ref_path = (
                BASE_DIR / ref_rel if not os.path.isabs(ref_rel) else Path(ref_rel)
            )

    if not ref_path or not ref_path.exists():
        console.print(
            f"[red]✗[/red] 音色 {persona} 未找到可用参考音频（标准样音 assets/temp/当前参考_{display_name}.wav 或 ref 配置均缺失）"
        )
        raise typer.Exit(1)

    base_instruct = pdata.get("instruction", "")
    if emotion_priority:
        final_instruct = (tone or emotion or "").strip()
    else:
        raw = " ".join(filter(None, [tone or "", emotion or ""]))
        final_instruct = f"{base_instruct} {raw}".strip()

    engine = _init_engine()
    processor = _init_processor()
    cloner = CloneMode(engine, processor)

    out_dir = BASE_DIR / "out"
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w\u4e00-\u9fff-]", "_", display_name)
    out_path = out_dir / f"[克隆]{safe_name}_{ts}.wav"

    console.print(f"\n[gold1]⏳ 正在合成...[/gold1]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as pbar:
        pbar.add_task("[cyan]加载模型 Base-1.7B...", total=None)
        input_instruct = f"<|im_start|>user\n{final_instruct}<|im_end|>\n"
        input_objs = engine.processor(
            text=input_instruct, return_tensors="pt", padding=True
        )
        instruct_ids = input_objs["input_ids"].to(engine.device)

        import torch

        torch.manual_seed(42)

        pbar.add_task(f"[cyan]生成语音 ({display_name})...", total=None)
        wavs, sr = cloner.run(
            persona=persona,
            text=text,
            lang="Chinese",
            instruct=final_instruct,
            emotion_priority=emotion_priority,
            allow_ref_fallback=True,
            reference_audio=str(ref_path),
        )

        pbar.add_task("[cyan]保存音频...", total=None)
        import soundfile as sf

        sf.write(str(out_path), wavs[0], sr)
        processor.apply_post_tuning(str(out_path))

    console.print(f"\n[green]✓[/green] [bold]{display_name}[/bold] 克隆合成完成")
    console.print(f"  输出 → {out_path.relative_to(BASE_DIR)}")


def tts_design(
    voice_name: str = typer.Argument(
        ..., help="新音色名称（将用于生成 voice_designs/ 和 personas.json 条目）"
    ),
    text: str = typer.Argument(..., help="音色建模用的短句（45 字以内）"),
    tone: Optional[str] = typer.Option(
        None, "--tone", help="音色描述（如「年轻女性，温柔贴耳」）"
    ),
    emotion: Optional[str] = typer.Option(
        None, "--emotion", help="情绪标签（如「温柔，安抚」）"
    ),
    commit_to_temp: bool = typer.Option(
        False, "--commit", help="确认满意后存入标准样音库（assets/temp/）"
    ),
):
    """从文字描述凭空设计新音色，不依赖任何参考音频。"""
    if not (tone or emotion):
        console.print("[red]✗[/red] 必须提供 --tone 或 --emotion（至少一个）")
        raise typer.Exit(1)

    instruct = _build_instruct(tone or "", emotion or "")
    if not text.strip():
        text = _default_design_text()
    engine = TTSBaseEngine("VoiceDesign", "1.7B")
    processor = _init_processor()
    designer = DesignMode(engine, processor)

    out_dir = BASE_DIR / "out"
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w\u4e00-\u9fff-]", "_", voice_name)
    out_path = out_dir / f"[设计]{safe_name}_{ts}.wav"

    console.print(f"\n[gold1]⏳ 正在设计音色：{voice_name}[/gold1]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as pbar:
        pbar.add_task("[cyan]加载 VoiceDesign 模型 1.7B...", total=None)
        wavs, sr = designer.run(text=text, lang="Chinese", instruct=instruct)

        pbar.add_task("[cyan]保存并净化音频...", total=None)
        import soundfile as sf

        sf.write(str(out_path), wavs[0], sr)
        processor.apply_design_cleanup(str(out_path))

    console.print(f"\n[green]✓[/green] 音色 [bold]{voice_name}[/bold] 设计完成")
    console.print(f"  输出 → {out_path.relative_to(BASE_DIR)}")

    if commit_to_temp:
        from core.utils import (
            upsert_persona_mapping,
            resolve_design_voice_key,
            write_generation_json,
        )

        voice_key = resolve_design_voice_key({"voice_name": voice_name})
        temp_seed_path = processor.extract_voice_seed(
            str(out_path), voice_name, max_sec=10, skip_start_ms=0
        )
        ref_rel = os.path.relpath(temp_seed_path, BASE_DIR).replace("\\", "/")
        design_rel = f"voice_designs/{safe_name}.json"
        persona_file = upsert_persona_mapping(
            str(BASE_DIR),
            persona_key=voice_key,
            persona_name=voice_name,
            ref_rel=ref_rel,
            design_rel=design_rel,
            instruction=instruct,
        )
        gen_json_path = write_generation_json(
            str(BASE_DIR), voice_key, source="voice_design"
        )
        console.print(f"  [green]✓ 标准样音已沉淀 → {ref_rel}[/green]")
        console.print(f"  [green]✓ 角色映射已更新 → {persona_file}[/green]")
