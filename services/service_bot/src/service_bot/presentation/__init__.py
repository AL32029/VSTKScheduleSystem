from .callbacks.callbacks_router import router as callback_router
from .messages.main_menu_router import router as main_menu_router

__all__ = [
    'callback_router',
    'main_menu_router'
]
