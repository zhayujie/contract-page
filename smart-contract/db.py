# -*- coding: utf-8 -*-

'''
create table users(
    id int not null auto_increment, 
    name varchar(100) not null,
    pass varchar(100) not null,
    primary key(id)
);

create table contract_content(
    id int not null auto_increment,
    username varchar(100) not null,
    contract_name varchar(100) not null,
    contract_id varchar(100) not null,
    party_a varchar(100) not null,
    sig_a varchar(100) not null,
    party_b varchar(100) not null,
    sig_b varchar(100) not null,
    valid_time date not null,
    object_desc varchar(500) not null,
    content varchar(1000) not null,
    primary key(id)
);
'''

import mysql.connector      # pip install mysql-connector
import util

config = util.get_config()
USER = config["user"]
PASSWORD = config["password"]
DATABASE = config["database"] 

def get_connect():
    conn = mysql.connector.connect(user=USER, password=PASSWORD, database=DATABASE)    
    return conn


def save_user(username, password):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute('insert into users(name, pass) values(%s, %s)', (username, password))
        conn.commit()
    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_pass(username):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        # 这里使用(username)会报错
        cursor.execute('select pass from users where name = %s', (username,))
        password = cursor.fetchall()
    except Exception as e:
        print(e)        
    finally:
        cursor.close()
        conn.close()
    if not password:
        return password
    else:
        return password[0][0]

def save_contract(username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, object_desc, content):
    # calculate the contract_id
    #contract_id = util.get_id(username, contract_name)
    try:
        sql = "insert into contract_content(username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, object_desc, content)" + \
            "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(sql, (username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, object_desc, content))
        conn.commit()
    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_user_contracts(username):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute('select contract_id, contract_name, party_a, party_b, valid_time, object_desc from contract_content where username = %s order by id desc', (username,))
        contracts = cursor.fetchall()
    except Exception as e:
        print(e)        
    finally:
        cursor.close()
        conn.close()
    return contracts


def get_contract(username, contract_id):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute('select * from contract_content where username = %s and contract_id = %s', (username, contract_id))
        contracts = cursor.fetchall()
    except Exception as e:
        print(e)        
    finally:
        cursor.close()
        conn.close()
    return contracts[0]


if __name__ == '__main__':
    save_user("zyj", "123")
    print(get_pass("zyj"))