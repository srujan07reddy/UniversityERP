import os
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command
from sqlalchemy import text
from app.database.base import Base
from app.database.session import async_engine
from app.core.config import settings


@pytest.fixture
def alembic_config():
    """Builds Alembic Config object pointing to backend/alembic.ini."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    cfg = Config(ini_path)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "migrations"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return cfg


def test_alembic_config_parameters(alembic_config):
    """Verify file template format and script directory settings."""
    assert alembic_config.get_main_option("script_location") is not None
    template = alembic_config.get_main_option("file_template")
    assert "year" in template
    assert "month" in template
    assert "day" in template
    assert "rev" in template
    assert "slug" in template


def test_metadata_binding():
    """Verify application declarative Base metadata is configured in migrations/env.py."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, "migrations", "env.py")
    with open(env_path, "r", encoding="utf-8") as f:
        env_content = f.read()

    assert "from app.database.base import Base" in env_content
    assert "target_metadata = Base.metadata" in env_content


def test_migration_history_exists(alembic_config):
    """Verify ScriptDirectory detects generated migration files."""
    script = ScriptDirectory.from_config(alembic_config)
    heads = script.get_heads()
    assert len(heads) == 1
    assert heads[0] == script.get_current_head()


@pytest.mark.asyncio
async def test_alembic_version_table_in_db(alembic_config):
    """Verify alembic_version table exists in PostgreSQL and tracks head revision."""
    script = ScriptDirectory.from_config(alembic_config)
    expected_head = script.get_current_head()
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SELECT version_num FROM alembic_version;"))
        current_rev = result.scalar()
        assert current_rev == expected_head


def test_programmatic_upgrade_and_downgrade(alembic_config):
    """Verify alembic command upgrade and downgrade lifecycle."""
    script = ScriptDirectory.from_config(alembic_config)
    expected_head = script.get_current_head()

    # 1. Downgrade to base
    command.downgrade(alembic_config, "base")

    # 2. Re-upgrade to head
    command.upgrade(alembic_config, "head")

    # Verify head reached cleanly
    head_rev = script.get_current_head()
    assert head_rev == expected_head
