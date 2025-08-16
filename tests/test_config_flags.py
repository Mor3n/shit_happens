# tests/test_config_flags.py
import os
import importlib

def reload_config():
    return importlib.reload(importlib.import_module("config.config")).Config

def test_ai_confess_reply_enabled(monkeypatch):
    monkeypatch.setenv("USE_AI_CONFESS_REPLY", "true")
    Config = reload_config()
    assert Config.USE_AI_CONFESS_REPLY is True

def test_ai_confess_reply_disabled(monkeypatch):
    monkeypatch.setenv("USE_AI_CONFESS_REPLY", "0")
    Config = reload_config()
    assert Config.USE_AI_CONFESS_REPLY is False

def test_ai_confess_reply_default(monkeypatch):
    monkeypatch.delenv("USE_AI_CONFESS_REPLY", raising=False)
    Config = reload_config()
    assert Config.USE_AI_CONFESS_REPLY is True  # default = "1"
