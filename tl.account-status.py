#!/usr/bin/env python3

import os
import re
import sys
import time
import pytz
import jdatetime
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import functions, errors
import utility as utl

for index, arg in enumerate(sys.argv):
    if index == 1:
        from_id = arg
    elif index == 2:
        status = arg
    elif index == 3:
        mbot_id = int(arg)
if len(sys.argv) != 4:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = cs.cursor()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbot_id}")
row_mbots = cs.fetchone()
try:
    path = f"{directory}/sessions/{row_mbots['phone']}"
    client = TelegramClient(session=path,api_id=row_mbots['api_id'],api_hash=row_mbots['api_hash'])
    client.connect()
    if client.is_user_authorized():
        if status == 'check':
            get_input_entity = client.get_input_entity(peer=777000)
            code = None
            for message in client.iter_messages(get_input_entity):
                try:
                    code_date = jdatetime.datetime.fromtimestamp(message.date.timestamp(), tz=pytz.timezone('Asia/Tehran'))
                    regex = re.findall('Login code: [\d]*. Do not give this code', message.message)[0]
                    code = regex.replace("Login code: ","").replace(". Do not give this code","")
                    break
                except:
                    pass
            password = f"<code>{row_mbots['password']}</code>" if row_mbots['password'] is not None else "None"
            code = f"<code>{code}</code>\n   📅 {code_date.strftime('%Y-%m-%d %H:%M:%S')}" if code is not None else "None"
            me = client.get_me()
            photo = "No" if me.photo is None else "Yes"
            count_other_sessions = 0
            current_sessions = ""
            for session in client(functions.account.GetAuthorizationsRequest()).authorizations:
                if session.current:
                    date_created = jdatetime.datetime.fromtimestamp(session.date_created.timestamp())
                    date_active = jdatetime.datetime.fromtimestamp(session.date_active.timestamp())
                    current_sessions += f"   🔻 IP: {session.ip}\n"
                    current_sessions += f"   🔻 Country: {session.country}\n"
                    current_sessions += f"   🔻 Device Model: {session.device_model}\n"
                    current_sessions += f"   🔻 Platform: {session.platform}\n"
                    current_sessions += f"   🔻 System Version: {session.system_version}\n"
                    current_sessions += f"   🔻 Api Id: {session.api_id}\n"
                    current_sessions += f"   🔻 App Name: {session.app_name}\n"
                    current_sessions += f"   🔻 App Version: {session.app_version}\n"
                    current_sessions += f"   🔻 Date Created: {date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    current_sessions += f"   🔻 Date Active: {date_active.strftime('%Y-%m-%d %H:%M:%S')}\n"
                else:
                    count_other_sessions += 1
            if count_other_sessions > 0:
                other_sessions = f"\nOther Sessions ({count_other_sessions}):\n"
                other_sessions += f"   🔻 /sessions_{me.phone}\n"
            else:
                other_sessions = "\nOther Sessions: None\n"
            utl.bot.send_message(
                chat_id=from_id,
                text=f"✅ Account is active\n\n"+
                    f"General:\n"+
                    f"   🔻 Phone: <code>{me.phone}</code>\n"+
                    f"   🔻 First Name: {me.first_name}\n"+
                    f"   🔻 Last Name: {me.last_name}\n"+
                    f"   🔻 Username: {me.username}\n"+
                    f"   🔻 Photo: {photo}\n"+
                    "\nCurrent Session:\n"+
                    f"{current_sessions}"+
                    f"{other_sessions}"+
                    f"\nPassword: {password}\n"+
                    f"Last Login Code: {code}",
                parse_mode='HTML'
            )
        elif status == 'sessions':
            i = 0
            for session in client(functions.account.GetAuthorizationsRequest()).authorizations:
                if not session.current:
                    i += 1
                    date_created = jdatetime.datetime.fromtimestamp(session.date_created.timestamp())
                    date_active = jdatetime.datetime.fromtimestamp(session.date_active.timestamp())
                    utl.bot.send_message(
                        chat_id=from_id,
                        text=f"Session {i}:\n"+
                            f"   🔻 IP: {session.ip}\n"
                            f"   🔻 Country: {session.country}\n"
                            f"   🔻 Device Model: {session.device_model}\n"
                            f"   🔻 Platform: {session.platform}\n"
                            f"   🔻 System Version: {session.system_version}\n"
                            f"   🔻 Api Id: {session.api_id}\n"
                            f"   🔻 App Name: {session.app_name}\n"
                            f"   🔻 App Version: {session.app_version}\n"
                            f"   🔻 Date Created: {date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"   🔻 Date Active: {date_active.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            "",
                        parse_mode='HTML'
                    )
    else:
        cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
        utl.bot.send_message(
            chat_id=from_id,
            text="❌ Account unavailable\n\n"+
                "❗️ You can login again"
        )
except errors.PhoneNumberInvalidError as e:
    utl.bot.send_message(chat_id=from_id,text="❌ Wrong phone number")
except errors.FloodWaitError as e:
    utl.bot.send_message(chat_id=from_id,text=f"❌ The account has been blocked for {utl.convert_time(e.seconds, 2)}")
except Exception as e:
    error = str(e)
    if "database is locked" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ Kill the processes and run the robot again")
    elif "You have tried logging in too many times" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ This phone number is limited due to a lot of effort, try again 24 hours later")
    elif "The used phone number has been banned" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ The number is blocked")
    else:
        print(f"Error2: {error}")
        utl.bot.send_message(chat_id=from_id,text=f"❌ Unknown error\n\n{error}")
finally:
    client.disconnect()
    
