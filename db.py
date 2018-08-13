# -*- coding: utf-8 -*-
import mysql.connector      # pip install mysql-connector

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
    content varchar(1000) not null,
    primary key(id)
);
'''

def get_connect():
    conn = mysql.connector.connect(user='root', password='451284296', database='contract')    
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

def save_contract(username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, content):
    try:
        sql = "insert into contract_content(username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, content)" + \
            "values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(sql, (username, contract_name, contract_id, party_a, sig_a, party_b, sig_b, valid_time, content))
        conn.commit()
    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    save_user("zyj", "123")
    print(get_pass("zyj"))