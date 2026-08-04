"""Settings repository for Ojo de Dios."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Setting


class SettingsRepository:
    """Persistence operations for runtime settings."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def set_value(self, key: str, value: str, description: str | None = None) -> Setting:
        """Create or update a setting value."""
        if not key:
            raise ValueError("Setting key cannot be empty.")
        setting = self.session.scalar(select(Setting).where(Setting.key == key))
        if setting is None:
            setting = Setting(key=key, value=value, description=description)
            self.session.add(setting)
        else:
            setting.value = value
            setting.description = description
        self.session.commit()
        self.session.refresh(setting)
        return setting

    def get_value(self, key: str, default: str | None = None) -> str | None:
        """Return a setting value, or default when missing."""
        setting = self.session.scalar(select(Setting).where(Setting.key == key))
        if setting is None:
            return default
        return setting.value

    def list_settings(self) -> list[Setting]:
        """Return all settings ordered by key."""
        return list(self.session.scalars(select(Setting).order_by(Setting.key)).all())
