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
        status = arg
    elif index == 3:
        table_id = arg
if len(sys.argv) != 4:
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
        if status == 'check':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{table_id}'")
            row_gtg = cs.fetchone()
            try:
                link = row_gtg['group_link']
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

                row_gtg['group_id'] = int(f"-100{result.full_chat.id}")
                cs.execute(f"UPDATE {utl.gtg} SET group_id='{row_gtg['group_id']}' WHERE id='{row_gtg['id']}'")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                row_gtg = cs.fetchone()
                
                info_msg = utl.bot.send_message(chat_id=from_id,text="Configuring ...")
                cs.execute(f"DELETE FROM {utl.analyze}")
                info_msg.edit_text(text="Analyzing ...")
                
                queryKey = ['','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                participants_all_id = []
                participants_all = []
                participants_real = []
                participants_fake = []
                participants_has_phone = []
                participants_online = []
                percent = timestamp_start = i = 0
                for key in queryKey:
                    offset = 0
                    while True:
                        participants = client(functions.channels.GetParticipantsRequest(chat, types.ChannelParticipantsSearch(key), offset, 200, hash=0))
                        if participants.users:
                            for user in participants.users:
                                try:
                                    if not user.id in participants_all_id:
                                        participants_all_id.append(user.id)
                                        if user.username and not user.bot:
                                            username = "@"+user.username
                                            if not username in participants_all:
                                                is_real = is_fake = is_phone = is_online = 0
                                                participants_all.append(username)
                                                if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                    if not username in participants_real:
                                                        participants_real.append(username)
                                                        is_real = 1
                                                elif not username in participants_fake:
                                                    participants_fake.append(username)
                                                    is_fake = 1
                                                if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                    if not username in participants_online:
                                                        participants_online.append(username)
                                                        is_online = 1
                                                if user.phone and not user.phone in participants_has_phone:
                                                    participants_has_phone.append(user.phone)
                                                    is_phone = 1
                                                utl.insert(cs, f"INSERT INTO {utl.analyze} (gtg_id,user_id,username,group_id,is_real,is_fake,is_phone,is_online,created_at) VALUES ('{row_gtg['id']}','{user.id}','{username}','{row_gtg['group_id']}','{is_real}','{is_fake}','{is_phone}','{is_online}','{timestamp}')")
                                except:
                                    pass
                            try:
                                offset += len(participants.users)
                                if (int(time.time()) - timestamp_start) > 4:
                                    cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                                    row_gtg = cs.fetchone()
                                    if not row_gtg:
                                        info_msg.delete()
                                        exit()
                                    elif row_gtg['status_analyze'] == 'end':
                                        break
                                    timestamp_start = int(time.time())
                                    count = len(participants_all_id)
                                    percent = float('{:.2f}'.format(count / participants_count * 100))
                                    percent_key = math.ceil((i / 26) * 100)
                                    if percent >= 100:
                                        break
                                    if percent_key > percent:
                                        percent = percent_key
                                    participants_all_length = len(participants_all)
                                    info_msg.edit_text(
                                        text="⏳ Analyzing...\n\n"+
                                            f"🔗 Link: {row_gtg['group_link']}\n"+
                                            f"♻️ Progress: {percent}%\n"+
                                            f"👥 Members: [{count:,}/{participants_count:,}]\n"+
                                            "➖➖➖➖➖➖\n"+
                                            f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                            f"📅 Duretion: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                                        disable_web_page_preview=True,
                                        reply_markup={'inline_keyboard': [[{'text': "Stop",'callback_data': f"status_analyze;{row_gtg['id']}"}]]}
                                    )
                            except:
                                pass
                        else:
                            break
                    cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                    row_gtg = cs.fetchone()
                    if not row_gtg:
                        info_msg.delete()
                        exit()
                    elif row_gtg['status_analyze'] == 'end':
                        break
                    if percent >= 100:
                        break
                    i += 1
                participants = client(functions.channels.GetParticipantsRequest(chat, types.ChannelParticipantsAdmins(), 0, 200, 0))
                if participants.users:
                    for user in participants.users:
                        try:
                            if user.username:
                                username = "@"+ user.username
                                cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{username}'")
                        except:
                            pass
                if row_gtg['type_send'] == 'unique':
                    i = 0
                    timestamp_start = timestamp = int(time.time())
                    count = cs.execute(f"SELECT {utl.analyze}.id as id,{utl.analyze}.username as username FROM {utl.analyze} INNER JOIN {utl.reports} ON {utl.analyze}.username={utl.reports}.username GROUP BY {utl.reports}.username")
                    result_detect_members = cs.fetchall()
                    for row in result_detect_members:
                        try:
                            cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                            if (int(time.time()) - timestamp_start) > 5:
                                timestamp_start = int(time.time())
                                info_msg.edit_text(
                                    text="⏳ Separation of members...\n\n"+
                                        f"🔗 Link: {row_gtg['group_link']}\n"+
                                        f"♻️ Progress: {(i / count * 100):.2f}%\n"+
                                        "➖➖➖➖➖➖\n"+
                                        f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                        f"📅 Duretion: {utl.convert_time((timestamp_start - timestamp), 2)}",
                                    disable_web_page_preview=True,
                                )
                        except:
                            pass
                        i += 1
                
                print(len(participants_real))
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_bad=0")
                users_all = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_real=1 AND is_bad=0")
                users_real = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_fake=1 AND is_bad=0")
                users_fake = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_phone=1 AND is_bad=0")
                users_has_phone = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_online=1 AND is_bad=0")
                users_online = cs.fetchone()['count']
                
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                row_gtg = cs.fetchone()
                if row_gtg:
                    cs.execute(f"UPDATE {utl.users} SET step='create_order;type_users;{row_gtg['id']}' WHERE user_id='{from_id}'")
                    utl.bot.send_message(
                        chat_id=from_id,
                        text="Select the type of users:\n\n"+
                            f"🔻 All users: {(users_all):,}\n"+
                            f"🔻 Real users: {users_real:,}\n"+
                            f"🔻 Fake users: {users_fake:,}\n"+
                            f"🔻 Online users: {users_online:,}\n"+
                            f"🔻 Users with phone: {users_has_phone:,}\n"+
                            f"⏰ Time: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': 'Real users'},{'text': 'All users'}],
                            [{'text': 'Online users'},{'text': 'Fake users'}],
                            [{'text': 'Users with phone'}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
            except errors.FloodWaitError as e:
                print(f"{row_mbots['phone']}" + str(e))
                end_restrict = int(e.seconds) + int(time.time())
                cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                utl.bot.send_message(chat_id=from_id,text="❌ Analysis account restricted, try again")
            except Exception as e:
                print(f"{row_mbots['phone']}: {e}")
                utl.bot.send_message(chat_id=from_id,text=f"❌ Error\n\n{e}")
        elif status == 'analyze':
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

                cs.execute(f"UPDATE {utl.egroup} SET chat_id='{chat_id}' WHERE id='{row_egroup['id']}'")
                queryKey = ['','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                participants_all_id = []
                participants_all_username = []
                participants_real = []
                participants_fake = []
                participants_has_phone = []
                participants_online = []
                participants_bots = []
                percent = timestamp_start = i = 0
                for key in queryKey:
                    offset = 0
                    while True:
                        participants = client(functions.channels.GetParticipantsRequest(chat,types.ChannelParticipantsSearch(key),offset,200,hash=0))
                        if participants.users:
                            for user in participants.users:
                                try:
                                    if not user.id in participants_all_id:
                                        participants_all_id.append(user.id)
                                        if user.username:
                                            username = f"@{user.username}"
                                            if user.bot:
                                                participants_bots.append(username)
                                            else:
                                                participants_all_username.append(username)
                                                if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                    if not username in participants_real:
                                                        participants_real.append(username)
                                                elif not username in participants_fake:
                                                    participants_fake.append(username)
                                                if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                    if not username in participants_online:
                                                        participants_online.append(username)
                                                if user.phone and not user.phone in participants_has_phone:
                                                    participants_has_phone.append(user.phone)
                                except:
                                    pass
                            try:
                                offset += len(participants.users)
                                if (int(time.time()) - timestamp_start) > 4:
                                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{row_egroup['id']}'")
                                    row_egroup = cs.fetchone()
                                    if row_egroup['status'] == 'end':
                                        break
                                    timestamp_start = int(time.time())
                                    count = len(participants_all_id)
                                    percent = float('{:.2f}'.format(count / participants_count * 100))
                                    if percent >= 100:
                                        break
                                    percent_key = math.ceil((i / 26) * 100)
                                    if percent_key > percent:
                                        percent = percent_key
                                    info_msg.edit_text(
                                        text="⏳ Analyzing...\n\n"+
                                            f"🔗 Link: {link}\n"+
                                            f"♻️ Progress: {percent}%\n"+
                                            f"👥 Members: [{count:,}/{participants_count:,}]\n"+
                                            "➖➖➖➖➖➖\n"+
                                            f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                            f"📅 Duretion: {utl.convert_time((int(time.time()) - timestamp), 2)}",
                                        disable_web_page_preview=True,
                                        reply_markup={'inline_keyboard': [[{'text': "Stop",'callback_data': f"analyze;{row_egroup['id']}"}]]}
                                    )
                            except:
                                pass
                        else:
                            break
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{row_egroup['id']}'")
                    row_egroup = cs.fetchone()
                    if row_egroup['status'] == 'end':
                        break
                    elif percent >= 100:
                        break
                    i += 1
                
                try:
                    os.mkdir(f"export/{row_egroup['id']}")
                except:
                    pass
                users_real = users_fake = users_has_phone = users_online = ""
                for value_ in participants_real:
                    users_real += f"{value_}\n"
                for value_ in participants_fake:
                    users_fake += f"{value_}\n"
                for value_ in participants_has_phone:
                    users_has_phone += f"{value_}\n"
                for value_ in participants_online:
                    users_online += f"{value_}\n"
                
                with open(f"export/{row_egroup['id']}/users_all.txt", 'w') as file:
                    file.write(users_real + users_fake)
                with open(f"export/{row_egroup['id']}/users_real.txt", 'w') as file:
                    file.write(users_real)
                with open(f"export/{row_egroup['id']}/users_fake.txt", 'w') as file:
                    file.write(users_fake)
                with open(f"export/{row_egroup['id']}/users_has_phone.txt", 'w') as file:
                    file.write(users_has_phone)
                with open(f"export/{row_egroup['id']}/users_online.txt", 'w') as file:
                    file.write(users_online)
                users_all_id = len(participants_all_id)
                users_real_count = len(participants_real)
                users_fake_count = len(participants_fake)
                users_has_phone_count = len(participants_has_phone)
                users_online_count = len(participants_online)
                bots_count = len(participants_bots)

                cs.execute(f"UPDATE {utl.egroup} SET status='end',users_real='{users_real_count}',users_fake='{users_fake_count}',users_has_phone='{users_has_phone_count}',users_online='{users_online_count}',participants_count='{participants_count}',participants_online_count='{online_count}',participants_bot_count='{bots_count}' WHERE id='{row_egroup['id']}'")
                utl.bot.send_message(
                    chat_id=from_id,
                    text=f"🔻 ID: <code>{chat_id}</code> (/exgroup_{str(chat_id)[1:]})\n"+
                        f"🔻 Link: {row_egroup['link']}\n"+
                        f"🔻 Total users: {participants_count:,}\n"+
                        f"🔻 Online users: {online_count:,}\n"+
                        f"🔻 Bots: {bots_count}\n"+
                        "‏————————————————————\n"+
                        "♻️ Identified users (with username):\n"+
                        f"🔻 All users: {(users_real_count + users_fake_count):,} (/ex_{row_egroup['id']}_a)\n"+
                        f"🔻 Real users: {users_real_count:,} (/ex_{row_egroup['id']}_u)\n"+
                        f"🔻 Fake users: {users_fake_count:,} (/ex_{row_egroup['id']}_f)\n"+
                        f"🔻 Users with phone: {users_has_phone_count:,} (/ex_{row_egroup['id']}_n)\n"+
                        f"🔻 Online users: {users_online_count:,} (/ex_{row_egroup['id']}_o)\n\n"+
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
