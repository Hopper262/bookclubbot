import discord
import sys
import logging
from daemonize import Daemonize
import smtplib
from email.message import EmailMessage
import traceback
import argparse

import bot

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', help='permissions username')
parser.add_argument('-g', '--group', help='permissions group')
parser.add_argument('-l', '--logfile', help='log file')
parser.add_argument('-p', '--pidfile', help='pid file')
parser.add_argument('-d', '--devmode', help='allow development-only commands', type=int, choices=range(0, 2), default=0)
parser.add_argument('-t', '--emailto', help='email destination for error logging')
parser.add_argument('-f', '--emailfrom', help='email source for error logging')
parser.add_argument('-s', '--emailsubject', help='email subject for error logging', default='Error from BookClubBot')
parser.add_argument('-U', '--dbuser', help='database username')
parser.add_argument('-P', '--dbpassword', help='database password')
parser.add_argument('-H', '--dbhost', help='database hostname or IP', default='localhost')
parser.add_argument('-D', '--db', help='database namespace')
parser.add_argument('token', help='bot token from Discord')
args = parser.parse_args()

dev_mode = (args.devmode > 0)
user_name = args.user
group_name = args.group
email_to = args.emailto
email_from = args.emailfrom
email_subject = args.emailsubject
pid = args.pidfile
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if args.logfile:
    fh = logging.FileHandler(args.logfile, 'w')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

client = discord.Client()
bot_token = args.token

config = {
    'user': args.dbuser,
    'password': args.dbpassword,
    'host': args.dbhost,
    'database': args.db
}
try:
    bot.initialize_db(config)
except:
    logger.exception('could not start database')
    sys.exit(1)

cmds = bot.initialize_bot(client, devmode=dev_mode)

@client.event
async def on_ready():
    logger.debug(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    await cmds.on_message(message)

def send_error_email(content):
    if email_to == None:
        return
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = email_subject
        msg['From'] = email_from
        msg['To'] = email_to
        smtp = smtplib.SMTP('localhost')
        smtp.send_message(msg)
        smtp.quit()
    except:
        logger.exception('Email send failed')

@client.event
async def on_error(event, *args, **kwargs):
    msg = 'Unhandled exception from ' + event + '('
    msg += ', '.join('{0!r}'.format(a) for a in args) + ', '
    msg += ', '.join('{0}={1!r}'.format(k, v) for k, v in kwargs)
    msg += ')'
    logger.exception(msg)
    send_error_email(msg + "\n\n" + traceback.format_exc())
    if event == 'on_message':
        try:
            await cmds.reply(args[0], 'Something went wrong.')
        except:
            pass

def main():
    client.run(bot_token)

sys.stdin.close()
sys.stdout.close()
sys.stderr.close()
daemon = Daemonize(app="bookclubbot", user=user_name, group=group_name, pid=pid, action=main, logger=logger, auto_close_fds=False)
daemon.start()
