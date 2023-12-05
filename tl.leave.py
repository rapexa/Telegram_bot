#!/usr/bin/env python3

import os
import sys
import time
import jdatetime
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import functions, types, errors
import utility as utl


for index, arg in enumerate(sys.argv):
    if index == 1:
        from_id = arg
    elif index == 2:
        status = arg
if len(sys.argv) != 3:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = cs.cursor()

cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()

info_msg = utl.bot.send_message(chat_id=from_id,text="Configuring ...")
if status == 'group':
    cs.execute(f"SELECT * FROM {utl.mbots} WHERE (status='submitted' OR status='restrict') AND ({timestamp}-last_leave_at)>86400 ORDER BY last_leave_at ASC")
elif status == 'private':
    cs.execute(f"SELECT * FROM {utl.mbots} WHERE (status='submitted' OR status='restrict') AND ({timestamp}-last_delete_chats_at)>86400 ORDER BY last_delete_chats_at ASC")
result = cs.fetchall()
if not result:
    info_msg.edit_text(text="⛔️ No accounts found, each account can be checked every 24 hours")
else:
    timestamp_start = int(time.time())
    count_analyzable = cs.rowcount
    count_analyze = 0
    for row_mbots in result:
        try:
            count_analyze += 1
            client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
            client.connect()
            if not client.is_user_authorized():
                cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
            else:
                if status == 'group':
                    cs.execute(f"UPDATE {utl.mbots} SET last_leave_at='{timestamp}' WHERE id='{row_mbots['id']}'")
                    for dialog in client.iter_dialogs():
                        chat_id = dialog.entity.id
                        if isinstance(dialog.entity, types.Channel):
                            client(functions.channels.LeaveChannelRequest(channel=dialog.entity))
                    if (int(time.time()) - timestamp_start) > 4 or count_analyze == count_analyzable:
                        timestamp_start = int(time.time())
                        percent = (count_analyze / count_analyzable) * 100
                        title = '✅ Leaving chats finished' if count_analyze == count_analyzable else '⏳ Leaving chats...'
                        # reply_markup = {'inline_keyboard': [[{'text': "Stop",'callback_data': "leave"}]]} if count_analyze == count_analyzable else None
                        info_msg.edit_text(
                            text=f"{title}\n\n"+
                                f"♻️ Progress: {percent}%\n"+
                                f"👤 Accounts: [{count_analyze:,} / {count_analyzable:,}]\n"+
                                "➖➖➖➖➖➖\n"+
                                f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                f"📅 Duretion: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                            disable_web_page_preview=True,
                        )
                elif status == 'private':
                    cs.execute(f"UPDATE {utl.mbots} SET last_delete_chats_at='{timestamp}' WHERE id='{row_mbots['id']}'")
                    for dialog in client.iter_dialogs():
                        chat_id = dialog.entity.id
                        if isinstance(dialog.entity, types.User):
                            if chat_id != 178220800 and chat_id != int(row_mbots['user_id']):
                                client.delete_dialog(entity=dialog.entity)
                    if (int(time.time()) - timestamp_start) > 4 or count_analyze == count_analyzable:
                        timestamp_start = int(time.time())
                        percent = (count_analyze / count_analyzable) * 100
                        title = '✅ Deleted chats finished' if count_analyze == count_analyzable else '⏳ Deleting chats...'
                        # reply_markup = {'inline_keyboard': [[{'text': "Stop",'callback_data': "leave"}]]} if count_analyze == count_analyzable else None
                        info_msg.edit_text(
                            text=f"{title}\n\n"+
                                f"♻️ Progress: {percent}%\n"+
                                f"👤 Accounts: [{count_analyze:,} / {count_analyzable:,}]\n"+
                                "➖➖➖➖➖➖\n"+
                                f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                f"📅 Duretion: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                            disable_web_page_preview=True,
                        )
        except Exception as e:
            print(f"{row_mbots['phone']}: {e}")
        finally:
            client.disconnect()

