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
            tmp = order[int(plugin.PRIORITY)]
        except KeyError:
            order[int(plugin.PRIORITY)] = []
        except AttributeError:
            plugin.PRIORITY = 999
        order[int(plugin.PRIORITY)].append(plugin)
    max = 0
    for p in order:
        plug = order[p]
        for i in plug:
            if int(i.PRIORITY) > max:
                max = int(i.PRIORITY)
    ret = []
    for i in range(max+1):
        ret.append(None)
    for p in order:
        ret[p] = order[p]
    return ret

def load_plugins():
    event._reset_()
    plugins = _getPlugins_()
    logging.debug(plugins)
    for index in plugins:
        if index != None:
            for imported in index:
                if inspect.isfunction(getattr(imported, "load", None)):
                    imported.load()
                    logging.info(f"loaded plugin \"{imported.__name__}\"")
                else:
                    logging.info(f"couldn't load {imported.__name__} because 'load' is not a function or doesen't exist")
        
logging.info("finished loading plugins")

#called when server is shutting down
def unload_plugins():
    plugins = reversed(_getPlugins_())
    logging.debug(plugins)
    for arr in plugins:
        if arr != None:
            for imported in arr:
                if inspect.isfunction(getattr(imported, "unload", None)):
                    imported.unload()
                    logging.info(f"unloaded plugin '{imported.__name__}'")
                else:
                    logging.info(f"unloaded plugin '{imported.__name__}' (plugin has no 'unload' function)")
    event._reset_()
