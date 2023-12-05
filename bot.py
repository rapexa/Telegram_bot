import os
import re
import time
import psutil
try:
    import requests
except:
    pass
import jdatetime
import pymysql.cursors
from telegram import Update, ChatPermissions,  ForceReply, chat, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler,CallbackQueryHandler, Filters, CallbackContext
from telegram.error import RetryAfter, TimedOut
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

if not os.path.exists(f"{directory}/sessions"):
    os.mkdir(f"{directory}/sessions")
if not os.path.exists(f"{directory}/import"):
    os.mkdir(f"{directory}/import")
if not os.path.exists(f"{directory}/export"):
    os.mkdir(f"{directory}/export")


step_page = 10


def user_panel(update,text=None):
    if not text:
        text = "User area:"
    update.message.reply_html(text=text,
        reply_markup={'resize_keyboard': True,'keyboard': [
            [{'text': '📊 Stats'}],
            [{'text': '➕ Create Order'}],
            [{'text': '➕ Add Account'}, {'text': '📋 Accounts'}],
            [{'text': '➕ Add Api'}, {'text': '➕ Create Category'}],
            [{'text': '📋 list'}],
            [{'text': '🔮 Analysis'}, {'text': '⚙️ Settings'}],
            [{'text': '📞 support'}, {'text': '📚 more'}],
        ]}
    )


class Pagination:
    def __init__(self,update,type_btn,output,step_page,num_all_pages):
        self.update = update
        self.type_btn = type_btn
        self.text = output
        self.step_page = step_page
        self.num_all_pages = num_all_pages

    def setStepPage(self,step_page):
        self.step_page = step_page
    
    def setText(self,text):
        self.text = text
    
    def setNumAllPages(self,num_all_pages):
        self.num_all_pages = num_all_pages
    
    def processMessage(self):
        if self.num_all_pages > self.step_page:
            self.update.message.reply_html(
                disable_web_page_preview=True,
                text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"Page 2 >>", 'callback_data': f"pg;{self.type_btn};2"}]]}
            )
        else:
            self.update.message.reply_html(disable_web_page_preview=True,text=self.text)
        return
    
    def processCallback(self):
        query = self.update.callback_query
        ex_data = query.data.split(";")
        num_current_page = int(ex_data[2])
        num_prev_page = num_current_page - 1
        num_next_page = num_current_page + 1
        if num_current_page == 1:
            query.edit_message_text(
                parse_mode='HTML',
                disable_web_page_preview=True,
                text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"Page {num_next_page} >>", 'callback_data': f"pg;{self.type_btn};{num_next_page}"}]]}
            )
        elif self.num_all_pages > (num_current_page * self.step_page):
            query.edit_message_text(
                parse_mode='HTML',
                disable_web_page_preview=True,
                text=self.text,
                reply_markup={'inline_keyboard': [
                    [{'text': f"<< Page {num_prev_page}", 'callback_data': f"pg;{self.type_btn};{num_prev_page}"},
                    {'text': f"Page {num_next_page} >>", 'callback_data': f"pg;{self.type_btn};{num_next_page}"}]
                ]}
            )
        else:
            query.edit_message_text(
                parse_mode='HTML',
                disable_web_page_preview=True,
                text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"<< Page {num_prev_page}", 'callback_data': f"pg;{self.type_btn};{num_prev_page}"}]]}
            )
        return


def callbackquery_process(update: Update, context: CallbackContext) -> None:
    # utl.write_on_file("callbackquery_process.txt",str(update))
    bot = context.bot
    query = update.callback_query
    from_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data
    ex_data = data.split(';')
    timestamp = int(time.time())
    try:
        if data == "test":
            return
        elif data == "nazan":
            return query.answer("Do not touch 😕")
        cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        cs = cs.cursor()

        cs.execute(f"SELECT * FROM {utl.admini}")
        row_admin = cs.fetchone()
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
        row_user = cs.fetchone()
        is_admin = True if from_id == utl.admin_id or row_user['status'] == 'admin' else False
        
        if row_admin['gtg_per'] or is_admin:
            if ex_data[0] == 'update':
                gtg_id = int(ex_data[1])
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    query.answer("❌ Not found",show_alert=True)
                else:
                    created_at = jdatetime.datetime.fromtimestamp(row_gtg['created_at']).strftime('%Y/%m/%d %H:%M:%S')
                    updated_at = jdatetime.datetime.fromtimestamp(row_gtg['updated_at']).strftime('%Y/%m/%d %H:%M:%S')
                    inline_keyboard = []
                    if not is_admin or row_gtg['status'] == 'end':
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': "nazan"}])
                    else:
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}])
                    inline_keyboard.append([{'text': '🔄 Update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                    
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE gtg_id={row_gtg['id']} AND status='send'")
                    count_done = cs.fetchone()['count']
                    if row_gtg['group_link'] is not None:
                        output = f"🆔 <code>{row_gtg['group_id']}</code>\n"
                        output += f"🔗 {row_gtg['group_link']}\n\n"
                    else:
                        output = ""
                    last_bot_check = f"🟠 Account under review: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] is not None and row_gtg['status'] != "end" else ""
                    if row_gtg['cats'] is None:
                        cats = "Not supported"
                    else:
                        where = ""
                        cats = row_gtg['cats'].split(",")
                        for category in cats:
                            where += f"id={int(category)} OR "
                        where = where[0:-4]
                        cats = ""
                        cs.execute(f"SELECT * FROM {utl.cats} WHERE {where}")
                        result = cs.fetchall()
                        for row in result:
                            cats += f"{row['name']},"
                        cats = cats[0:-1]
                    count_send_per_account = row_gtg['add_per_h'] if row_gtg['add_per_h'] > 0 else "Not supported"
                    query.edit_message_text(
                        text=f"{output}"+
                            f"👤 Send / Requested: [{count_done:,} / {row_gtg['count']:,}]\n"+
                            f"👤 Checking / Max: [{row_gtg['count_request']:,} / {row_gtg['max_users']:,}]\n\n"+
                            f"{last_bot_check}"+
                            f"🔵 Total accounts: {row_gtg['count_acc']}\n"+
                            f"🔵 Spam accounts: {row_gtg['count_spam']}\n"+
                            f"🔵 Restricted accounts: {row_gtg['count_restrict']}\n"+
                            f"🔵 Reported accounts: {row_gtg['count_report']}\n"+
                            f"🔵 Lost accounts: {row_gtg['count_accout']}\n\n"+
                            f"🔴 Get spam errors: {row_gtg['count_usrspam']}\n"+
                            f"🔴 Incorrect username errors: {row_gtg['count_userincorrect']}\n"+
                            f"🔴 Restricted accounts: {row_gtg['count_restrict_error']}\n"+
                            f"🔴 Other errors: {row_gtg['count_other_errors']}\n\n"+
                            f"🟣 Categories: {cats}\n"+
                            f"🟣 Count send per account: {count_send_per_account}\n\n"+
                            f"⚪️ Remaining send output: /exo_{row_gtg['id']}_r\n"+
                            f"⚪️ Successful send output: /exo_{row_gtg['id']}_m\n"+
                            "➖➖➖➖➖➖\n"+
                            f"📅️ Created: {created_at}\n"+
                            f"📅️ Updated: {updated_at}\n"+
                            f"📅️ ️Now: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup={'inline_keyboard': inline_keyboard}
                    )
                return
        if from_id == utl.admin_id or row_user['status'] == 'admin':
            if ex_data[0] == 'pg':
                if ex_data[1] == 'accounts':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                            row_cats = cs.fetchone()
                            if row['status'] == 'restrict':
                                output += f"{i}. Phone: <code>{row['phone']}</code>\n"
                                output += f"⛔ Limitations: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                            else:
                                output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"📂 Category: /category_{row['id']} ({row_cats['name']})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"❌ Delete: /delete_{row['id']}\n\n"
                            i += 1
                        output = f"List of all accounts:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"accounts",output,step_page,count)
                        ob.processCallback()
                elif ex_data[1] == 'restrict':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='restrict' ORDER BY end_restrict ASC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                            row_cats = cs.fetchone()
                            output += f"{i}. Phone: <code>{row['phone']}</code>\n"
                            output += f"⛔ Limitations: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                            output += f"📂 Category: /category_{row['id']} ({row_cats['name']})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"❌ Delete: /delete_{row['id']}\n\n"
                            i += 1
                        output = f"List of restricted accounts:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='restrict' AND user_id IS NOT NULL")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"restrict",output,step_page,count)
                        ob.processCallback()
                elif ex_data[1] == 'first_level':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='first_level' AND user_id IS NOT NULL ORDER BY last_order_at DESC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                            row_cats = cs.fetchone()
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"📂 Category: /category_{row['id']} ({row_cats['name']})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"❌ Delete: /delete_{row['id']}\n\n"
                            i += 1
                        output = f"List of unregistered accounts:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='first_level' AND user_id IS NOT NULL")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"first_level",output,step_page,count)
                        ob.processCallback()
                elif ex_data[1] == 'submitted':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' ORDER BY last_order_at ASC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                            row_cats = cs.fetchone()
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"📂 Category: /category_{row['id']} ({row_cats['name']})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"❌ Delete: /delete_{row['id']}\n\n"
                            i += 1
                        output = f"List of active accounts:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted' AND user_id IS NOT NULL")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"submitted",output,step_page,count)
                        ob.processCallback()
                elif ex_data[1] == 'adability':
                    limit_per_h = row_admin['limit_per_h'] * 3600
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp} ORDER BY last_order_at ASC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row['cat_id']}")
                            row_cats = cs.fetchone()
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"📂 Category: /category_{row['id']} ({row_cats['name']})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"❌ Delete: /delete_{row['id']}\n\n"
                            i += 1
                        output = f"List of accounts that can be sent:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted' AND user_id IS NOT NULL AND (last_order_at+{limit_per_h})<{timestamp}")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"adability",output,step_page,count)
                        ob.processCallback()
                elif ex_data[1] == 'orders':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.gtg} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            created_at = jdatetime.datetime.fromtimestamp(row['created_at'])
                            count_done = cs.execute(f"SELECT id FROM {utl.reports} WHERE gtg_id={row['id']} AND status='send'")
                            output += f"{i}. /gtg_{row['id']}\n"
                            output += f"🔹️ Group: {row['group_link']}\n"
                            output += f"🔹️ Send / Requested: [{count_done} / {row['count']}]\n"
                            output += f"🔹️ Status: {utl.status_gtg[row['status']]}\n"
                            output += f"📅️ {created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                            i += 1
                        output = f"Order list:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg}")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"orders",output,step_page,count)
                        ob.processCallback()
                        cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
                elif ex_data[1] == 'categories':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.cats} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row['id']}")
                            count_mbots = cs.fetchone()['count']
                            output += f"{i}. Name: {row['name']} ({count_mbots})\n"
                            output += f"❌ Delete: /DeleteCat_{row['id']}\n\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.cats}")
                        rowcount = cs.fetchone()['count']
                        output = f"📜 Categories ({rowcount})\n\n{output}"
                        ob = Pagination(update, "categories", output, step_page, rowcount)
                        ob.processCallback()
                    return
                elif ex_data[1] == 'apis':
                    selected_pages = (int(ex_data[2]) - 1) * step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                    result = cs.fetchall()
                    if not result:
                        query.answer("⛔️ There is no other page")
                    else:
                        output = ""
                        for row in result:
                            output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                            output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                            output += f"❌ Delete: /DeleteApi_{row['id']}\n\n"
                            i += 1
                        cs.output = f"List of api:\n\n{output}"
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                        count = cs.fetchone()['count']
                        ob = Pagination(update,"apis",output,step_page,count)
                        ob.processCallback()
                        cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
                return
            elif ex_data[0] == 'settings':
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
                row_gtg = cs.fetchone()
                if row_gtg:
                    return query.answer("❌ There is an active order",show_alert=True)
                elif ex_data[1] == 'time_spam_restrict':
                    row_admin['time_spam_restrict'] += (int(ex_data[2]) * 86400)
                    if row_admin['time_spam_restrict'] < 0:
                        return query.answer("❌ Must be at least 0",show_alert=True)
                    cs.execute(f"UPDATE {utl.admini} SET time_spam_restrict={row_admin['time_spam_restrict']}")
                elif ex_data[1] == 'change_pass' or ex_data[1] == 'exit_session' or ex_data[1] == 'is_change_profile' or ex_data[1] == 'is_set_username' or ex_data[1] == 'gtg_per':
                    row_admin[ex_data[1]] = 1 - row_admin[ex_data[1]]
                    cs.execute(f"UPDATE {utl.admini} SET {ex_data[1]}={row_admin[ex_data[1]]}")
                else:
                    number = int(ex_data[2])
                    if ex_data[1] == 'api_per_number':
                        row_admin['api_per_number'] += number
                        if row_admin['api_per_number'] < 1:
                            return query.answer("❌ Must be at least 1")
                        else:
                            cs.execute(f"UPDATE {utl.admini} SET api_per_number={row_admin['api_per_number']}")
                    elif ex_data[1] == 'add_per_h':
                        row_admin['add_per_h'] += number
                        if row_admin['add_per_h'] < 3:
                            return query.answer("❌ Must be at least 3")
                        elif row_admin['add_per_h'] > 100:
                            return query.answer("❌ The maximum must be 100")
                        else:
                            cs.execute(f"UPDATE {utl.admini} SET add_per_h={row_admin['add_per_h']}")
                    elif ex_data[1] == 'limit_per_h':
                        row_admin['limit_per_h'] += number
                        if row_admin['limit_per_h'] < 0:
                            return query.answer("❌ Must be at least 0")
                        else:
                            cs.execute(f"UPDATE {utl.admini} SET limit_per_h={row_admin['limit_per_h']}")
                api_per_number = f"Register {row_admin['api_per_number']} accounts in each api" if row_admin['api_per_number'] <= 5 else f"⚠️ Register {row_admin['api_per_number']} accounts in each api ⚠️"
                add_per_h = f"Each account will send {row_admin['add_per_h']} in each use" if row_admin['add_per_h'] <= 16 else f"⚠️ Each account will send {row_admin['add_per_h']} in each use ⚠️"
                limit_per_h = f"Use each account every {row_admin['limit_per_h']} hours" if row_admin['limit_per_h'] >= 24 else f"⚠️ Use each account every {row_admin['limit_per_h']} hours ⚠️"
                time_spam_restrict = int(row_admin['time_spam_restrict'] / 86400)
                change_pass = "✅ Change / Set two step password ✅" if row_admin['change_pass'] else "❌ Change / Set two step password ❌"
                exit_session = "✅ Exit the rest of the sessions ✅" if row_admin['exit_session'] else "❌ Exit the rest of the sessions ❌"
                is_change_profile = "✅ Set name, bio and profile ✅" if row_admin['is_change_profile'] else "❌ Set name, bio and profile ❌"
                is_set_username = "✅ Set username ✅" if row_admin['is_set_username'] else "❌ Set username ❌"
                gtg_per = "✅ All access to the order ID ✅" if row_admin['gtg_per'] else "❌ All access to the order ID ❌"

                query.edit_message_text(
                    text=f"Settings:",
                    reply_markup={'inline_keyboard': [
                        [{'text': api_per_number,'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;api_per_number;+10"},
                            {'text': '+5','callback_data': "settings;api_per_number;+5"},
                            {'text': '+1','callback_data': "settings;api_per_number;+1"},
                            {'text': '-1','callback_data': "settings;api_per_number;-1"},
                            {'text': '-5','callback_data': "settings;api_per_number;-5"},
                            {'text': '-10','callback_data': "settings;api_per_number;-10"},
                        ],
                        [{'text': add_per_h,'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;add_per_h;+10"},
                            {'text': '+5','callback_data': "settings;add_per_h;+5"},
                            {'text': '+1','callback_data': "settings;add_per_h;+1"},
                            {'text': '-1','callback_data': "settings;add_per_h;-1"},
                            {'text': '-5','callback_data': "settings;add_per_h;-5"},
                            {'text': '-10','callback_data': "settings;add_per_h;-10"},
                        ],
                        [{'text': limit_per_h,'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;limit_per_h;+10"},
                            {'text': '+5','callback_data': "settings;limit_per_h;+5"},
                            {'text': '+1','callback_data': "settings;limit_per_h;+1"},
                            {'text': '-1','callback_data': "settings;limit_per_h;-1"},
                            {'text': '-5','callback_data': "settings;limit_per_h;-5"},
                            {'text': '-10','callback_data': "settings;limit_per_h;-10"},
                        ],
                        [{'text': f"Account should rest for {time_spam_restrict} day when receiving spam",'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;time_spam_restrict;+10"},
                            {'text': '+5','callback_data': "settings;time_spam_restrict;+5"},
                            {'text': '+1','callback_data': "settings;time_spam_restrict;+1"},
                            {'text': '-1','callback_data': "settings;time_spam_restrict;-1"},
                            {'text': '-5','callback_data': "settings;time_spam_restrict;-5"},
                            {'text': '-10','callback_data': "settings;time_spam_restrict;-10"},
                        ],
                        [{'text': change_pass,'callback_data': "settings;change_pass"}],
                        [{'text': exit_session,'callback_data': "settings;exit_session"}],
                        [{'text': is_change_profile,'callback_data': "settings;is_change_profile"}],
                        [{'text': is_set_username,'callback_data': "settings;is_set_username"}],
                        [{'text': gtg_per,'callback_data': "settings;gtg_per"}],
                    ]}
                )
                return
            elif ex_data[0] == 'change_status':
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_data[1])}")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    query.answer("❌ Not found")
                else:
                    inline_keyboard = []
                    if row_gtg['status'] == 'doing':
                        if ex_data[2] == 'none':
                            inline_keyboard.append([{'text': 'Are you sure?', 'callback_data': "nazan"}])
                            inline_keyboard.append([{'text': '❌ Cancel ❌', 'callback_data': f"update;{row_gtg['id']}"},{'text': '✅ End ✅', 'callback_data': f"change_status;{row_gtg['id']};end"}])
                            return query.edit_message_reply_markup(reply_markup={'inline_keyboard': inline_keyboard})
                        elif ex_data[2] == 'end':
                            row_gtg['status'] = 'end'
                            utl.end_order(cs, f"{directory}/files/exo_{row_gtg['id']}_r.txt", row_gtg)
                    inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': "nazan"}])
                    inline_keyboard.append([{'text': '🔄 Update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                    query.edit_message_reply_markup(reply_markup={'inline_keyboard': inline_keyboard})
                return
            elif ex_data[0] == "d":
                cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_data[1]}'")
                row_user_select = cs.fetchone()
                if row_user_select is None:
                    query.answer("❌ Not found")
                else:
                    value = ex_data[2]
                    if value == 'balance':
                        change_balance = row_user_select['balance'] + int(ex_data[3])
                        if change_balance <= 0:
                            if not row_user_select['balance']:
                                return query.answer("❌ It's impossible",show_alert=True)
                            else:
                                row_user_select['balance'] = 0
                        else:
                            row_user_select['balance'] = change_balance
                        cs.execute(f"UPDATE {utl.users} SET balance='{row_user_select['balance']}' WHERE user_id='{row_user_select['user_id']}'")
                    if value == 'is_submit_panel':
                        row_user_select['is_submit_panel'] = 1 - row_user_select['is_submit_panel']
                        cs.execute(f"UPDATE {utl.users} SET is_submit_panel='{row_user_select['is_submit_panel']}' WHERE user_id='{row_user_select['user_id']}'")
                    else:
                        if value == "admin" or ((value == "user" or value == "block") and row_user_select['status'] == 'admin'):
                            if utl.admin_id == from_id:
                                cs.execute(f"UPDATE {utl.users} SET status='{value}' WHERE user_id='{row_user_select['user_id']}'")
                            else:
                                return query.answer("⛔️ This function is for the main admin",show_alert=True)
                        elif value == "block" or value == "user":
                            cs.execute(f"UPDATE {utl.users} SET status='{value}' WHERE user_id='{row_user_select['user_id']}'")
                        elif value == "sendmsg":
                            cs.execute(f"UPDATE {utl.users} SET step='sendmsg;{row_user_select['user_id']}' WHERE user_id='{from_id}'")
                            return bot.send_message(
                                chat_id=chat_id,
                                text="Send the message:\n"+
                                    "Cancel: /panel"
                            )
                        else:
                            return
                    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{row_user_select['user_id']}'")
                    row_user_select = cs.fetchone()
                    block = 'Block ✅' if row_user_select['status'] == "block" else 'Block ❌'
                    block_status = 'user' if row_user_select['status'] == "block" else 'block'
                    admin = 'Admin ✅' if row_user_select['status'] == "admin" else 'Admin ❌'
                    admin_status = 'user' if row_user_select['status'] == "admin" else 'admin'
                    query.edit_message_text(parse_mode='HTML',text=f"User <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                        reply_markup={'inline_keyboard': [
                            [{'text': "Send Message",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                            [
                                {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                                {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                            ]
                        ]}
                    )
                return
            elif ex_data[0] == "analyze":
                cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{ex_data[1]}'")
                row_egroup = cs.fetchone()
                if row_egroup is None:
                    query.answer("❌ Not found")
                else:
                    cs.execute(f"UPDATE {utl.egroup} SET status='end' WHERE id='{row_egroup['id']}'")
                    query.edit_message_reply_markup(
                        reply_markup={'inline_keyboard': [[{'text': "Running out ...",'callback_data': "nazan"}]]}
                    )
                return
            elif ex_data[0] == "status_analyze":
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{ex_data[1]}'")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    query.answer("❌ Not found")
                else:
                    cs.execute(f"UPDATE {utl.gtg} SET status_analyze='end' WHERE id='{row_gtg['id']}'")
                    query.edit_message_reply_markup(
                        reply_markup={'inline_keyboard': [[{'text': "Running out ...",'callback_data': "nazan"}]]}
                    )
                return
    except RetryAfter as e:
        query.answer(f"⚠️ Try again {e.retry_after} seconds later", show_alert=True)


def private_process(update: Update, context: CallbackContext) -> None:
    # utl.write_on_file("private_process.txt",str(update))
    bot = context.bot
    message = update.message
    from_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text if message.text else ""
    if message.text:
        txtcap = message.text
    elif message.caption:
        txtcap = message.caption
    ex_text = text.split('_')
    timestamp = int(time.time())

    cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    cs = cs.cursor()

    cs.execute(f"SELECT * FROM {utl.admini}")
    row_admin = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
    row_user = cs.fetchone()
    if row_user is None:
        uniq_id = utl.uniq_id_generate(cs,10,utl.users)
        cs.execute(f"INSERT INTO {utl.users} (user_id,status,step,created_at,uniq_id) VALUES ('{from_id}','user','start','{timestamp}','{uniq_id}')")
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
        row_user = cs.fetchone()
    ex_step = row_user['step'].split(';')
    is_admin = True if from_id == utl.admin_id or row_user['status'] == 'admin' else False
    
    if row_admin['gtg_per'] or is_admin:
        if ex_text[0] == '/gtg':
            gtg_id = int(ex_text[1])
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ No found")
            else:
                created_at = jdatetime.datetime.fromtimestamp(row_gtg['created_at']).strftime('%Y/%m/%d %H:%M:%S')
                updated_at = jdatetime.datetime.fromtimestamp(row_gtg['updated_at']).strftime('%Y/%m/%d %H:%M:%S')
                inline_keyboard = []
                if not is_admin or row_gtg['status'] == 'end':
                    if not is_admin and row_gtg['status'] == 'start':
                        return
                    else:
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': "nazan"}])
                else:
                    inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}])
                inline_keyboard.append([{'text': '🔄 Update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE gtg_id={row_gtg['id']} AND status='send'")
                count_done = cs.fetchone()['count']
                if row_gtg['group_link'] is not None:
                    output = f"🆔 <code>{row_gtg['group_id']}</code>\n"
                    output += f"🔗 {row_gtg['group_link']}\n\n"
                else:
                    output = ""
                last_bot_check = f"🟠 Account under review: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] is not None and row_gtg['status'] != "end" else ""
                if row_gtg['cats'] is None:
                    cats = "Not supported"
                else:
                    where = ""
                    cats = row_gtg['cats'].split(",")
                    for category in cats:
                        where += f"id={int(category)} OR "
                    where = where[0:-4]
                    cats = ""
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE {where}")
                    result = cs.fetchall()
                    for row in result:
                        cats += f"{row['name']},"
                    cats = cats[0:-1]
                count_send_per_account = row_gtg['add_per_h'] if row_gtg['add_per_h'] > 0 else "Not supported"
                message.reply_html(
                    text=f"{output}"+
                        f"👤 Send / Requested: [{count_done:,} / {row_gtg['count']:,}]\n"+
                        f"👤 Checking / Max: [{row_gtg['count_request']:,} / {row_gtg['max_users']:,}]\n\n"+
                        f"{last_bot_check}"+
                        f"🔵 Total accounts: {row_gtg['count_acc']}\n"+
                        f"🔵 Spam accounts: {row_gtg['count_spam']}\n"+
                        f"🔵 Restricted accounts: {row_gtg['count_restrict']}\n"+
                        f"🔵 Reported accounts: {row_gtg['count_report']}\n"+
                        f"🔵 Lost accounts: {row_gtg['count_accout']}\n\n"+
                        f"🔴 Get spam errors: {row_gtg['count_usrspam']}\n"+
                        f"🔴 Incorrect username errors: {row_gtg['count_userincorrect']}\n"+
                        f"🔴 Restricted accounts: {row_gtg['count_restrict_error']}\n"+
                        f"🔴 Other errors: {row_gtg['count_other_errors']}\n\n"+
                        f"🟣 Categories: {cats}\n"+
                        f"🟣 Count send per account: {count_send_per_account}\n\n"+
                        f"⚪️ Remaining send output: /exo_{row_gtg['id']}_r\n"+
                        f"⚪️ Successful send output: /exo_{row_gtg['id']}_m\n"+
                        "➖➖➖➖➖➖\n"+
                        f"📅️ Created: {created_at}\n"+
                        f"📅️ Updated: {updated_at}\n"+
                        f"📅 ️Now: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}",
                    disable_web_page_preview=True,
                    reply_markup={'inline_keyboard': inline_keyboard}
                )
            return
    if is_admin:
        if ex_step[0] == 'set_cache':
            if not message.forward_from_chat:
                message.reply_html(text="❌ Forward a post from the cache channel")
            elif not message.forward_from_chat.username:
                message.reply_html(text="❌ Channel cache must be public")
            elif bot.get_chat_member(chat_id=message.forward_from_chat.id, user_id=utl.bot_id).status == "left":
                message.reply_html(
                    text="❌ Make sure the robot is in the admin channel",
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
            else:
                cs.execute(f"UPDATE {utl.admini} SET cache='{message.forward_from_chat.username}'")
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
                message.reply_html(text="✅ Cache channel registered successfully")
                user_panel(update)
            return
        elif row_admin['cache'] is None or text == '/cache':
            cs.execute(f"UPDATE {utl.users} SET step='set_cache;none' WHERE user_id='{from_id}'")
            message.reply_html(
                text="Send a post from the cache channel:",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
            return
        elif text == '/start' or text == '/panel' or text == utl.menu_var:
            user_panel(update)
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
            cs.execute(f"DELETE FROM {utl.gtg} WHERE user_id='{from_id}' AND status='start'")
            return
        elif ex_step[0] == 'sendmsg':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_step[1]}'")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                message.reply_html(text=f"❌ Not found")
            else:
                try:
                    if update.message.text:
                        bot.send_message(chat_id=row_user_select['user_id'],disable_web_page_preview=True,parse_mode='HTML',
                        text=f"📧️ New message from support\n——————————————————\n{txtcap}"
                    )
                    elif update.message.photo:
                        bot.send_photo(chat_id=row_user_select['user_id'],parse_mode='HTML',
                            photo=update.message.photo[len(update.message.photo) - 1].file_id,
                            caption=f"📧️ New message from support\n——————————————————\n{txtcap}"
                        )
                    elif update.message.video:
                        bot.send_video(chat_id=row_user_select['user_id'],parse_mode='HTML',
                            video=update.message.video.file_id,
                            caption=f"📧️ New message from support\n——————————————————\n{txtcap}"
                        )
                    elif update.message.audio:
                        bot.send_audio(chat_id=row_user_select['user_id'],parse_mode='HTML',
                            audio=update.message.audio.file_id,
                            caption=f"📧️ New message from support\n——————————————————\n{txtcap}"
                        )
                    elif update.message.voice:
                        bot.send_voice(chat_id=row_user_select['user_id'],parse_mode='HTML',
                            voice=update.message.voice.file_id,
                            caption=f"📧️ New message from support\n——————————————————\n{txtcap}"
                        )
                    elif update.message.document:
                        bot.send_document(chat_id=row_user_select['user_id'],parse_mode='HTML',
                            document=update.message.document.file_id,
                            caption=f"📧️ New message from support\n——————————————————\n{txtcap}"
                        )
                    else:
                        return message.reply_html(text="⛔️ Message not supported")
                    cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
                    message.reply_html(text="✅ Message sent successfully")
                except:
                    return message.reply_html(text="❌ There was a problem sending the message")
            return
        elif ex_step[0] == 'add_acc':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_step[2]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Unknown error")
            elif ex_step[1] == 'phone':
                phone = text.replace("+","").replace(" ","")
                if not re.findall('^[0-9]*$', phone):
                    message.reply_html(text="❌ Wrong phone number")
                else:
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}' AND id NOT IN ('{row_mbots['id']}')")
                    row_mbots_select = cs.fetchone()
                    if row_mbots_select is not None:
                        if row_mbots_select['status'] == 'first_level':
                            cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots_select['id']}")
                        else:
                            return message.reply_html(text="❌ Previously registered phone number")
                    info_msg = message.reply_html(text="Pending ...")
                    cs.execute(f"UPDATE {utl.mbots} SET creator_user_id='{from_id}',phone='{phone}' WHERE id={row_mbots['id']}")
                    os.system(f"python \"{directory}/tl.account.py\" {from_id} first_level {row_mbots['id']}")
                    info_msg.delete()
                return
            elif ex_step[1] == 'code':
                try:
                    ex_nl_text = text.split("\n")
                    if len(ex_nl_text) == 1:
                        cs.execute(f"UPDATE {utl.mbots} SET code='{int(text)}' WHERE id={row_mbots['id']}")
                    elif len(ex_nl_text) == 2:
                        if len(ex_nl_text[0]) > 200 or len(ex_nl_text[1]) > 200:
                            return message.reply_html(text="❌ Incorrect input")
                        cs.execute(f"UPDATE {utl.mbots} SET code='{int(ex_nl_text[0])}',password='{ex_nl_text[1]}' WHERE id={row_mbots['id']}")
                    info_msg = message.reply_html(text="Pending ...")
                    os.system(f"python \"{directory}/tl.account.py\" {from_id} code {row_mbots['id']}")
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
                    row_mbots = cs.fetchone()
                    if row_mbots['status'] == 'submitted':
                        cs.execute(f"UPDATE {utl.users} SET step='set_cat;{row_mbots['id']}' WHERE user_id='{from_id}'")
                        keyboard = []
                        cs.execute(f"SELECT * FROM {utl.cats}")
                        result = cs.fetchall()
                        for row in result:
                            keyboard.append([{'text': row['name']}])
                        keyboard.append([{'text': utl.menu_var}])
                        message.reply_html(
                            text="Choose one of the categories:",
                            reply_markup={'resize_keyboard': True,'keyboard': keyboard}
                        )
                    info_msg.delete()
                except:
                    message.reply_html(text="❌ Incorrect input")
                return
            return
        elif ex_step[0] == 'create_order':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{ex_step[2]}'")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ Not found")
            elif ex_step[1] == 'category':
                if text == '⏩ skip':
                    if row_gtg['cats'] is None:
                        return message.reply_html(text="❌ You must select a category")
                    cs.execute(f"UPDATE {utl.users} SET step='create_order;type;{row_gtg['id']}' WHERE user_id='{from_id}'")
                    message.reply_html(
                        text="Select the order type:",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': '🔴 With Group Link 🔴'}],
                            [{'text': '🔵 With List Members 🔵'}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
                else:
                    cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
                    row_cats = cs.fetchone()
                    if row_cats is None:
                        message.reply_html(text="❌ Not found")
                    else:
                        cats = ""
                        if row_gtg['cats'] is not None:
                            cats = row_gtg['cats'].split(",")
                            for category in cats:
                                try:
                                    if int(category) == row_cats['id']:
                                        return message.reply_html(text="❌ Already selected")
                                except:
                                    pass
                            cats = f"{row_gtg['cats']},{row_cats['id']}"
                        else:
                            cats = row_cats['id']
                        row_gtg['cats'] = str(cats)
                        limit_per_h = row_admin['limit_per_h'] * 3600
                        where = ""
                        cats = row_gtg['cats'].split(",")
                        for category in cats:
                            where += f"cat_id={int(category)} OR "
                        where = where[0:-4]
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND ({where}) AND (last_order_at+{limit_per_h})<{timestamp} LIMIT 1")
                        if cs.fetchone() is None:
                            message.reply_html(text="❌ There is no account with sending ability in this category")
                        else:
                            cs.execute(f"UPDATE {utl.gtg} SET cats='{row_gtg['cats']}' WHERE id={row_gtg['id']}")
                            keyboard = [[{'text': utl.menu_var}, {'text': '⏩ skip'}]]
                            cs.execute(f"SELECT * FROM {utl.cats}")
                            result = cs.fetchall()
                            for row in result:
                                keyboard.append([{'text': row['name']}])
                            message.reply_html(
                                text="✅ Selected\n\n"+
                                    "Choose another item or go to the next step:",
                                reply_markup={'resize_keyboard': True,'keyboard': keyboard}
                            )
                return
            elif ex_step[1] == 'type':
                if text == '🔴 With Group Link 🔴':
                    limit_per_h = row_admin['limit_per_h'] * 3600
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp} ORDER BY last_order_at ASC")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        message.reply_html(text="❌ No accounts found")
                    else:
                        cs.execute(f"UPDATE {utl.users} SET step='create_order;type_send;{row_gtg['id']}' WHERE user_id='{from_id}'")
                        message.reply_html(
                            text="Select the send type:",
                            reply_markup={'resize_keyboard': True,'keyboard': [
                                [{'text': 'All members'}],
                                [{'text': 'Unique members'}],
                                [{'text': utl.menu_var}]
                            ]}
                        )
                    return
                elif text == '🔵 With List Members 🔵':
                    limit_per_h = row_admin['limit_per_h'] * 3600
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        message.reply_html(text="❌ No accounts found")
                    else:
                        cs.execute(f"UPDATE {utl.users} SET step='create_order_file;info;{row_gtg['id']}' WHERE user_id='{from_id}'")
                        bot.send_document(
                            chat_id=from_id,
                            document=open(f"{directory}/files/list-members.txt", "rb"),
                            caption="Send a list of members in the sample file format:",
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(utl.menu_var)]])
                        )
                    return
                else:
                    message.reply_html(text="⛔️ Select from the menu")
            elif ex_step[1] == 'type_send':
                if text == 'All members':
                    type_send = 'all'
                elif text == 'Unique members':
                    type_send = 'unique'
                else:
                    return message.reply_html(text="⛔️ Select from the menu")
                cs.execute(f"UPDATE {utl.gtg} SET type_send='{type_send}' WHERE id={row_gtg['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='create_order;info;{row_gtg['id']}' WHERE user_id='{from_id}'")
                message.reply_html(
                    text="Send information as sample format:\n\n"+
                        "Group link\n"+
                        "Number send\n\n"+
                        "example:\n" +
                        "https://t.me/source\n" +
                        "100",
                    disable_web_page_preview=True,
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
                return
            elif ex_step[1] == 'info':
                try:
                    ex_nl_text = text.split("\n")
                    group_link = ex_nl_text[0].replace("/+","/joinchat/")
                    count = int(ex_nl_text[1])
                    ex_nl_text = text.split("\n")
                    if len(group_link) > 200 or len(ex_nl_text) != 2:
                        message.reply_html(text="❌ Invalid values")
                    elif group_link[0:13] != "https://t.me/":
                        message.reply_html(text="❌ Invalid group")
                    else:
                        cs.execute(f"UPDATE {utl.gtg} SET group_link='{group_link}',count='{count}' WHERE id={row_gtg['id']}")
                        cs.execute(f"UPDATE {utl.users} SET step='create_order;get_message;{row_gtg['id']}' WHERE user_id='{from_id}'")
                        message.reply_html(text="Send the message:")
                except:
                    message.reply_html(text="❌ Unknown error")
            elif ex_step[1] == "get_message":
                if text != "✅ end ✅":
                    try:
                        uniq_id = utl.uniq_id_generate(cs,15,utl.files)
                        if message.text:
                            info_msg = bot.send_message(
                                chat_id=f"@{row_admin['cache']}",
                                disable_web_page_preview=True,
                                parse_mode='HTML',
                                text=txtcap
                            )
                            cs.execute(f"INSERT INTO {utl.files} (gtg_id,type_message,message_id,created_at,uniq_id) VALUES ('{row_gtg['id']}','message','{info_msg.message_id}','{timestamp}','{uniq_id}')")
                        elif message.photo:
                            info_msg = bot.send_photo(
                                chat_id=f"@{row_admin['cache']}",
                                parse_mode='HTML',
                                photo=message.photo[len(message.photo) - 1].file_id,
                                caption=txtcap
                            )
                            type_message = "photo"
                        elif message.video:
                            info_msg = bot.send_video(
                                chat_id=f"@{row_admin['cache']}",
                                parse_mode='HTML',
                                video=message.video.file_id,
                                caption=txtcap
                            )
                            type_message = "video"
                        elif message.audio:
                            info_msg = bot.send_audio(
                                chat_id=f"@{row_admin['cache']}",
                                parse_mode='HTML',
                                audio=message.audio.file_id,
                                caption=txtcap
                            )
                            type_message = "audio"
                        elif message.voice:
                            info_msg = bot.send_voice(
                                chat_id=f"@{row_admin['cache']}",
                                parse_mode='HTML',
                                voice=message.voice.file_id,
                                caption=txtcap
                            )
                            type_message = "voice"
                        elif message.document:
                            info_msg = bot.send_document(
                                chat_id=f"@{row_admin['cache']}",
                                parse_mode='HTML',
                                document=message.document.file_id,
                                caption=txtcap
                            )
                            type_message = "document"
                        else:
                            return message.reply_html(text="⛔️ Message not supported")
                        if not message.text:
                            cs.execute(f"INSERT INTO {utl.files} (gtg_id,type_message,message_id,created_at,uniq_id) VALUES ('{row_gtg['id']}','{type_message}','{info_msg.message_id}','{timestamp}','{uniq_id}')")
                        cs.execute(f"SELECT * FROM {utl.files} WHERE uniq_id='{uniq_id}'")
                        row_files = cs.fetchone()
                        if row_files is None:
                            return message.reply_html(text="❌ There is a problem, try again")
                    except:
                        return message.reply_html(text="❌ There was a problem sending the message to the channel cache")
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.files} WHERE gtg_id='{row_gtg['id']}'")
                count = cs.fetchone()['count']
                if count < 3 and text != "✅ end ✅":
                    message.reply_html(
                        text=f"Send message {count + 1}:\n\n" +
                            "❕ Up to 3 messages",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': "✅ end ✅"}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
                else:
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                    info_msg = message.reply_html(
                        text="Pending ...",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
                    os.system(f"python \"{directory}/tl.analyze.py\" {from_id} check {row_gtg['id']}")
                return
            elif ex_step[1] == 'type_users':
                info_msg = message.reply_html(text="Configuring...")
                if text == 'All users':
                    type_users = 'users_all'
                elif text == 'Real users':
                    type_users = 'users_real'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_real=0")
                elif text == 'Fake users':
                    type_users = 'users_fake'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_fake=0")
                elif text == 'Online users':
                    type_users = 'users_online'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_online=0")
                elif text == 'Users with phone':
                    type_users = 'users_has_phone'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_phone=0")
                else:
                    return message.reply_html(text="❌ Just select from the menu")
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze}")
                max_users = cs.fetchone()['count']
                cs.execute(f"UPDATE {utl.gtg} SET status='doing',max_users='{max_users}',type_users='{type_users}',add_per_h='{row_admin['add_per_h']}',created_at='{timestamp}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                user_panel(update,
                    text=f"✅ Order successfully registered\n\n"+
                        f"♻️ /gtg_{row_gtg['id']}"
                )
                info_msg.delete()
                return
        elif ex_step[0] == 'create_order_file':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{ex_step[2]}'")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ Not found")
            elif ex_step[1] == 'info':
                if not message.document:
                    message.reply_html(text="❌ Please send a txt file")
                else:
                    info_msg = message.reply_html(text="Checking the file ...")
                    try:
                        list_members = []
                        path = f"files/id-{row_gtg['id']}.txt"
                        info_action = bot.get_file(message.document.file_id)
                        with open(path, "wb") as file:
                            file.write(requests.get(info_action.file_path).content)
                        with open(path, "rb") as file:
                            result = file.read().splitlines()
                            for value in result:
                                value = value.decode('utf8')
                                if value == "" or len(value) < 5:
                                    continue
                                elif value[0:1] != "@":
                                    value = f"@{value}"
                                if not value in list_members:
                                    list_members.append(value)
                        cs.execute(f"DELETE FROM {utl.analyze}")
                        for value in list_members:
                            cs.execute(f"INSERT INTO {utl.analyze} (gtg_id,username,is_real,created_at) VALUES ('{row_gtg['id']}','{value}','1','{timestamp}')")
                        if row_gtg['type_send'] == 'unique':
                            i = 0
                            timestamp_start = timestamp = int(time.time())
                            cs.execute(f"SELECT {utl.analyze}.id as id,{utl.analyze}.username as username FROM {utl.analyze} INNER JOIN {utl.reports} ON {utl.analyze}.username={utl.reports}.username GROUP BY {utl.reports}.username")
                            count = cs.rowcount
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

                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze}")
                        max_users = cs.fetchone()['count']
                        cs.execute(f"UPDATE {utl.gtg} SET max_users='{max_users}',count='{max_users}',type_users='users_all' WHERE id={row_gtg['id']}")
                        cs.execute(f"UPDATE {utl.users} SET step='create_order_file;get_message;{row_gtg['id']}' WHERE user_id='{from_id}'")
                        message.reply_html(text="Send the message:")
                    except:
                        message.reply_html(text="❌ There was a problem analyzing the file")
                    info_msg.delete()
            elif ex_step[1] == "get_message":
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{ex_step[2]}'")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    message.reply_html(text="❌ Not found")
                else:
                    if text != "✅ end ✅":
                        try:
                            uniq_id = utl.uniq_id_generate(cs,15,utl.files)
                            if message.text:
                                info_msg = bot.send_message(chat_id=f"@{row_admin['cache']}",disable_web_page_preview=True,parse_mode='HTML',
                                    text=txtcap
                                )
                                cs.execute(f"INSERT INTO {utl.files} (gtg_id,type_message,message_id,created_at,uniq_id) VALUES ('{row_gtg['id']}','message','{info_msg.message_id}','{timestamp}','{uniq_id}')")
                            elif message.photo:
                                info_msg = bot.send_photo(chat_id=f"@{row_admin['cache']}",parse_mode='HTML',
                                    photo=message.photo[len(message.photo) - 1].file_id,
                                    caption=txtcap
                                )
                                type_message = "photo"
                            elif message.video:
                                info_msg = bot.send_video(chat_id=f"@{row_admin['cache']}",parse_mode='HTML',
                                    video=message.video.file_id,
                                    caption=txtcap
                                )
                                type_message = "video"
                            elif message.audio:
                                info_msg = bot.send_audio(chat_id=f"@{row_admin['cache']}",parse_mode='HTML',
                                    audio=message.audio.file_id,
                                    caption=txtcap
                                )
                                type_message = "audio"
                            elif message.voice:
                                info_msg = bot.send_voice(chat_id=f"@{row_admin['cache']}",parse_mode='HTML',
                                    voice=message.voice.file_id,
                                    caption=txtcap
                                )
                                type_message = "voice"
                            elif message.document:
                                info_msg = bot.send_document(chat_id=f"@{row_admin['cache']}",parse_mode='HTML',
                                    document=message.document.file_id,
                                    caption=txtcap
                                )
                                type_message = "document"
                            else:
                                return message.reply_html(text="⛔️ Message not supported")
                            if not message.text:
                                cs.execute(f"INSERT INTO {utl.files} (gtg_id,type_message,message_id,created_at,uniq_id) VALUES ('{row_gtg['id']}','{type_message}','{info_msg.message_id}','{timestamp}','{uniq_id}')")
                            cs.execute(f"SELECT * FROM {utl.files} WHERE uniq_id='{uniq_id}'")
                            row_files = cs.fetchone()
                            if row_files is None:
                                return message.reply_html(text="❌ There is a problem, try again")
                        except:
                            return message.reply_html(text="❌ There was a problem sending the message to the channel cache")
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.files} WHERE gtg_id='{row_gtg['id']}'")
                    count = cs.fetchone()['count']
                    if count < 3 and text != "✅ end ✅":
                        message.reply_html(
                            text=f"Send message {count + 1}:\n\n" +
                                "❕ Up to 3 messages",
                            reply_markup={'resize_keyboard': True,'keyboard': [
                                [{'text': "✅ end ✅"}],
                                [{'text': utl.menu_var}]
                            ]}
                        )
                    else:
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze}")
                        max_users = cs.fetchone()['count']
                        cs.execute(f"UPDATE {utl.gtg} SET status='doing',add_per_h='{row_admin['add_per_h']}',created_at='{timestamp}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                        user_panel(update,
                            text=f"✅ Order successfully registered\n\n"+
                                f"♻️ /gtg_{row_gtg['id']}"
                        )
                return
        elif ex_step[0] == 'analyze':
            if ex_step[1] == 'type':
                if text == 'Users':
                    cs.execute(f"UPDATE {utl.users} SET step='analyze;users' WHERE user_id='{from_id}'")
                    return message.reply_html(
                        text="Send group link:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
                elif text == 'Messages':
                    cs.execute(f"UPDATE {utl.users} SET step='analyze;messages' WHERE user_id='{from_id}'")
                    return message.reply_html(
                        text="Send group link:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
            elif ex_step[1] == 'users':
                uniq_id = utl.uniq_id_generate(cs,10,utl.egroup)
                text = text.replace("/+","/joinchat/")
                cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,link,status,created_at,updated_at,uniq_id) VALUES (0,{from_id},'{text}','start','{timestamp}','{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.egroup} WHERE uniq_id='{uniq_id}'")
                row_egroup = cs.fetchone()
                if not row_egroup:
                    message.reply_html(text="❌ Unknown error, try again")
                else:
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                    info_msg = message.reply_html(text="Pending ...")
                    os.system(f"python \"{directory}/tl.analyze.py\" {from_id} analyze {row_egroup['id']}")
                    user_panel(update)
                    info_msg.delete()
            elif ex_step[1] == 'messages':
                uniq_id = utl.uniq_id_generate(cs,10,utl.egroup)
                text = text.replace("/+","/joinchat/")
                cs.execute(f"INSERT INTO {utl.egroup} (type,user_id,link,status,created_at,updated_at,uniq_id) VALUES (1,{from_id},'{text}','start','{timestamp}','{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.egroup} WHERE uniq_id='{uniq_id}'")
                row_egroup = cs.fetchone()
                if not row_egroup:
                    message.reply_html(text="❌ Unknown error, try again")
                else:
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                    info_msg = message.reply_html(text="Pending ...")
                    os.system(f"python \"{directory}/tl_analyze_messages.py\" {from_id} {row_egroup['id']}")
                    user_panel(update)
                    info_msg.delete()
            return
        elif ex_step[0] == 'add_api':
            try:
                ex_nl_text = text.split("\n")
                if len(ex_nl_text[0]) > 200 or len(ex_nl_text[1]) > 200 or len(ex_nl_text) != 2:
                    message.reply_html(text="❌ Incorrect input")
                else:
                    api_id = ex_nl_text[0]
                    api_hash = ex_nl_text[1]
                    cs.execute(f"SELECT * FROM {utl.apis} WHERE api_id='{api_id}' OR api_hash='{api_hash}'")
                    row_apis = cs.fetchone()
                    if row_apis is not None:
                        message.reply_html(text="❌ This api is already registered")
                    else:
                        cs.execute(f"INSERT INTO {utl.apis} (api_id,api_hash) VALUES ('{api_id}','{api_hash}')")
                        cs.execute(f"UPDATE {utl.users} SET step='add_api;' WHERE user_id='{from_id}'")
                        message.reply_html(
                            text="✅ Successfully added\n\n"+
                                "Send another api:",
                            reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                        )
            except:
                message.reply_html(text="❌ Send according to the sample")
            return
        elif ex_step[0] == 'create_cat':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
            row_cats = cs.fetchone()
            if row_cats is not None:
                message.reply_html(text="❌ Categories have already been added")
            if not re.findall('^[A-Za-z]*$', text):
                message.reply_html(text="❌ Use only English letters")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                cs.execute(f"INSERT INTO {utl.cats} (name) VALUES ('{text}')")
                message.reply_html(
                    text="✅ Successfully added",
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
                user_panel(update)
            return 
        elif ex_step[0] == 'set_cat':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_step[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Category not found")
            else:
                cs.execute(f"SELECT * FROM {utl.cats} WHERE name='{text}'")
                row_cats = cs.fetchone()
                if row_cats is None:
                    message.reply_html(text="❌ Not found")
                else:
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                    cs.execute(f"UPDATE {utl.mbots} SET cat_id={row_cats['id']} WHERE id={row_mbots['id']}")
                    message.reply_html(
                        text="✅ Successfully updated",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
            return
        elif text == '➕ Create Order':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
            row_gtg = cs.fetchone()
            if row_gtg is not None:
                message.reply_html(text="❌ There is an active order")
            else:
                uniq_id = utl.uniq_id_generate(cs, 10, utl.gtg)
                cs.execute(f"INSERT INTO {utl.gtg} (user_id,status,status_analyze,created_at,updated_at,uniq_id) VALUES ('{from_id}','start','run','{timestamp}','{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE uniq_id='{uniq_id}'")
                row_gtg = cs.fetchone()
                if row_gtg is not None:
                    cs.execute(f"UPDATE {utl.users} SET step='create_order;category;{row_gtg['id']}' WHERE user_id='{from_id}'")
                    keyboard = [[{'text': utl.menu_var}, {'text': '⏩ skip'}]]
                    cs.execute(f"SELECT * FROM {utl.cats}")
                    result = cs.fetchall()
                    for row in result:
                        keyboard.append([{'text': row['name']}])
                    message.reply_html(
                        text="Select a category:",
                        reply_markup={'resize_keyboard': True,'keyboard': keyboard}
                    )
            return
        if text == '📋 list':
            keyboard = [
                [{'text': '📋 Orders'}],
                [{'text': '📋 Apis'}, {'text': '📋 Categories'}],
                [{'text': '🏛 Main Menu'}]]
            cs.execute(f"SELECT * FROM {utl.cats}")
            result = cs.fetchall()
            message.reply_html(
            text="Select a category:",
            reply_markup={'resize_keyboard': True,'keyboard': keyboard}
                    )
            return
        elif text == '📋 Orders':
            cs.execute(f"SELECT * FROM {utl.gtg} ORDER BY id DESC LIMIT 0,{step_page}")
            result = cs.fetchall()
            if not result:
                message.reply_html(text="❌ The list is empty")
            else:
                output = ""
                i = 1
                for row in result:
                    created_at = jdatetime.datetime.fromtimestamp(row['created_at'])
                    count_done = cs.execute(f"SELECT id FROM {utl.reports} WHERE gtg_id={row['id']} AND status='send'")
                    output += f"{i}. /gtg_{row['id']}\n"
                    output += f"🔹️ group: {row['group_link']}\n"
                    output += f"🔹️ done: [{count_done} / {row['count']}]\n"
                    output += f"🔹️ status: {utl.status_gtg[row['status']]}\n"
                    output += f"📅️ created: {created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                    i += 1
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg}")
                count = cs.fetchone()['count']
                output = f"📋 Orders ({count})\n\n{output}"
                ob = Pagination(update, "orders", output, step_page, count)
                ob.processMessage()
            return
        elif text == '➕ Add Account':
            cs.execute(f"DELETE FROM {utl.mbots} WHERE creator_user_id='{from_id}' AND status='first_level' AND user_id IS NULL")
            row_apis = utl.select_api(cs,row_admin['api_per_number'])
            if row_apis is None:
                message.reply_html(text="❌ No api found")
            else:
                uniq_id = utl.uniq_id_generate(cs,10,utl.mbots)
                cs.execute(f"INSERT INTO {utl.mbots} (cat_id,creator_user_id,api_id,api_hash,status,created_at,uniq_id) VALUES (1,'{from_id}','{row_apis['api_id']}','{row_apis['api_hash']}','first_level','{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{uniq_id}'")
                row_mbots = cs.fetchone()
                if row_mbots is not None:
                    cs.execute(f"UPDATE {utl.users} SET step='add_acc;phone;{row_mbots['id']}' WHERE user_id='{from_id}'")
                    message.reply_html(
                        text="Enter the phone number:",
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
            return
        elif text == '📋 Accounts':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL LIMIT 1")
            row_mbots = cs.fetchone()
            if not row_mbots:
                message.reply_html(text="❌ The list is empty")
            else:
                limit_per_h = row_admin['limit_per_h'] * 3600
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
                accs_all = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted'")
                accs_active = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
                accs_ability_ad = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='restrict'")
                accs_restrict = cs.fetchone()['count']
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='first_level' AND user_id IS NOT NULL")
                accs_first_level = cs.fetchone()['count']
                message.reply_html(
                    text="📋 Accounts:\n\n" +
                        "Delete all unregistered accounts: /DelUnregistered",
                    reply_markup={'inline_keyboard': [
                        [{'text': f"💢 All ({accs_all}) 💢", 'callback_data': f"pg;accounts;1"}],
                        [
                            {'text': f"⛔️ Not Registered ({accs_first_level})", 'callback_data': f"pg;first_level;1"},
                            {'text': f"❌ Limited ({accs_restrict})", 'callback_data': f"pg;restrict;1"}
                        ],
                        [
                            {'text': f"♻️ Ability Send ({accs_ability_ad})", 'callback_data': f"pg;adability;1"},
                            {'text': f"✅ Active ({accs_active})", 'callback_data': f"pg;submitted;1"}
                        ]
                    ]}
                )
            return
        elif text == '➕ Add Api':
            cs.execute(f"UPDATE {utl.users} SET step='add_api;' WHERE user_id='{from_id}'")
            message.reply_html(
                text="Sent api information:\n\n"+
                "example:\n"+
                "api id\n"+
                "api hash",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
            return
        elif text == '📋 Apis':
            cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT 0,{step_page}")
            result = cs.fetchall()
            if not result:
                message.reply_html(text="❌ The list is empty")
            else:
                output = ""
                for row in result:
                    output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                    output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                    output += f"❌ Delete: /DeleteApi_{row['id']}\n\n"
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                count = cs.fetchone()['count']
                output = f"📋 Apis ({count})\n\n{output}"
                ob = Pagination(update, "apis", output, step_page, count)
                ob.processMessage()
            return
        elif text == '➕ Create Category':
            cs.execute(f"UPDATE {utl.users} SET step='create_cat;none' WHERE user_id='{from_id}'")
            message.reply_html(
                text="Enter the category name:",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
            return
        elif text == '📋 Categories':
            cs.execute(f"SELECT * FROM {utl.cats} ORDER BY id DESC LIMIT 0,{step_page}")
            result = cs.fetchall()
            if not result:
                message.reply_html(text="❌ The list is empty")
            else:
                output = ""
                i = 1
                for row in result:
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row['id']}")
                    count_mbots = cs.fetchone()['count']
                    output += f"{i}. Name: {row['name']} ({count_mbots})\n"
                    output += f"❌ Delete: /DeleteCat_{row['id']}\n\n"
                    i += 1
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.cats}")
                count = cs.fetchone()['count']
                output = f"📋 Categories ({count})\n\n{output}"
                ob = Pagination(update, "categories", output, step_page, count)
                ob.processMessage()
            return
        elif text == '🔮 Analysis':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ No accounts found")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='analyze;type' WHERE user_id='{from_id}'")
                message.reply_html(
                    text="Select the type of analysis:",
                    reply_markup={'resize_keyboard': True,'keyboard': [
                        [{'text': 'Users'}, {'text': 'Messages'}],
                        [{'text': utl.menu_var}],
                    ]}
                )
            return
        elif text == "⚙️ Settings":
            api_per_number = f"Register {row_admin['api_per_number']} accounts in each api" if row_admin['api_per_number'] <= 5 else f"⚠️ Register {row_admin['api_per_number']} accounts in each api ⚠️"
            add_per_h = f"Each account will send {row_admin['add_per_h']} in each use" if row_admin['add_per_h'] <= 16 else f"⚠️ Each account will send {row_admin['add_per_h']} in each use ⚠️"
            limit_per_h = f"Use each account every {row_admin['limit_per_h']} hours" if row_admin['limit_per_h'] >= 24 else f"⚠️ Use each account every {row_admin['limit_per_h']} hours ⚠️"
            time_spam_restrict = int(row_admin['time_spam_restrict'] / 86400)
            change_pass = "✅ Change / Set two step password ✅" if row_admin['change_pass'] else "❌ Change / Set two step password ❌"
            exit_session = "✅ Exit the rest of the sessions ✅" if row_admin['exit_session'] else "❌ Exit the rest of the sessions ❌"
            is_change_profile = "✅ Set name, bio and profile ✅" if row_admin['is_change_profile'] else "❌ Set name, bio and profile ❌"
            is_set_username = "✅ Set username ✅" if row_admin['is_set_username'] else "❌ Set username ❌"
            gtg_per = "✅ All access to the order ID ✅" if row_admin['gtg_per'] else "❌ All access to the order ID ❌"
            
            message.reply_html(
                text=f"Settings:",
                reply_markup={'inline_keyboard': [
                    [{'text': api_per_number,'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;api_per_number;+10"},
                        {'text': '+5','callback_data': "settings;api_per_number;+5"},
                        {'text': '+1','callback_data': "settings;api_per_number;+1"},
                        {'text': '-1','callback_data': "settings;api_per_number;-1"},
                        {'text': '-5','callback_data': "settings;api_per_number;-5"},
                        {'text': '-10','callback_data': "settings;api_per_number;-10"},
                    ],
                    [{'text': add_per_h,'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;add_per_h;+10"},
                        {'text': '+5','callback_data': "settings;add_per_h;+5"},
                        {'text': '+1','callback_data': "settings;add_per_h;+1"},
                        {'text': '-1','callback_data': "settings;add_per_h;-1"},
                        {'text': '-5','callback_data': "settings;add_per_h;-5"},
                        {'text': '-10','callback_data': "settings;add_per_h;-10"},
                    ],
                    [{'text': limit_per_h,'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;limit_per_h;+10"},
                        {'text': '+5','callback_data': "settings;limit_per_h;+5"},
                        {'text': '+1','callback_data': "settings;limit_per_h;+1"},
                        {'text': '-1','callback_data': "settings;limit_per_h;-1"},
                        {'text': '-5','callback_data': "settings;limit_per_h;-5"},
                        {'text': '-10','callback_data': "settings;limit_per_h;-10"},
                    ],
                    [{'text': f"Account should rest for {time_spam_restrict} day when receiving spam",'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;time_spam_restrict;+10"},
                        {'text': '+5','callback_data': "settings;time_spam_restrict;+5"},
                        {'text': '+1','callback_data': "settings;time_spam_restrict;+1"},
                        {'text': '-1','callback_data': "settings;time_spam_restrict;-1"},
                        {'text': '-5','callback_data': "settings;time_spam_restrict;-5"},
                        {'text': '-10','callback_data': "settings;time_spam_restrict;-10"},
                    ],
                    [{'text': change_pass,'callback_data': "settings;change_pass"}],
                    [{'text': exit_session,'callback_data': "settings;exit_session"}],
                    [{'text': is_change_profile,'callback_data': "settings;is_change_profile"}],
                    [{'text': is_set_username,'callback_data': "settings;is_set_username"}],
                    [{'text': gtg_per,'callback_data': "settings;gtg_per"}],
                ]}
            )
            return
        elif text == '📊 Stats':
            now = jdatetime.datetime.now()
            time_today = jdatetime.datetime(day = now.day,month = now.month,year = now.year).timestamp()
            time_yesterday = time_today - 86400
            limit_per_h = row_admin['limit_per_h'] * 3600
            
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg}")
            orders_count_all = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg} WHERE created_at>={time_today}")
            orders_count_today = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg} WHERE created_at<{time_today} AND created_at>={time_yesterday}")
            orders_count_yesterday = cs.fetchone()['count']

            cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE status='send'")
            orders_count_moved_all = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE created_at>={time_today} AND status='send'")
            orders_count_moved_today = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.reports} WHERE created_at<{time_today} AND created_at>={time_yesterday} AND status='send'")
            orders_count_moved_yesterday = cs.fetchone()['count']

            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
            accs_all = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted'")
            accs_active = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
            accs_ability_ad = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='restrict'")
            accs_restrict = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='first_level' AND user_id IS NOT NULL")
            accs_first_level = cs.fetchone()['count']

            cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
            apis_count_all = cs.fetchone()['count']
            message.reply_html(
                text="📊 Statistics:\n\n"+
                    "🛍 Orders:\n"+
                    f"🟢 Today: {orders_count_today} ({orders_count_moved_today:,})\n"+
                    f"⚪️ Yesterday: {orders_count_yesterday} ({orders_count_moved_yesterday:,})\n"+
                    f"🔴 All: {orders_count_all} ({orders_count_moved_all:,})\n\n"+
                    "🤖 Accounts:\n"+
                    f"💢️️ All: {accs_all}\n"+
                    f"✅️ Active: {accs_active}\n"+
                    f"♻️️ Ability Send: {accs_ability_ad}\n"+
                    f"⚠️ limited: {accs_restrict}\n"+
                    f"⛔️ Not registered: {accs_first_level}\n\n"+
                    f"🔘 Total api: {apis_count_all}"
            )
            return
        elif text == '📚 more':
            message.reply_html(
                text="📚 more\n\n"+
                    f"- User details: /d_{from_id}\n\n"+
                    "- Edit channel cache: /cache\n\n"+
                    "- Add an account via session: /import\n\n"+
                    "- Accounts leave groups: /LeaveGroups\n\n"+
                    "- Accounts delete chats: /DeleteChats\n"+
                    "➖➖➖➖➖➖",
            )
            return
        elif text == '📞 support':
            message.reply_html(
                text="📞 support\n\n"+
                    f"- آدرس سایت:https://addjou.shop\n\n"+
                    f"- آیدی کانال: @addjou\n\n"+
                    "- آیدی پشتیبان: @add_jou\n\n"+
                    "➖➖➖➖➖➖",
            )
            return
        elif text == '/import':
            info_msg = message.reply_html(text="Pending ...")
            os.system(f"python \"{directory}/tl.import.py\" {from_id}")
            user_panel(update, "✅ The session import operation is over")
            info_msg.delete()
            return
        elif text == '/DelUnregistered':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='first_level'")
            result = cs.fetchall()
            if result:
                for row in result:
                    try:
                        cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row['id']}")
                        os.remove(f"{directory}/sessions/{row['phone']}.session")
                    except:
                        pass
                message.reply_html(text=f"✅ Done successfully")
            else:
                message.reply_html(text=f"❌ No accounts found")
            return
        elif text == '/LeaveGroups':
            info_msg = message.reply_html(text=f"Pending ...")
            os.system(f"python \"{directory}/tl.leave.py\" {from_id} group")
            info_msg.delete()
            return
        elif text == '/DeleteChats':
            info_msg = message.reply_html(text=f"Pending ...")
            os.system(f"python \"{directory}/tl.leave.py\" {from_id} private")
            info_msg.delete()
            return
        elif ex_text[0] == '/category':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_text[1]}' or phone='{ex_text[1]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Not found")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='set_cat;{row_mbots['id']}' WHERE user_id='{from_id}'")
                keyboard = []
                cs.execute(f"SELECT * FROM {utl.cats}")
                result = cs.fetchall()
                for row in result:
                    keyboard.append([{'text': row['name']}])
                keyboard.append([{'text': utl.menu_var}])
                message.reply_html(
                    text="Choose one of the categories:",
                    reply_markup={'resize_keyboard': True,'keyboard': keyboard}
                )
            return
        elif ex_text[0] == '/DeleteCat':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={int(ex_text[1])}")
            row_cats = cs.fetchone()
            if row_cats is None:
                message.reply_html(text="❌ Not found")
            elif row_cats['id'] == 1:
                message.reply_html(text="❌ This category cannot be deleted")
            else:
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE cat_id={row_cats['id']}")
                count = cs.fetchone()['count']
                if count < 1:
                    cs.execute(f"DELETE FROM {utl.cats} WHERE id={row_cats['id']}")
                    message.reply_html(text="✅ Successfully deleted")
                else:
                    message.reply_html(
                        text=f"❌ Delete Category: {row_cats['name']}\n\n"+
                            f"/DeleteCatConfirm_{row_cats['id']}\n\n"+
                            f"⚠️ {count} accounts have been registered in this category",
                        reply_to_message_id=message_id
                    )
            return
        elif ex_text[0] == '/DeleteCatConfirm':
            cs.execute(f"SELECT * FROM {utl.cats} WHERE id={int(ex_text[1])}")
            row_cats = cs.fetchone()
            if row_cats is None:
                message.reply_html(text="❌ Not found")
            else:
                cs.execute(f"UPDATE {utl.mbots} SET cat_id=1 WHERE cat_id={row_cats['id']}")
                cs.execute(f"DELETE FROM {utl.cats} WHERE id={row_cats['id']}")
                message.reply_html(text="✅ Successfully deleted")
            return
        elif ex_text[0] == '/sessions':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_text[1]}' or phone='{ex_text[1]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Not found")
            else:
                info_msg = message.reply_html(text="Pending ...")
                os.system(f"python \"{directory}/tl.account-status.py\" {from_id} sessions {row_mbots['id']}")
                info_msg.delete()
            return
        elif ex_text[0] == '/status':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_text[1]}' OR phone='{ex_text[1]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Not found")
            else:
                info_msg = message.reply_html(text="Pending ...")
                os.system(f"python \"{directory}/tl.account-status.py\" {from_id} check {row_mbots['id']}")
                cs.execute(f"SELECT * FROM {utl.cats} WHERE id={row_mbots['cat_id']}")
                row_cats = cs.fetchone()
                message.reply_html(
                    f"📂 Category: /category_{row_mbots['id']} ({row_cats['name']})\n\n"+
                    f"❌ Delete Account: /delete_{row_mbots['id']}"
                )
                info_msg.delete()
            return
        elif ex_text[0] == '/delete':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_text[1]}' or phone='{ex_text[1]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Not found")
            else:
                message.reply_html(
                    reply_to_message_id=message_id,
                    text=f"❌ Delete Account: {row_mbots['phone']}\n\n"+
                    f"/deleteconfirm_{ex_text[1]}"
                )
            return
        elif ex_text[0] == '/deleteconfirm':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id='{ex_text[1]}' or phone='{ex_text[1]}'")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ Not found")
            else:
                cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                message.reply_html(text=f"✅ Successfully deleted")
            return
        elif ex_text[0] == '/DeleteApi':
            cs.execute(f"SELECT * FROM {utl.apis} WHERE id={int(ex_text[1])}")
            row_apis = cs.fetchone()
            if row_apis is None:
                message.reply_html(text="❌ Not found")
            else:
                cs.execute(f"DELETE FROM {utl.apis} WHERE id={row_apis['id']}")
                message.reply_html(text=f"✅ Successfully deleted")
            return
        elif ex_text[0] == '/exgroup':
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE chat_id='-{ex_text[1]}' AND status='end' ORDER BY id DESC")
            result = cs.fetchall()
            if not result or result is None:
                message.reply_html(text="❌ No analysis has been performed on this group")
            else:
                i = 1
                output = ""
                for row in result:
                    output += f"{i}. /ex_{row['id']}\n"
                    i += 1
                message.reply_html(
                    text=f"♨️ Analyzes performed from this group\n\n"+
                        f"{output}"
                )
            return
        elif ex_text[0] == '/ex':
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_text[1])}")
            row_egroup = cs.fetchone()
            if row_egroup is None:
                message.reply_html(text="❌ Not found")
            else:
                if row_egroup['type'] == 0:
                    try:
                        type = ex_text[2]
                        info_msg = message.reply_html(text="Sending ...")
                        try:
                            if type == 'a':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_all.txt","rb"),caption='Identified users')
                            elif type == 'u':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_real.txt","rb"),caption='Real users')
                            elif type == 'f':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_fake.txt","rb"),caption='Fake users')
                            elif type == 'n':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_has_phone.txt","rb"),caption='Users with phone')
                            elif type == 'o':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_online.txt","rb"),caption='Online users')
                        except:
                            message.reply_html(text="❌ There was a problem uploading the file")
                        info_msg.delete()
                    except:
                        message.reply_html(
                            text=f"🔻 ID: <code>{row_egroup['chat_id']}</code>\n"+
                                f"🔻 Link: {row_egroup['link']}\n"+
                                f"🔻 Total users: {row_egroup['participants_count']:,}\n"+
                                f"🔻 Online users: {row_egroup['participants_online_count']:,}\n"+
                                f"🔻 Bots: {row_egroup['participants_bot_count']}\n"+
                                "‏————————————————————\n"+
                                "♻️ Identified users (with username):\n"+
                                f"🔻 All users: {(row_egroup['users_real'] + row_egroup['users_fake']):,} (/ex_{row_egroup['id']}_a)\n"+
                                f"🔻 Real users: {row_egroup['users_real']:,} (/ex_{row_egroup['id']}_u)\n"+
                                f"🔻 Fake users: {row_egroup['users_fake']:,} (/ex_{row_egroup['id']}_f)\n"+
                                f"🔻 Users with phone: {row_egroup['users_has_phone']:,} (/ex_{row_egroup['id']}_n)\n"+
                                f"🔻 Online users: {row_egroup['users_online']:,} (/ex_{row_egroup['id']}_o)",
                            disable_web_page_preview=True,
                        )
                else:
                    try:
                        info_msg = message.reply_html(text="Sending ...")
                        try:
                            if ex_text[2] == 'a':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_all.txt","rb"),caption='Identified users')
                            elif ex_text[2] == 'u':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_username.txt","rb"),caption='Username users')
                            elif ex_text[2] == 'b':
                                bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_bots.txt","rb"),caption='Bots')
                        except:
                            message.reply_html(text="❌ There was a problem uploading the file")
                        info_msg.delete()
                    except:
                        message.reply_html(
                            text=f"🔻 ID: <code>{row_egroup['chat_id']}</code>\n"+
                                f"🔻 Link: {row_egroup['link']}\n"+
                                f"🔻 Total users: {row_egroup['participants_count']:,:,}\n"+
                                f"🔻 Online users: {row_egroup['participants_online_count']:,:,}\n"+
                                "‏————————————————————\n"+
                                "♻️ Identified users:\n"+
                                f"🔻 All users: {row_egroup['users_all']:,} (/ex_{row_egroup['id']}_a)\n"+
                                f"🔻 Username users: {row_egroup['users_real']:,} (/ex_{row_egroup['id']}_u)\n"+
                                f"🔻 Bots: {row_egroup['participants_bot_count']:,} (/ex_{row_egroup['id']}_u)",
                            disable_web_page_preview=True,
                        )
            return
        elif ex_text[0] == '/exo':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_text[1])}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ Not found")
            elif row_gtg['status'] != 'end':
                message.reply_html("❌ The order must be completed")
            else:
                type = ex_text[2]
                path = f"{directory}/files/exo_{row_gtg['id']}_{type}.txt"
                info_msg = message.reply_html(text="Sending ...")
                try:
                    if type == 'm':
                        cs.execute(f"SELECT * FROM {utl.reports} WHERE gtg_id={row_gtg['id']} AND status='send'")
                        result = cs.fetchall()
                        if not result:
                            message.reply_html(text="❌ No members found")
                        else:
                            list_users = ""
                            for row in result:
                                list_users += f"{row['username']}\n"
                            utl.write_on_file(path, list_users)
                            bot.send_document(chat_id=chat_id,document=open(path, "rb"),caption='Successful send')
                    elif type == 'r':
                        if not os.path.exists(path):
                            message.reply_html(text="❌ No members found")
                        else:
                            bot.send_document(chat_id=chat_id,document=open(path, "rb"),caption='Remaining send')
                except:
                    message.reply_html(text="❌ There is a problem")
                info_msg.delete()
            return
        elif ex_text[0] == "/d":
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_text[1]}'")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                message.reply_html(text=f"❌ Not found")
            else:
                block = 'Block ✅' if row_user_select['status'] == "block" else 'Block ❌'
                block_status = 'user' if row_user_select['status'] == "block" else 'block'
                admin = 'Admin ✅' if row_user_select['status'] == "admin" else 'Admin ❌'
                admin_status = 'user' if row_user_select['status'] == "admin" else 'admin'
                message.reply_html(
                    text=f"User <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                    reply_markup={'inline_keyboard': [
                        [{'text': "Send Message",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                        [
                            {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                            {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                        ]
                    ]}
                )
            return
        

if __name__ == '__main__':
    updater = Updater(utl.token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat_type.private & Filters.update.message & Filters.update, private_process, run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(callbackquery_process, run_async=True))
    
    # updater.start_polling(drop_pending_updates=True)
    updater.start_polling()
    updater.idle()
