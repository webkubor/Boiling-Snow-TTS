from scripts.run_clone import (
    resolve_clone_model_path,
    resolve_target_audio,
    resolve_voice_profile,
)


def test_resolve_clone_model_path_priority():
    paths = {
        "clone_model_directory": "./models/Base-0.6B",
        "models_directory": "./models/CustomVoice-0.6B",
    }
    assert resolve_clone_model_path(paths, "./override/base") == "./override/base"
    assert resolve_clone_model_path(paths) == "./models/Base-0.6B"


def test_resolve_clone_model_path_legacy_fallback():
    paths = {"models_directory": "./legacy/model-dir"}
    assert resolve_clone_model_path(paths) == "./legacy/model-dir"


def test_resolve_clone_model_path_default():
    assert resolve_clone_model_path({}) == "./models/Base-0.6B"


def test_resolve_voice_profile():
    profiles = {"a": {"target": "a.wav"}}
    assert resolve_voice_profile(profiles, "a") == {"target": "a.wav"}
    assert resolve_voice_profile(profiles, "missing") is None
    assert resolve_voice_profile(profiles, None) is None


def test_resolve_target_audio_priority():
    profile = {"target": "profile.wav"}
    assert resolve_target_audio("cli.wav", profile) == "cli.wav"
    assert resolve_target_audio(None, profile) == "profile.wav"
    assert resolve_target_audio(None, None) is None
