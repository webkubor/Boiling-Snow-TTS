import os
import traceback
import uuid
import time
from typing import Any, Dict, List, Optional

import soundfile as sf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.engine import TTSBaseEngine
from core.modes.cloner import CloneMode
from core.modes.designer import DesignMode
from core.modes.dialogue import DialogueMode
from core.processor import AudioProcessor
from core.utils import (
    generate_output_path,
    get_persona_cn,
    get_persona_map,
    log_generation_metadata,
    upsert_persona_mapping,
    resolve_design_voice_key,
    resolve_design_voice_label,
    sanitize_path_component,
    validate_runtime_config,
    write_generation_json,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_UPLOAD_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}


class DialogueLine(BaseModel):
    role: str
    text: str
    tone: str = ""
    emotion: str = ""
    emotion_priority: bool = False


class GenerateRequest(BaseModel):
    mode: str = Field(default="clone", description="clone | design | dialogue")
    model_size: str = "1.7B"
    model_type: Optional[str] = None
    language: str = "Chinese"
    title: str = "WebUI_未命名"
    episode: str = "WEB"

    persona: Optional[str] = None
    voice_name: str = ""
    commit_to_temp: bool = False
    reference_audio: str = ""
    text: str = ""
    tone: str = ""
    emotion: str = ""
    emotion_priority: bool = False

    lines: List[DialogueLine] = Field(default_factory=list)


class RuntimeService:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _cache_key(self, model_type: str, model_size: str) -> str:
        """生成模型实例缓存键，避免同规格模型被重复加载。"""
        return f"{model_type}:{model_size}"

    def get_runtime(self, model_type: str, model_size: str) -> Dict[str, Any]:
        """按模型类型和规格获取运行时对象。

        若缓存命中则直接复用；否则初始化引擎与模式执行器并写入缓存。
        """
        key = self._cache_key(model_type, model_size)
        if key in self._cache:
            return self._cache[key]

        engine = TTSBaseEngine(model_type, model_size)
        processor = AudioProcessor(BASE_DIR)
        cloner = CloneMode(engine, processor)
        runtime = {
            "engine": engine,
            "processor": processor,
            "cloner": cloner,
            "designer": DesignMode(engine, processor),
            "dialogue": DialogueMode(engine, processor, cloner),
        }
        self._cache[key] = runtime
        return runtime


runtime_service = RuntimeService()

app = FastAPI(title="Boiling-Snow-TTS Web API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_mode(req: GenerateRequest) -> str:
    """规范化前端传入模式，默认回退为 clone。"""
    return (req.mode or "clone").lower()


def _resolve_model_type(mode: str, model_type: Optional[str]) -> str:
    """根据模式决定模型类型，允许前端显式覆盖。"""
    return model_type or ("VoiceDesign" if mode == "design" else "Base")


def _build_cfg(req: GenerateRequest, mode: str, model_type: str) -> Dict[str, Any]:
    """将 Web 请求对象转换为核心生成链路可识别的配置字典。"""
    if mode == "dialogue":
        return {
            "type": "dialogue",
            "model_type": model_type,
            "model_size": req.model_size,
            "title": req.title,
            "episode": req.episode,
            "language": req.language,
            "emotion_priority": req.emotion_priority,
            "lines": [
                {
                    "role": line.role,
                    "text": line.text,
                    "tone": line.tone,
                    "emotion": line.emotion,
                    "emotion_priority": line.emotion_priority,
                }
                for line in req.lines
            ],
        }

    cfg = {
        "type": "design" if mode == "design" else "single",
        "model_type": model_type,
        "model_size": req.model_size,
        "title": req.title,
        "episode": req.episode,
        "language": req.language,
        "voice_name": req.voice_name,
        "commit_to_temp": req.commit_to_temp,
        "reference_audio": req.reference_audio,
        "text": req.text,
        "tone": req.tone,
        "emotion": req.emotion,
        "emotion_priority": req.emotion_priority,
    }
    if mode != "design":
        cfg["persona"] = req.persona
    return cfg


def _run_design(runtime: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    """执行音色设计模式，并将结果写入 out/，同时提取参考种子。"""
    instruct = f"{cfg.get('tone', '')}, {cfg.get('emotion', '')}".strip(", ")
    wavs, sr = runtime["designer"].run(cfg.get("text", ""), cfg.get("language", "Chinese"), instruct)
    final_path = generate_output_path(cfg, BASE_DIR)
    sf.write(final_path, wavs[0], sr)

    voice_label = resolve_design_voice_label(cfg)
    runtime["processor"].apply_design_cleanup(final_path)
    if bool(cfg.get("commit_to_temp", False)):
        voice_key = resolve_design_voice_key(cfg)
        temp_seed_path = runtime["processor"].extract_voice_seed(final_path, voice_label, max_sec=10, skip_start_ms=0)
        cfg["_temp_seed_path"] = os.path.relpath(temp_seed_path, BASE_DIR)

        persona_file = upsert_persona_mapping(
            BASE_DIR,
            persona_key=voice_key,
            persona_name=voice_label,
            ref_rel=cfg["_temp_seed_path"],
            design_rel=f"voice_designs/{voice_label}.json",
            instruction=f"{cfg.get('tone', '')} {cfg.get('emotion', '')}".strip(),
        )
        cfg["_persona_mapping_file"] = os.path.relpath(persona_file, BASE_DIR)
        cfg["_persona_key"] = voice_key

        cfg["_generation_json"] = os.path.relpath(
            write_generation_json(BASE_DIR, voice_key, source="web_voice_design"),
            BASE_DIR
        )
    else:
        cfg["_pending_commit"] = True
    return final_path


def _run_dialogue(runtime: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    """执行多角色对话模式，返回最终合成音频路径。"""
    return runtime["dialogue"].run(cfg)


def _run_clone(runtime: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    """执行单人克隆模式，并做后处理后返回输出路径。"""
    instruct = f"{cfg.get('tone', '')}, {cfg.get('emotion', '')}".strip(", ")
    wavs, sr = runtime["cloner"].run(
        cfg.get("persona"),
        cfg.get("text", ""),
        cfg.get("language", "Chinese"),
        instruct,
        emotion_priority=bool(cfg.get("emotion_priority", False)),
        reference_audio=cfg.get("reference_audio"),
    )
    final_path = generate_output_path(cfg, BASE_DIR)
    sf.write(final_path, wavs[0], sr)
    runtime["processor"].apply_post_tuning(final_path)
    return final_path


def _format_generate_response(final_path: str) -> Dict[str, Any]:
    """统一封装生成结果，返回相对路径与播放/下载地址。"""
    file_name = os.path.basename(final_path)
    cache_bust = int(time.time() * 1000)
    return {
        "ok": True,
        "path": os.path.relpath(final_path, BASE_DIR),
        "file_name": file_name,
        "audio_url": f"/api/files/{file_name}?t={cache_bust}",
        "download_url": f"/api/files/{file_name}?download=1",
    }


@app.get("/api/health")
def health():
    """健康检查接口，用于前端探活。"""
    return {"ok": True}


@app.get("/api/personas")
def list_personas():
    """读取并返回角色列表，供前端下拉框渲染。"""
    personas = get_persona_map()
    items = []
    for key, data in personas.items():
        if isinstance(data, dict):
            items.append(
                {
                    "key": key,
                    "name": data.get("name", key),
                    "instruction": data.get("instruction", ""),
                    "ref": data.get("ref", ""),
                }
            )
        else:
            items.append({"key": key, "name": str(data), "instruction": "", "ref": ""})
    return {"items": items}


@app.post("/api/reference/upload")
async def upload_reference_audio(
    persona: str = Form(...),
    file: UploadFile = File(...),
):
    """上传参考音频并自动提取黄金样音到 assets/temp。

    - 入参: persona + 音频文件
    - 出参: 原始文件路径与提取后的种子路径
    """
    if not persona.strip():
        raise HTTPException(status_code=400, detail="persona 不能为空")

    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(status_code=400, detail="仅支持 wav/mp3/m4a/flac/ogg/aac")

    ref_dir = os.path.join(BASE_DIR, "assets", "reference")
    os.makedirs(ref_dir, exist_ok=True)

    persona_cn = sanitize_path_component(get_persona_cn(persona), fallback="未命名角色")
    raw_name = f"{persona_cn}_上传_{uuid.uuid4().hex[:8]}{ext}"
    raw_path = os.path.join(ref_dir, raw_name)

    content = await file.read()
    with open(raw_path, "wb") as f:
        f.write(content)

    processor = AudioProcessor(BASE_DIR)
    seed_path = processor.extract_voice_seed(raw_path, persona_cn)

    return {
        "ok": True,
        "raw_path": os.path.relpath(raw_path, BASE_DIR),
        "seed_path": os.path.relpath(seed_path, BASE_DIR),
        "persona": persona,
        "persona_name": persona_cn,
    }


@app.post("/api/generate")
def generate(req: GenerateRequest):
    """统一生成入口：克隆/设计/对话三种模式共用该接口。"""
    try:
        mode = _resolve_mode(req)
        model_type = _resolve_model_type(mode, req.model_type)
        runtime = runtime_service.get_runtime(model_type=model_type, model_size=req.model_size)

        cfg = _build_cfg(req, mode, model_type)
        validate_runtime_config(cfg, config_ref=f"webui:{mode}")

        if mode == "design":
            final_path = _run_design(runtime, cfg)
        elif mode == "dialogue":
            final_path = _run_dialogue(runtime, cfg)
        else:
            final_path = _run_clone(runtime, cfg)

        log_generation_metadata(cfg, final_path, BASE_DIR)
        resp = _format_generate_response(final_path)
        if cfg.get("_temp_seed_path"):
            resp["temp_seed_path"] = cfg["_temp_seed_path"]
        if cfg.get("_persona_mapping_file"):
            resp["persona_mapping_file"] = cfg["_persona_mapping_file"]
            resp["persona_key"] = cfg.get("_persona_key")
        if cfg.get("_generation_json"):
            resp["generation_json"] = cfg["_generation_json"]
        if cfg.get("_pending_commit"):
            resp["pending_commit"] = True
        return resp
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/files/{file_name}")
def serve_file(file_name: str, download: int = 0, t: Optional[int] = None):
    """提供音频文件访问与下载能力。"""
    safe_name = os.path.basename(file_name)
    file_path = os.path.join(BASE_DIR, "out", safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    headers = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    if download:
        return FileResponse(file_path, filename=safe_name, media_type="audio/wav", headers=headers)
    return FileResponse(file_path, media_type="audio/wav", headers=headers)
