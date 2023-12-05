import glob
import os
import time
import string
import random
import psutil
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import functions, types, errors
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


def random_generate(num):
    return str(''.join(random.choices(string.ascii_uppercase + string.digits, k = num)))


while True:
    try:
        timestamp = int(time.time())
        cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        cs = cs.cursor()

        cs.execute(f"SELECT * FROM {utl.admini}")
        row_admin = cs.fetchone()
        
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE status='doing'")
        row_gtg = cs.fetchone()
        if row_gtg is None:
            cs.execute(f"UPDATE {utl.mbots} SET status='submitted' WHERE status='restrict' AND end_restrict<{timestamp}")
            if row_admin['exit_session']:
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE is_exit_session=0 AND (status='submitted' OR status='restrict') AND ({timestamp}-exit_session_at)>43200")
                for row in cs.fetchall():
                    try:
                        cs.execute(f"UPDATE {utl.mbots} SET exit_session_at='{timestamp}' WHERE phone='{row['phone']}'")
                        client = TelegramClient(session=f"{directory}/sessions/{row['phone']}", api_id=row['api_id'], api_hash=row['api_hash'])
                        client.connect()
                        if not client.is_user_authorized():
                            cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE phone='{row['phone']}'")
                            print(f"{row['phone']}: first_level")
                        else:
                            is_ok = True
                            for session in client(functions.account.GetAuthorizationsRequest()).authorizations:
                                if not session.current:
                                    if (timestamp - session.date_created.timestamp()) > 90000:
                                        try:
                                            client(functions.account.ResetAuthorizationRequest(hash=session.hash))
                                            print(f"{row['phone']}: Exit Session")
                                        except:
                                            is_ok = False
                                    else:
                                        is_ok = False
                            if is_ok:
                                cs.execute(f"UPDATE {utl.mbots} SET is_exit_session=1 WHERE phone='{row['phone']}'")
                    except Exception as e:
                        print("Error: " + str(e))
                    finally:
                        try:
                            client.disconnect()
                        except:
                            pass
            if row_admin['change_pass']:
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE is_change_pass=0 AND (status='submitted' OR status='restrict') AND ({timestamp}-change_pass_at)>43200")
                for row in cs.fetchall():
                    try:
                        cs.execute(f"UPDATE {utl.mbots} SET change_pass_at='{timestamp}' WHERE phone='{row['phone']}'")
                        client = TelegramClient(session=f"{directory}/sessions/{row['phone']}", api_id=row['api_id'], api_hash=row['api_hash'])
                        client.connect()
                        if not client.is_user_authorized():
                            cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE phone='{row['phone']}'")
                            print(f"{row['phone']}: first_level")
                        else:
                            try:
                                new_password = random_generate(10)
                                if row['password'] is None or row['password'] == '':
                                    client.edit_2fa(new_password=new_password)
                                else:
                                    client.edit_2fa(current_password=row['password'],new_password=new_password)
                                cs.execute(f"UPDATE {utl.mbots} SET password='{new_password}',is_change_pass=1 WHERE phone='{row['phone']}'")
                                print(f"{row['phone']}: Password Changed")
                            except Exception as e:
                                if "you entered is invalid" in str(e):
                                    print(f"{row['phone']}: Password Invalid")
                                    cs.execute(f"UPDATE {utl.mbots} SET is_change_pass=1 WHERE phone='{row['phone']}'")
                                else:
                                    print("Error Password" + str(e))
                    except Exception as e:
                        print("Error: " + str(e))
                    finally:
                        try:
                            client.disconnect()
                        except:
                            pass
            if row_admin['is_change_profile']:
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE (status='submitted' OR status='restrict') AND is_change_profile=0")
                result = cs.fetchall()
                if result:
                    name_list = utl.name_list
                    about_list = utl.about_list
                    name_list_length = len(name_list) - 1
                    about_list_length = len(about_list) - 1
                    files = glob.glob(f"{directory}/images/*.jpg")
                    files_length = len(files) - 1
                    username_list = utl.username_list
                    username_list_length = len(username_list) - 1
                    i = 0
                    for row_mbots in result:
                        try:
                            i += 1
                            client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
                            client.connect()
                            if not client.is_user_authorized():
                                cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
                            else:
                                client(functions.account.UpdateProfileRequest(first_name=name_list[random.randint(0, name_list_length)],last_name='',about=about_list[random.randint(0, about_list_length)]))
                                client(functions.photos.UploadProfilePhotoRequest(file=client.upload_file(files[random.randint(0, files_length)])))
                                client(functions.photos.UploadProfilePhotoRequest(file=client.upload_file(files[random.randint(0, files_length)])))
                                cs.execute(f"UPDATE {utl.mbots} SET is_change_profile=1 WHERE id='{row_mbots['id']}'")
                                if not row_mbots['is_set_username'] and row_admin['is_set_username']:
                                    client(functions.account.UpdateUsernameRequest(username=username_list[random.randint(0, username_list_length)] + random_generate(10)))
                                    cs.execute(f"UPDATE {utl.mbots} SET is_set_username=1 WHERE id='{row_mbots['id']}'")
                                print(f"{i}. {row_mbots['phone']} : Ok")
                        except Exception as e:
                            print(f"{i}. {row_mbots['phone']} : {e}")
                        finally:
                            try:
                                client.disconnect()
                            except:
                                pass
            if row_admin['is_set_username']:
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE (status='submitted' OR status='restrict') AND is_set_username=0")
                result = cs.fetchall()
                if result:
                    username_list = utl.username_list
                    username_list_length = len(username_list) - 1
                    i = 0
                    for row_mbots in result:
                        try:
                            i += 1
                            client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
                            client.connect()
                            if not client.is_user_authorized():
                                cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
                            else:
                                client(functions.account.UpdateUsernameRequest(username=username_list[random.randint(0, username_list_length)] + random_generate(10)))
                                cs.execute(f"UPDATE {utl.mbots} SET is_set_username=1 WHERE id='{row_mbots['id']}'")
                                print(f"{i}. {row_mbots['phone']} : u Ok")
                        except Exception as e:
                            print(f"{i}. {row_mbots['phone']} : u {e}")
                        finally:
                            try:
                                client.disconnect()
                            except:
                                pass
    except:
        pass
    time.sleep(60)
