#!/usr/bin/env python3

import os
import sys
import time
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import errors
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
    if status == 'first_level':
        client = TelegramClient(session=path,api_id=row_mbots['api_id'],api_hash=row_mbots['api_hash'])
        client.connect()
        if client.is_user_authorized():
            me = client.get_me()
            cs.execute(f"UPDATE {utl.mbots} SET user_id='{me.id}',status='submitted' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
            utl.bot.send_message(chat_id=from_id,text=f"✅ Account is active")
            exit()
        else:
            client.disconnect()
            try:
                os.remove(f"{directory}/sessions/{row_mbots['phone']}.session")
            except:
                pass
    client = TelegramClient(session=path,api_id=row_mbots['api_id'],api_hash=row_mbots['api_hash'])
    client.connect()
    if status == 'first_level':
        me = client.send_code_request(phone=row_mbots['phone'])
        cs.execute(f"UPDATE {utl.mbots} SET phone_code_hash='{me.phone_code_hash}',code=null,password=null WHERE id={row_mbots['id']}")
        cs.execute(f"UPDATE {utl.users} SET step='add_acc;code;{row_mbots['id']}' WHERE user_id='{from_id}'")
        utl.bot.send_message(
            chat_id=from_id,
            text="Enter the code and password:\n\n"+
                "❕ Example without password:\n"+
                "12345\n\n"+
                "❕ Example with password:\n"+
                "code\n"+
                "password"
        )
    elif status == 'code':
        is_ok = True
        try:
            me = client.sign_in(phone=row_mbots['phone'],phone_code_hash=row_mbots['phone_code_hash'],code=row_mbots['code'])
        except errors.PhoneCodeInvalidError as e:
            utl.bot.send_message(chat_id=from_id,text="❌ Code is wrong")
            is_ok = False
        except errors.SessionPasswordNeededError as e:
            if row_mbots['password'] is None:
                utl.bot.send_message(
                    chat_id=from_id,
                    text="❌ The account has a password!\n\n" +
                        "code\n" +
                        "password\n\n" +
                        "❕ For example, send each one in a line",
                )
                is_ok = False
            else:
                me = client.sign_in(password=row_mbots['password'])
        if is_ok:
            cs.execute(f"UPDATE {utl.mbots} SET user_id='{me.id}',status='submitted' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
            utl.bot.send_message(chat_id=from_id,text="✅ Successfully registered")
except errors.PhoneCodeExpiredError as e:
    utl.bot.send_message(chat_id=from_id,text="❌ Code expired")
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
    elif "The password (and thus its hash value) you entered is invalid" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ Wrong password")
    else:
        print(f"Error2: {error}")
        utl.bot.send_message(chat_id=from_id,text=f"❌ Unknown error\n\n{error}")
finally:
    client.disconnect()
    
