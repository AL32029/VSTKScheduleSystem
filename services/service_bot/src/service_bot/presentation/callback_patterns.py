import re

USER_SETTINGS_COMPILE = re.compile(r"^user_settings_(profile_type|notifications)$")
OPEN_DAY_SCHEDULE_COMPILE = re.compile(r"^open_(group|cabinet)_([а-я0-9]+)$")
DAY_SCHEDULE_PANEL_COMPILE = re.compile(
    r"^schedule_(group|cabinet)_([а-я0-9]+)_(today|tomorrow|delete)(?:_(update))?$",
)
