# coding=utf-8
import functools
PLUGINS = {}
PLUGIN_HOOKS = ("PLUGIN_ENABLE", "PLUGIN_DISABLE", "PLAYER_CHAT_EVENT", "BLOCK_BREAK_EVENT", "MOB_DAMAGE_EVENT")


def add_hook(_func=None, *, hook_id=None):
    def decorator_add_hook(func):
        @functools.wraps(func)
        def wrapper_add_hook(*args, **kwargs):
            if hook_id is None or hook_id not in PLUGIN_HOOKS:
                raise TypeError("Incorrect hook type!")
            else:
                PLUGINS[hook_id][func.__name__] = func
                return func
        return wrapper_add_hook

    if _func is None:
        raise TypeError("Need a hook!")
    else:
        return decorator_add_hook
