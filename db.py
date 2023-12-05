import pymysql.cursors
import utility as utl


cs = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = cs.cursor()

def alter_table(cs, sql):
    try:
        cs.execute(sql)
    except:
        pass
    try:
        sql_split = sql.split(" ")
        if sql[0:11] == 'ALTER TABLE':
            if 'UNIQUE' in sql:
                try:
                    cs.execute(f"ALTER TABLE {sql_split[2]} ADD CONSTRAINT {sql_split[4]} UNIQUE({sql_split[4]})")
                except:
                    pass
            sql = sql.replace("ADD", "CHANGE").replace(" UNIQUE", "")
            sql_split_2 = sql.split(f"{sql_split[2]} ")
            sql_split_2[1] = sql_split_2[1].replace(f"{sql_split[4]}", f"{sql_split[4]} {sql_split[4]}")
            sql = f"{sql_split[2]} ".join(sql_split_2)
            cs.execute(sql)
    except:
        pass

alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.admini} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD cache varchar(50) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD change_pass tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD exit_session tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD is_change_profile tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD is_set_username tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD gtg_per tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD time_spam_restrict int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD api_per_number int(11) NOT NULL DEFAULT 1")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD limit_per_h int(11) NOT NULL DEFAULT 24")
alter_table(cs, f"ALTER TABLE {utl.admini} ADD add_per_h int(11) NOT NULL DEFAULT 16")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.analyze} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD gtg_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD user_id varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD username varchar(50) DEFAULT NULL UNIQUE")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD group_id varchar(30) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD is_real tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD is_fake tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD is_phone tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD is_online tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD is_bad tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD reserved_by varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.analyze} ADD created_at int(11) NOT NULL DEFAULT 0")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.apis} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.apis} ADD api_id varchar(20) DEFAULT NULL UNIQUE")
alter_table(cs, f"ALTER TABLE {utl.apis} ADD api_hash varchar(200) DEFAULT NULL UNIQUE")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.egroup} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD type TINYINT(1) NOT NULL DEFAULT 0 AFTER id")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD user_id varchar(30) DEFAULT NULL AFTER type")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD chat_id varchar(30) DEFAULT NULL AFTER user_id")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD link varchar(200) DEFAULT NULL AFTER chat_id")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD status varchar(50) DEFAULT NULL AFTER link")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD users_all int(11) NOT NULL DEFAULT 0 AFTER status")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD users_real int(11) NOT NULL DEFAULT 0 AFTER users_all")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD users_fake int(11) NOT NULL DEFAULT 0 AFTER users_real")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD users_has_phone int(11) NOT NULL DEFAULT 0 AFTER users_fake")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD users_online int(11) NOT NULL DEFAULT 0 AFTER users_has_phone")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD participants_count int(11) NOT NULL DEFAULT 0 AFTER users_online")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD participants_online_count int(11) NOT NULL DEFAULT 0 AFTER participants_count")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD participants_bot_count int(11) NOT NULL DEFAULT 0 AFTER participants_online_count")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD created_at int(11) NOT NULL DEFAULT 0 AFTER participants_bot_count")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD updated_at int(11) NOT NULL DEFAULT 0 AFTER created_at")
alter_table(cs, f"ALTER TABLE {utl.egroup} ADD uniq_id varchar(20) DEFAULT NULL UNIQUE AFTER updated_at")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.files} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.files} ADD gtg_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.files} ADD type_message varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.files} ADD message_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.files} ADD created_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.files} ADD uniq_id varchar(20) DEFAULT NULL")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.gtg} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD user_id varchar(20) DEFAULT NULL AFTER id")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD cats varchar(100) NULL DEFAULT NULL AFTER user_id")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD group_link varchar(200) DEFAULT NULL AFTER cats")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD group_id varchar(20) DEFAULT NULL AFTER group_link")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count int(11) NOT NULL DEFAULT 0 AFTER group_id")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD max_users int(11) NOT NULL DEFAULT 0 AFTER count")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_request int(11) NOT NULL DEFAULT 0 AFTER max_users")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD last_bot_check varchar(20) DEFAULT NULL AFTER count_request")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD type_users varchar(50) DEFAULT NULL AFTER last_bot_check")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD type_send varchar(50) DEFAULT NULL AFTER type_users")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD status varchar(50) DEFAULT NULL AFTER type_send")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD status_analyze varchar(10) DEFAULT NULL AFTER status")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_spam int(11) NOT NULL DEFAULT 0 AFTER status_analyze")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_acc int(11) NOT NULL DEFAULT 0 AFTER count_spam")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_restrict int(11) NOT NULL DEFAULT 0 AFTER count_acc")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_restrict_error int(11) NOT NULL DEFAULT 0 AFTER count_restrict")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_report int(11) NOT NULL DEFAULT 0 AFTER count_restrict_error")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_accout int(11) NOT NULL DEFAULT 0 AFTER count_report")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_usrspam int(11) NOT NULL DEFAULT 0 AFTER count_accout")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_userincorrect int(11) NOT NULL DEFAULT 0 AFTER count_usrspam")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD count_other_errors int(11) NOT NULL DEFAULT 0 AFTER count_userincorrect")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD add_per_h int(11) NOT NULL DEFAULT 0 AFTER count_other_errors")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD created_at int(11) NOT NULL DEFAULT 0 AFTER add_per_h")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD updated_at int(11) NOT NULL DEFAULT 0 AFTER created_at")
alter_table(cs, f"ALTER TABLE {utl.gtg} ADD uniq_id varchar(20) DEFAULT NULL UNIQUE AFTER updated_at")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.mbots} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD creator_user_id varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD cat_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD phone varchar(20) DEFAULT NULL UNIQUE")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD user_id varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD status varchar(50) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD end_restrict int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD last_order_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD last_leave_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD last_delete_chats_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD api_id varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD api_hash varchar(200) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD phone_code_hash varchar(100) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD code int(11) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD password varchar(100) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD is_change_pass tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD change_pass_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD is_exit_session tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD exit_session_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD is_change_profile tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD is_set_username tinyint(1) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD created_at int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.mbots} ADD uniq_id varchar(20) DEFAULT NULL UNIQUE")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.reports} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD gtg_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD bot_id int(11) NOT NULL DEFAULT 0")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD user_id varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD username varchar(50) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD group_id varchar(30) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD status varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.reports} ADD created_at int(11) NOT NULL DEFAULT 0")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.cats} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.cats} ADD name varchar(50) DEFAULT NULL UNIQUE")
alter_table(cs, f"UPDATE {utl.mbots} SET cat_id=1 WHERE cat_id=0")


alter_table(cs, f"CREATE TABLE IF NOT EXISTS {utl.users} (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;")
alter_table(cs, f"ALTER TABLE {utl.users} ADD id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY")
alter_table(cs, f"ALTER TABLE {utl.users} ADD user_id varchar(20) DEFAULT NULL UNIQUE")
alter_table(cs, f"ALTER TABLE {utl.users} ADD status varchar(20) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.users} ADD step varchar(50) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.users} ADD created_at int(11) DEFAULT NULL")
alter_table(cs, f"ALTER TABLE {utl.users} ADD uniq_id varchar(20) DEFAULT NULL UNIQUE")


cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()
if row_admin is None:
    cs.execute(f"INSERT INTO {utl.admini} (id) VALUES (1)")
cs.execute(f"SELECT * FROM {utl.cats}")
row_cats = cs.fetchone()
if row_cats is None:
    cs.execute(f"INSERT INTO {utl.cats} (id,name) VALUES (1,'default')")