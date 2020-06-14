from .botcommands import BotCommands
from .db import initialize as db_initialize

def initialize_db(config):
    db_initialize(config)

def initialize_bot(client, name='BookClubBot', prefix='!bookclub', devmode=False):
    cmds = BotCommands(client, botname=name, prefix=prefix, devmode=devmode)

    from .cmd_checkin import bp as checkin_bp
    cmds.register_blueprint(checkin_bp)

    return cmds
