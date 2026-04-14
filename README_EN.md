# SnowVoice Studio

An open-source Chinese TTS workstation built for humans, AI, and agents.

> Current stage: **CLI works today, WebUI is planned next.**

SnowVoice Studio is a local-first wrapper around **Qwen3-TTS**. The goal is simple: install it once, run it locally, and make it easy for both non-technical users and automation agents to use the same workflow.

<p align="center">
  <img src="assets/cover.jpg" width="100%" alt="SnowVoice Studio Cover"/>
</p>

## What it does today

- Local Chinese TTS with a clear CLI entrypoint: `snowvoice`
- Voice cloning from registered personas and cached reference audio
- Voice design from text prompts
- Dialogue generation through the current `main.py` flow

## Quick Start

```bash
git clone https://github.com/webkubor/snowvoice-studio.git
cd snowvoice-studio
chmod +x install.sh
./install.sh
source .venv/bin/activate
snowvoice --help
```

## Minimal agent bootstrap

```bash
git clone https://github.com/webkubor/snowvoice-studio.git
cd snowvoice-studio
./install.sh
source .venv/bin/activate
snowvoice --help
```

## Main commands

```bash
snowvoice voice list
snowvoice clone <persona> "Hello from SnowVoice Studio"
snowvoice design <voice_name> "This is a short modeling sentence" --tone "warm, clean, intimate"
python main.py dialogue
```

## Status

| Capability | Status | Notes |
| :--- | :--- | :--- |
| CLI | Available | Primary interface |
| Voice cloning | Available | Persona-based workflow |
| Voice design | Available | Text-to-voice design |
| Dialogue | Available | Current entry is `python main.py dialogue` |
| WebUI | Planned | Roadmap item, not shipped yet |

## Roadmap

### Phase 1: Rename and cleanup

- [x] Rename repository to `snowvoice-studio`
- [x] Rename Python package to `snowvoice-studio`
- [x] Rename the main CLI entry to `snowvoice`
- [x] Rewrite README for beginners and agents

### Phase 2: CLI hardening

- [ ] Add `snowvoice doctor`
- [ ] Add `snowvoice init`
- [ ] Add a proper `dialogue` CLI subcommand
- [ ] Improve error messages for setup and runtime failures

### Phase 3: WebUI MVP

- [ ] Upload reference audio in the browser
- [ ] Configure clone / design / dialogue jobs in a form
- [ ] Preview, download, and inspect outputs in the browser
- [ ] Reuse the same engine as the CLI

### Phase 4: Agent automation

- [ ] Support fully non-interactive installation
- [ ] Define stable task input / output contracts
- [ ] Make model, config, and output discovery agent-friendly
- [ ] Add minimal automation examples

## License

[Apache-2.0](LICENSE)
