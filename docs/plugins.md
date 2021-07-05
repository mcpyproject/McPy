# plugins
The plugins sytem consist of two main parts
1. event (classes.plugins.event)
2. api    (classes.plugins.api)

## event
[source](/classes/plugins/event.py)

The `events` api handles events and can be imported via
```py
from classes.plugin import event
```
There are 3 functions in this api
* `event.registerEvent(name: str)`

    creates a new event which can have functions assigned to it via event.register()
* `event.register(event: str,func: typing.Callable)`

    registers function (func) to event (event) which will be called when ever the event is called via event.fire()
* `event.fire(event: str,*args,**kwargs) -> list`

    takes a `event` and arguments and runs all functions attached with the arguments and returns a list containg all outputs from all called functions

## api
[source](/classes/plugins/api.py)

the `api` api contains pre-defined functions for ease of acess and can be imported via
```py
from classes.plugin import api
```
functions
* `api.chat_message(message: str)`

    sends `message` as a message in chat

