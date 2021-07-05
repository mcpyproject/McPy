from multiprocessing import Array
from . import api
from . import event

import os
import logging
import inspect

def _getPlugins_() -> Array:
    import pkgutil
    import importlib
    if not (os.path.exists('plugins/')):
        os.mkdir('plugins/')
    import plugins as exts

    def unqualify(name: str) -> str:
        """Return an unqualified name given a qualified module/package `name`."""
        return name.rsplit(".", maxsplit=1)[-1]
    plugins = {}
    for module in pkgutil.walk_packages(exts.__path__, f"{exts.__name__}."):
        plugin_name = unqualify(module.name)
        if plugin_name.startswith("_"):
            next
        plugins[plugin_name] = importlib.import_module(module.name)
    return plugins

def load_plugins():
    event._reset_()
    plugins = _getPlugins_()
    for plugin_name in plugins:
        imported = plugins[plugin_name]
        if inspect.isfunction(getattr(imported, "load", None)):
            imported.load()
            logging.info(f"loaded plugin \"{plugin_name}\"")
        else:
            logging.info(f"couldn't load {plugin_name} because 'load' is not a function or doesen't exist")
    logging.info("finished loading plugins")

#called when server is shutting down
def unload_plugins():
    plugins = _getPlugins_()
    for plugin_name in plugins:
        imported = plugins[plugin_name]
        if inspect.isfunction(getattr(imported, "unload", None)):
            imported.unload()
            logging.info(f"unloaded plugin '{plugin_name}'")
        else:
            logging.info(f"unloaded plugin '{plugin_name}' (plugin has no 'unload' function)")
    event._reset_()
