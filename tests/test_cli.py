import importlib
import sys

import pytest
from typer.testing import CliRunner


@pytest.fixture()
def cli_module(monkeypatch):
    """
    Load the CLI with BOARDGAME_DB_MODE=memory so tests never touch data/boardgames.db.
    Because engine/settings are created at import-time, we must reload modules after setting env.
    """
    monkeypatch.setenv("BOARDGAME_DB_MODE", "memory")

    # Ensure fresh imports that use the env var
    for name in ["app.config", "app.database", "cli"]:
        if name in sys.modules:
            del sys.modules[name]

    import cli as cli_mod
    importlib.reload(cli_mod)  # safety

    return cli_mod


def test_cli_seed_then_export(cli_module):
    runner = CliRunner()

    # Reset DB (no prompt)
    r1 = runner.invoke(cli_module.app, ["reset", "--yes"])
    assert r1.exit_code == 0
    assert "Database reset complete" in r1.output

    # Seed 2 games
    r2 = runner.invoke(cli_module.app, ["seed", "--sample", "2"])
    assert r2.exit_code == 0
    assert "Seeded" in r2.output

    # Export should print at least 2 lines (games)
    r3 = runner.invoke(cli_module.app, ["export"])
    assert r3.exit_code == 0

    lines = [ln.strip() for ln in r3.output.splitlines() if ln.strip()]
    # Each game line looks like: "1: Catan | Klaus Teuber | rating=7.2"
    game_lines = [ln for ln in lines if ":" in ln and "| rating=" in ln]
    assert len(game_lines) >= 2


def test_cli_reset_cancel(cli_module):
    runner = CliRunner()

    # Run reset WITHOUT --yes and answer "n" to confirmation
    r = runner.invoke(cli_module.app, ["reset"], input="n\n")
    assert r.exit_code == 0
    assert "Cancelled." in r.output
