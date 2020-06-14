from collections import OrderedDict
from enum import Enum
import functools
import logging

class BotCommands(object):
    prefix = ''
    botname = ''
    devmode = False
    client = None
    commands = OrderedDict()
    
    class Action(Enum):
        HANDLED = 0
        IGNORE = 1
        USAGE = 2
        HELP = 3

    class Blueprint(object):
        commands = OrderedDict()
        _parent = None
        
        @property
        def client(self):
            if self._parent == None:
                return None
            return self._parent.client
        
        def register(self, name, *, spec=None, desc=None, devonly=False):
            def decorator_register(func):
                self.commands[name] = { 'name': name, 'func': func, 'devonly': devonly }
                if spec != None:
                    self.commands[name]['spec'] = spec
                if desc != None:
                    self.commands[name]['desc'] = desc
                @functools.wraps(func)
                def wrapper_register(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper_register
            return decorator_register
    
    def __init__(self, client, botname='Bot', prefix='', devmode=False):
        self.client = client
        self.prefix = prefix
        self.botname = botname
        self.devmode = devmode
    
    def register(self, name, *, spec=None, desc=None, devonly=False):
        def decorator_outer(func):
            bp = self.Blueprint()
            dec = bp.register(name, spec=spec, desc=desc, devonly=devonly)
            result = dec(func)
            self.register_blueprint(bp)
            return result
        return decorator_outer
    
    def register_blueprint(self, blueprint):
        for name in blueprint.commands:
            self.commands[name] = blueprint.commands[name]
        blueprint._parent = self
    
    async def reply(self, message, content):
        await message.channel.send(f'{message.author.mention} {content}')
        
    async def print_usage(self, message, name):
        content = 'Command is: `' + self.prefix + name
        if 'spec' in self.commands[name]:
            content += ' ' + self.commands[name]['spec']
        content += '`'
        await self.reply(message, content)
    
    async def print_help(self, message):
        content = self.botname + ' commands:\n'
        for name in self.commands:
            if not self.commands[name]['devonly'] or self.devmode:
                content += '`' + self.prefix + name
                if 'spec' in self.commands[name]:
                    content += ' ' + self.commands[name]['spec']
                content += '`\n'
                if 'desc' in self.commands[name]:
                    content += '          ' + self.commands[name]['desc'] + '\n'
        await self.reply(message, content)
    
    async def on_message(self, message):
        # ignore messages from ourselves
        if message.author.id == self.client.user.id:
            return
        
        # check for prefix
        if not message.content.startswith(self.prefix):
            return
        parts = message.content[len(self.prefix):].split(None, 1)
        name = ''
        unparsed_args = ''
        if len(parts) > 0:
            name = parts[0].lower()
        if len(parts) > 1:
            unparsed_args = parts[1]

        if name in self.commands:
            if not self.commands[name]['devonly'] or self.devmode:
                res = await self.commands[name]['func'](message, name, unparsed_args)
                if type(res) == str:
                    await self.reply(message, res)
                elif res == self.Action.HANDLED:
                    pass
                elif res == self.Action.IGNORE:
                    pass
                elif res == self.Action.USAGE:
                    await self.print_usage(message, name)
                elif res == self.Action.HELP:
                    await self.print_help(message)
            else:
                await self.print_help(message)
        else:
            await self.print_help(message)
