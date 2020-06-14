from .botcommands import BotCommands
from .db import *

import datetime

bp = BotCommands.Blueprint()
@bp.register('checkin', desc='Notify book club members')
async def run_checkin(message, name, argstr):
    discord_server_id = message.channel.guild.id
    result = db_fetchone('SELECT book, pages, meeting_date FROM meeting WHERE meeting_date > CURDATE() AND discord_server_id = %s ORDER BY meeting_date DESC', (discord_server_id,))
    
    if not result:
        return 'No upcoming book club meetings scheduled.'
    
    meeting_date = result["meeting_date"]
    pages = result["pages"]
    
    next_meeting = meeting_date.strftime("%B %e, %Y")
    pages_per_day = int(pages / 30)
    
    days_until_meeting = (meeting_date -  datetime.date.today()).days
    pages_read = pages - (days_until_meeting * pages_per_day)
    
    return f'The next book club meeting is {next_meeting}. We are reading {result["book"]}. You should read {pages_per_day} pages per day, and should have read {pages_read} pages by now.'
