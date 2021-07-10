import collections

from . import api
from . import event

import os
import logging
import inspect

def _getPlugins_() -> list:
    import pkgutil
    import importlib
    os.makedirs("plugins/", exist_ok=True)
    import plugins as exts

    def unqualify(name: str) -> str:
        """Return an unqualified name given a qualified module/package `name`."""
        return name.rsplit(".")[-1]
    
    #get all ing plugins
    plugins = []
    for module in pkgutil.walk_packages(exts.__path__, f"{exts.__name__}."):
        plugin_name = unqualify(module.name)
        if plugin_name.startswith("_"):
            continue
        plugins.append(importlib.import_module(module.name))
    
    #get a dictionary of the priorities
    order = collections.defaultdict(list)
    for plugin in plugins:
        plugin
        try:
            tmp = order[int(plugin.PRIORITY)]
        except AttributeError:
            plugin.PRIORITY = 999
        order[int(plugin.PRIORITY)].append(plugin)

    #get the highest priority to see how big we have to make the list
    highest_priority = 0
    for p in order:
        plug = order[p]
        for i in plug:
            if int(i.PRIORITY) > highest_priority:
                highest_priority = int(i.PRIORITY)
    list_of_list = []
    for i in range(highest_priority+1):
        list_of_list.append(None)
    for p in order:
        list_of_list[p] = order[p]
    
    #flatten the list of list into a single list
    ret = []
    for prior in list_of_list:
        if prior == None:
            continue
        for plugin in prior:
            ret.append(plugin)
    return ret

def load_plugins():
    event._reset_()
    plugins = _getPlugins_()
    logging.debug(plugins)
    for imported in plugins:
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
    for imported in plugins:
        if inspect.isfunction(getattr(imported, "unload", None)):
            imported.unload()
            logging.info(f"unloaded plugin '{imported.__name__}'")
        else:
            logging.info(f"unloaded plugin '{imported.__name__}' (plugin has no 'unload' function)")
    event._reset_()
