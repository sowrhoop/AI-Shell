import os
import tempfile

from ai_shell.config import AppConfig, config_dir, config_path


def test_config_load_save_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        os.environ["AI_SHELL_CONFIG_DIR"] = td
        try:
            # Load defaults when no file exists
            cfg = AppConfig.load()
            assert cfg.model
            # Modify and save
            cfg.model = "gpt-test"
            cfg.temperature = 0.5
            cfg.save()
            assert os.path.exists(config_path())
            # Reload and check
            cfg2 = AppConfig.load()
            assert cfg2.model == "gpt-test"
            assert cfg2.temperature == 0.5
        finally:
            del os.environ["AI_SHELL_CONFIG_DIR"]

