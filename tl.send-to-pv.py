import os
import re
import time
import psutil
import datetime
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import functions, errors
import utility as utl


directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))
pid_this_thread = int(os.getpid())
result = utl.get_pids_by_full_script_name(f"{directory}/{filename}")
for pid in result:
    if pid_this_thread != pid:
        try:
            pid = psutil.Process(pid)
            pid.terminate()
            time.sleep(2)
        except:
            pass
print(f"ok: {filename}")


def check_report(client, phone):
    try:
        for r in client(functions.messages.StartBotRequest(bot="@spambot",peer="@spambot",start_param="start")).updates:
            for r1 in client(functions.messages.GetMessagesRequest(id=[r.id + 1])).messages:
                if "I’m afraid some Telegram users found your messages annoying and forwarded them to our team of moderators for inspection." in r1.message:
                    if "Unfortunately, your account is now limited" in r1.message:
                        return int(time.time()) + 259200
                    else:
                        regex = re.findall('automatically released on [\d\w ,:]*UTC', r1.message)[0]
                        regex = regex.replace("automatically released on ","")
                        regex = regex.replace(" UTC","")
                        restrict = datetime.datetime.strptime(regex, "%d %b %Y, %H:%M").timestamp()
                        print(f"{phone}: Reported")
                        return restrict
            break
    except:
        pass
    return False


def send_tp_pv(cs, row_admin, row_gtg, row_mbots, result):
    try:
        timestamp = int(time.time())
        count_send = i = count_limit = is_spam = 0
        total_send = cs.execute(f"SELECT id FROM {utl.reports} WHERE gtg_id='{row_gtg['id']}' AND status='send'")

        client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
        client.connect()
        if not client.is_user_authorized():
            print("first_level")
            cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.gtg} SET count_accout=count_accout+1 WHERE id={row_gtg['id']}")
        else:
            restrict = check_report(client, row_mbots['phone'])
            if restrict:
                cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{restrict}' WHERE id={row_mbots['id']}")
                cs.execute(f"UPDATE {utl.gtg} SET count_report=count_report+1 WHERE id={row_gtg['id']}")
            else:
                msgs = []
                cs.execute(f"SELECT * FROM {utl.files} WHERE gtg_id='{row_gtg['id']}'")
                result_plus = cs.fetchall()
                for row_pus in result_plus:
                    msgs.append(client.get_messages(f"@{row_admin['cache']}", ids=row_pus['message_id']))
                for row in result:
                    cs.execute(f"UPDATE {utl.gtg} SET count_request=count_request+1 WHERE id={row_gtg['id']}")
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                    try:
                        for message in msgs:
                            if message.media is None:
                                client.send_message(entity=row['username'], message=message, parse_mode='html') 
                            else:
                                client.send_file(entity=row['username'], file=message, caption=message.message, parse_mode='html') 
                        utl.insert(cs, f"INSERT INTO {utl.reports} (gtg_id,bot_id,user_id,username,group_id,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{row['user_id']}','{row['username']}','{row_gtg['group_id']}','send','{timestamp}')")
                        print(f"{row_mbots['id']} ({i}): Send")
                        count_send += 1
                        if (total_send + count_send) >= row_gtg['count']:
                            break
                    except errors.FloodWaitError as e:
                        print(f"{row_mbots['id']} ({i}): Restricted when Send")
                        end_restrict = int(time.time()) + int(e.seconds)
                        cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                        cs.execute(f"UPDATE {utl.gtg} SET count_restrict=count_restrict+1,count_restrict_error=count_restrict_error+1 WHERE id={row_gtg['id']}")
                        break
                    except Exception as e:
                        error = str(e)
                        print(f"{row_mbots['id']} ({i}): Error when Send ({str(e)})")
                        if 'Too many requests' in error:
                            cs.execute(f"UPDATE {utl.gtg} SET count_usrspam=count_usrspam+1 WHERE id={row_gtg['id']}")
                            count_limit += 1
                            if count_limit > 4 and not is_spam:
                                is_spam = 1
                                cs.execute(f"UPDATE {utl.gtg} SET count_spam=count_spam+1 WHERE id={row_gtg['id']}")
                                if row_admin['time_spam_restrict'] > 0:
                                    end_restrict = int(time.time()) + row_admin['time_spam_restrict']
                                    cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                                    return
                        elif 'No user has' in error or 'The specified user was deleted' in error or 'ResolveUsernameRequest' in error:
                            cs.execute(f"UPDATE {utl.gtg} SET count_userincorrect=count_userincorrect+1 WHERE id={row_gtg['id']}")
                        elif 'You can\'t write in this chat' in error:
                            cs.execute(f"UPDATE {utl.gtg} SET count_restrict_error=count_restrict_error+1 WHERE id={row_gtg['id']}")
                        else:
                            cs.execute(f"UPDATE {utl.gtg} SET count_other_errors=count_other_errors+1 WHERE id={row_gtg['id']}")
                    i += 1
                    if i % 5 == 0:
                        time.sleep(1)
                restrict = check_report(client, row_mbots['phone'])
                if restrict:
                    cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{restrict}' WHERE id={row_mbots['id']}")
                    cs.execute(f"UPDATE {utl.gtg} SET count_report=count_report+1 WHERE id={row_gtg['id']}")
    except Exception as e:
        print(f"{row_mbots['id']} ({i}): Error when Start ({str(e)})")
    finally:
        try:
            client.disconnect()
        except:
            pass
    print(f"{row_mbots['id']} RESULT: [{count_send} / {total_send}]")


while True:
    try:
        timestamp = int(time.time())
        cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        cs = cs.cursor()

        cs.execute(f"SELECT * FROM {utl.admini}")
        row_admin = cs.fetchone()
        limit_per_h = row_admin['limit_per_h'] * 3600
        
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE status='doing'")
        row_gtg = cs.fetchone()
        if row_gtg is not None:
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE gtg_id='{row_gtg['id']}' AND status='send'")
            total_send = cs.fetchone()['count']
            if total_send > 0 and total_send >= row_gtg['count']:
                utl.end_order(cs, f"{directory}/files/exo_{row_gtg['id']}_r.txt", row_gtg)
            else:
                where = ""
                cats = row_gtg['cats'].split(",")
                for category in cats:
                    where += f"cat_id={int(category)} OR "
                where = where[0:-4]
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND ({where}) AND (last_order_at+{limit_per_h})<{timestamp} ORDER BY last_order_at ASC")
                result_mbots = cs.fetchall()
                if result_mbots:
                    for row_mbots in result_mbots:
                        cs.execute(f"SELECT * FROM {utl.analyze} LIMIT {row_gtg['add_per_h']}")
                        result = cs.fetchall()
                        if result:
                            cs.execute(f"UPDATE {utl.mbots} SET last_order_at='{timestamp}' WHERE id={row_mbots['id']}")
                            cs.execute(f"UPDATE {utl.gtg} SET count_acc=count_acc+1,last_bot_check='{row_mbots['phone']}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                            send_tp_pv(cs, row_admin, row_gtg, row_mbots, result)
                        else:
                            utl.end_order(cs, f"{directory}/files/exo_{row_gtg['id']}_r.txt", row_gtg)
                            break
                        timestamp = int(time.time())
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE gtg_id='{row_gtg['id']}' AND status='send'")
                        total_send = cs.fetchone()['count']
                        cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={row_gtg['id']} AND status='doing'")
                        row_gtg = cs.fetchone()
                        if row_gtg is None or (total_send > 0 and total_send >= row_gtg['count']):
                            break
                        else:
                            cs.execute(f"UPDATE {utl.gtg} SET updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                else:
                    utl.end_order(cs, f"{directory}/files/exo_{row_gtg['id']}_r.txt", row_gtg)
    except Exception as e:
        print(f"Error in main: {e}")
    time.sleep(10)

