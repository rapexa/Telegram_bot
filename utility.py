import time
import string
import random
import psutil
import telegram
from config import *

admini = 'pvs_admin_eyrjbyzkgnfrcjnthxspkw3i49u71u'
analyze = 'pvs_analyze_1v6sb9v7jqsfmyti3deoaexhruk2ww'
apis = 'pvs_apis_r8ybbjdxevulwftihtr0la7egnazhi'
cats = 'pvs_cats_pcUXOtiFZyjMmoeCLgzHxWR7Y1qdbJ'
egroup = 'pvs_egroup_btexymj9jkdix1pvl8qncsgufhvodc'
files = 'pvs_files_q1cfyqtmlvbczteyuaiil8moen4hxo'
gtg = 'pvs_gtg_b12qwihpd4otffj30v8mgnieaaspr6'
mbots = 'pvs_mbots_hcxsbtxg0m2lqfuehvduyn58k9a1zd'
reports = 'pvs_reports_uc9ih2ms0rwjdq5laxiestyg3rkcba'
users = 'pvs_users_bhyi9cfucqdyx6nmkozu8pk5wai0vs'

menu_var = '🏛 Main Menu'
panel_var = '👨‍💻 Admin Panel'
back_var = 'Back 🔙'

bot = telegram.Bot(token=token)
get_me = bot.get_me()
bot_id = get_me.id
bot_username = get_me.username

status_mbots = {
    'first_level': 'Not registered ⏳',
    'submitted': 'Active ✅',
    'restrict': 'Limited ⛔️'
}
status_gtg = {
    'start': 'Preparing ❕️',
    'doing': 'Doing ♻️',
    'end': 'Completed ✅',
}


name_list = [
    'Arghavan','Yaran','Parmida','Tara','Samin','Janan','Chakameh','Hadis','Dayan','Zakereh','Roya','Zari','Sara','Shadi','Atefeh','Ghazal',
    'Gasedak','Amal','Aneseh','Atiyeh','Ala','Ayeh','Ayat','Aynoor','Abtesam','Aklil','Akram','Asena','Amira','Amaneh','Amineh','Asila','Aroon',
    'Ima','Asra','Alhan','Alisa','Talia','Tabarak','Tabasom','Taranom','Taktam','Tasnim','Tina','Sana','Smr','Samreh','Samina','Samineh','Samin',
    'Jenan','Hanipha','Hanipheh','Hoora','Hooraneh','Hareh','Hamedeh','Hadis','Hadiseh','Hakimeh','Hosna','Hosniyeh','Hosna','Hasiba','Hamra',
    'Hemaseh','Hana','Hanan','Hananeh','Hoor Afarin','Hoor Rokh','Hoordis','Hoorcad','Hoori Dokht','Hoorosh','Hooriya','Halma','Heliya','Heliyeh',
    'Khazar','Dina','Dorsa','Rada','Rahel','Rafe','Rayehe','Rakeehe','Rahil','Rahmeh','Raziyeh','Rezvaneh','Roman','Roman','Reyhan','Reyhaneh',
    'Raniya','Romisa','Zamzam','Zoofa','Zeytoon',
]


about_list = [
    'Do not let anyone step on your dreams',
    'If you are afraid of the heights of the sky, you cant own the moon',
    'Be deaf when your beautiful dreams are said to be impossible',
    'You only know a part of me; I am a world full of mystery',
    'Be your own hero',
    'Be happy, let them understand that you are stronger than yesterday',
    'In a world full of trends I want to remain a classic',
    'Be strong and firm :) But be kind',
    'Stay kind. It makes you beautiful.',
    'Blocking is for the weak youre gonna see me enjoying my life',
    'You can break me, but you will never destroy me',
    'Never be the same to people, who arent the same to you anymore',
    'always smile laughter embarrasses your enemies',
    'Some people want to see you fail Disappoint them',
    'know the difference between being patient and wasting your time',
    'Silent people have the loudest minds',
    'silence is the most powerful sceam',
    'Live for ourselves not for showing that to others',
    'I will win, not immediately but definitely',
    'Life is short… Smile while you still have teeth',
    'Forgiving someone is easy, trusting them again not',
    'The kites always rise with adverse winds',
    'When you catch in a calumny, you know your real friends',
    'When you realize Your worth youll stop giving people Discounts',
    'Always the huge blaze is from small spunkie',
    'I shine from within so no one can dim my light',
    'We are born to be real, not perfect',
    'I’m a woman with ambition and a heart of gold',
    'Everything started from a dream',
    'Believing in making the impossible possible',
    'We have nothing to fear but fear itself',
    'My mission in life is not merely to survive but thrive',
    'It wasn’t always easy but it’s worth it',
    'Time is precious, waste it wisely',
    'Live each day as if itٌs your last',
    'Life is short. Live passionately',
]


username_list = [
    'mary','jennifer','elizabeth','linda','barbara','susan','margaret','jessica','dorothy','sarah','nancy','betty','lisa','sandra','helen',
    'ashley','donna','kimberly','carol','michelle','emily','amanda','melissa','deborah','laura','stephanie','rebecca','sharon','kathleen',
    'cynthia','ruth','anna','shirley','amy','angela','virginia','brenda','pamela','catherine','nicole','samantha','dennis','diane'
]


def end_order(cs, path, row_gtg):
    cs.execute(f"UPDATE {gtg} SET status='end',updated_at='{int(time.time())}' WHERE id={row_gtg['id']}")
    list_users = ""
    cs.execute(f"SELECT * FROM {analyze} WHERE gtg_id={row_gtg['id']}")
    result_analyze = cs.fetchall()
    if result_analyze:
        for row in result_analyze:
            list_users += f"{row['username']}\n"
        write_on_file(path ,list_users)
        

def read_file(name):
    with open(name, 'r') as file:
        return file.read()


def write_on_file(name,content):
    with open(name, 'w') as file:
        file.write(content)


def insert(cs, sql):
    try:
        cs.execute(sql)
    except:
        pass


def uniq_id_generate(cs, num, table):
    randon_num = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = num)))
    cs.execute(f"SELECT * FROM {table} WHERE uniq_id='{randon_num}'")
    if cs.fetchone() is None:
        return randon_num
    else:
        uniq_id_generate(num,table)


def select_api(cs, num):
    outout = ""
    cs.execute(f"SELECT api_id,count(*) FROM {mbots} GROUP BY api_id HAVING count(*)>={num}")
    result = cs.fetchall()
    if not result:
        cs.execute(f"SELECT * FROM {apis} ORDER BY RAND()")
        return cs.fetchone()
    
    for row in result:
        outout += f"'{row['api_id']}',"
    
    cs.execute(f"SELECT * FROM {apis} WHERE api_id NOT IN ({outout[0:-1]}) ORDER BY RAND()")
    return cs.fetchone()


def convert_time(time, level=4):
    time = int(time)
    day = int(time / 86400)
    hour = int((time % 86400) / 3600)
    minute = int((time % 3600) / 60)
    second = int(time % 60)
    level_check = 1
    if time >= 86400:
        if time == 86400:
            return "1 day"
        output = f"{day} day"
        if hour > 0 and level > level_check:
            output += f", {hour} hour"
            level_check += 1
        if minute > 0 and level > level_check:
            output += f", {minute} minute"
            level_check += 1
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if time >= 3600:
        if time == 3600:
            return "1 hour"
        output = f"{hour} hour"
        if minute > 0 and level > level_check:
            output += f", {minute} minute"
            level_check += 1
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if time >= 60:
        if time == 60:
            return "1 minute"
        output = f"{minute} minute"
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if second > 0:
        return f"{second} second"
    else:
        return f"1 second"

def get_pids_by_full_script_name(script_name):
    pids = []
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            pid = proc.pid
        except psutil.NoSuchProcess:
            continue
        except Exception as e:
            # print(e)
            pass

        if (len(cmdline) >= 2 and 'python3' in cmdline[0] and cmdline[1] == script_name):
            pids.append(int(pid))
    return pids
