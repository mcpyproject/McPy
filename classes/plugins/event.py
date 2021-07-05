import os
import builtins
import logging
import pickle
import typing
_pickleLevel_ = 5 #pickle level to use when comprssing and storing events
def _save_(events):
    folder = os.path.dirname(os.path.realpath(__file__))
    with open(f'{folder}/events.pickle',"wb") as file:
        pickle.dump(events,file,protocol=_pickleLevel_)

def _load_():
    folder = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(f'{folder}/events.pickle',"rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
def _reset_():
    folder = os.path.dirname(os.path.realpath(__file__))
    with open(f'{folder}/events.pickle',"wb") as file:
        pickle.dump({},file,protocol=_pickleLevel_)

_events_ = {}

def registerEvent(name: str):
    _events_ = _load_()
    try:
        tmp = _events_[name]
        logging.info(f"event '{name}' was allready registered")
    except KeyError:
        logging.info(f"registering event '{name}'")
        _events_[name] = []
    _save_(_events_)

def register(event: str,func: typing.Callable):
    _events_ = _load_()
    try:
        _events_[event].append(func)
    except KeyError:
        registerEvent(event)
        _events_ = _load_()
        _events_[event].append(func)
    _save_(_events_)

def fire(event: str,*args,**kwargs) -> list:
    import traceback
    _events_ = _load_()
    ret = []
    for func in _events_[event]:
        try:
            ret.append(func(*args,**kwargs))
        except builtins.TypeError:
            print(traceback.format_exc())
            logging.error(f"a plugin connected to event '{event}' forgot to use *args and **kwargs")
    return ret