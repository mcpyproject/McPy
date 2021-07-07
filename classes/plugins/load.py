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
    order = {}
    for plugin_name in plugins:
        plugin = plugins[plugin_name]
        try:
            tmp = order[plugin.PRIORITY]
        except KeyError:
            order[plugin.PRIORITY] = []
        except AttributeError:
            plugin.PRIORITY = 999
        order[plugin.PRIORITY].append(plugin) 
    return order

def load_plugins():
    event._reset_()
    plugins = _getPlugins_()
    logging.debug(plugins)
    for priority_num in plugins:
        priority = plugins[priority_num]
        if type(priority) != type(event):
            for plugin_name in priority:
                imported = plugin_name
                if inspect.isfunction(getattr(imported, "load", None)):
                    imported.load()
                    logging.info(f"loaded plugin \"{plugin_name}\"")
                else:
                    logging.info(f"couldn't load {plugin_name} because 'load' is not a function or doesen't exist")
        else:
            imported = priority
            if inspect.isfunction(getattr(imported, "load", None)):
                imported.load()
                logging.info(f"loaded plugin \"{priority.__name__}\"")
            else:
                logging.info(f"couldn't load {priority} because 'load' is not a function or doesen't exist")
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
