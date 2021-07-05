# installing plugins
to install a plugin just put the module (file/folder) in the plugins folder
if the plugins folder doesen't exist it will be created on startup

# example plugin
example plugin which creates a new `command` event and registers two new commands

[pastebin](https://pastebin.com/eR0sM2fH)
# creating a plugin
all plugins require a `load` function which takes no arguments
the `load` function will be called upon server startup
in the `load` function you should register functions to events (see `event.register`, `event.register`)

optionally you can include a `unload` function which will be called when the server is shutting down

# plugin api
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

there are some default events that get registered automatically
`chat` - this event is fired every time a player uses chat 
    passes 2 arguments `name: str` which is the players name and `message: str` which is the players message
    if a value `True` is returned from *any* event function the message will not be sent into chat

## api
[source](/classes/plugins/api.py)

the `api` api contains pre-defined functions for ease of acess and can be imported via
```py
from classes.plugin import api
```
functions
* `api.chat_message(message: str)`

    sends `message` as a message in chat


