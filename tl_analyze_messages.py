import os
import sys
import time
import math
import jdatetime
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import types, functions, errors
import utility as utl

for index, arg in enumerate(sys.argv):
    if index == 1:
        from_id = arg
    elif index == 2:
        table_id = arg
if len(sys.argv) != 3:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = cs.cursor()

cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' ORDER BY RAND()")
row_mbots = cs.fetchone()
if not row_mbots:
    utl.bot.send_message(chat_id=from_id,text=f"⛔️ No accounts found")
    exit()
try:
    client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
    client.connect()
    if not client.is_user_authorized():
        cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
        utl.bot.send_message(chat_id=from_id,parse_mode='HTML',text=f"⛔️ Account /status_{row_mbots['id']} was unavailable (<code>{row_mbots['phone']}</code>)")
    else:
        cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{table_id}'")
        row_egroup = cs.fetchone()
        info_msg = utl.bot.send_message(chat_id=from_id,text="Analyzing ...")
        try:
            link = row_egroup['link']
            try:
                client(functions.channels.GetParticipantRequest(channel=link,participant="me"))
            except:
                try:
                    if "/joinchat/" in link:
                        client(functions.messages.ImportChatInviteRequest(link.split("/joinchat/")[1]))
                    else:
                        client(functions.channels.JoinChannelRequest(channel=link))
                except errors.UserAlreadyParticipantError as e:
                    pass
            result = client(functions.channels.GetFullChannelRequest(channel=link))
            chat = result.full_chat.id
            chat_id = int(f"-100{chat}")
            participants_count = result.full_chat.participants_count
            online_count = result.full_chat.online_count
            cs.execute(f"UPDATE {utl.egroup} SET chat_id='{chat_id}' WHERE id={row_egroup['id']}")
            
            first_message_id = 0
            last_message_id = 0
            participants_all_id = []
            participants_all = []
            participants_bots = []
            timestamp_start = i = 0
            for message in client.iter_messages(chat_id):
                last_message_id = message.id
                if not first_message_id:
                    first_message_id = message.id
                if isinstance(message, types.Message):
                    try:
                        if message.from_id is not None and isinstance(message.from_id, types.PeerUser):
                            user_id = message.from_id.user_id
                            if not user_id in participants_all_id:
                                participants_all_id.append(user_id)
                                result = client.get_entity(user_id)
                                if result.bot:
                                    participants_bots.append(f"@{result.username}")
                                elif result.username is not None:
                                    participants_all.append(f"@{result.username}")
                            
                    except Exception as e:
                        print(e)
                if (int(time.time()) - timestamp_start) > 5:
                    timestamp_start = int(time.time())
                    info_msg.edit_text(
                        text="⏳ Analyzing...\n\n"+
                            f"🔗 Link: {link}\n"+
                            f"♻️ Analyzed messages: {(first_message_id-last_message_id):,}\n"+
                            f"👥 All Members: {len(participants_all_id):,}\n"+
                            f"👥 Username Members: {len(participants_all):,}\n"+
                            "➖➖➖➖➖➖\n"+
                            f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                            f"📅 Duretion: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                        disable_web_page_preview=True,
                        reply_markup={'inline_keyboard': [[{'text': "Stop",'callback_data': f"analyze;{row_egroup['id']}"}]]}
                    )
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={row_egroup['id']}")
                    row_egroup = cs.fetchone()
                    if row_egroup['status'] == 'end':
                        break
            
            try:
                os.mkdir(f"export/{row_egroup['id']}")
            except:
                pass
            users_all = users_username = users_bots = ""
            for value_ in participants_all_id:
                users_all += f"{value_}\n"
            for value_ in participants_all:
                users_username += f"{value_}\n"
            for value_ in participants_bots:
                users_bots += f"{value_}\n"
            
            with open(f"export/{row_egroup['id']}/users_all.txt", 'w') as file:
                file.write(users_all)
            with open(f"export/{row_egroup['id']}/users_username.txt", 'w') as file:
                file.write(users_username)
            with open(f"export/{row_egroup['id']}/users_bots.txt", 'w') as file:
                file.write(users_bots)
            row_egroup['chat_id'] = str(chat_id)
            row_egroup['participants_count'] = participants_count
            row_egroup['participants_online_count'] = online_count
            row_egroup['users_all'] = len(participants_all_id)
            row_egroup['users_real'] = len(participants_all)
            row_egroup['participants_bot_count'] = len(participants_bots)
            
            cs.execute(f"UPDATE {utl.egroup} SET status='end',users_all={row_egroup['users_all']},users_real={row_egroup['users_real']},participants_count={row_egroup['participants_count']},participants_online_count={row_egroup['participants_online_count']},participants_bot_count={row_egroup['participants_bot_count']} WHERE id={row_egroup['id']}")
            utl.bot.send_message(
                chat_id=from_id,
                text=f"🔻 ID: <code>{row_egroup['chat_id']}</code>\n"+
                    f"🔻 Link: {row_egroup['link']}\n"+
                    f"🔻 Total users: {row_egroup['participants_count']:,}\n"+
                    f"🔻 Online users: {row_egroup['participants_online_count']:,}\n"+
                    "‏————————————————————\n"+
                    "♻️ Identified users:\n"+
                    f"🔻 All users: {row_egroup['users_all']:,} (/ex_{row_egroup['id']}_a)\n"+
                    f"🔻 Username users: {row_egroup['users_real']:,} (/ex_{row_egroup['id']}_u)\n"+
                    f"🔻 Bots: {row_egroup['participants_bot_count']:,} (/ex_{row_egroup['id']}_u)\n"+
                    f"⏰ Time: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                parse_mode='HTML',
                disable_web_page_preview=True,
            )
        except errors.FloodWaitError as e:
            print(f"{row_mbots['phone']}" + str(e))
            end_restrict = int(e.seconds) + int(time.time())
            cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
            utl.bot.send_message(chat_id=from_id,text="❌ Analysis account restricted, try again")
        except Exception as e:
            print(f"{row_mbots['phone']}" + str(e))
            utl.bot.send_message(chat_id=from_id,text="❌ There was a problem with the account becoming a member of the group")
except Exception as e:
    print(e)
    utl.bot.send_message(chat_id=from_id,text=f"❌ There was an error connecting to account /status_{row_mbots['id']}")
finally:
    client.disconnect()
try:
    info_msg.delete()
except:
    pass
