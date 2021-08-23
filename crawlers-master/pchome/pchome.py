import requests
import pprint
import re
import random
import time
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

def mysql_connection(**kwargs):
    try:
        cnx = mysql.connector.connect(**kwargs)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        print('successfully connected to MySQL server.')

    cursor = cnx.cursor()
    return cursor,cnx


# Create datebase if not exist
def create_database(cursor,DB_NAME):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)
            )
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


# Creating table
def create_table(cursor,DB_NAME):
    TABLES = {}
    TABLES['products'] = (
        "CREATE TABLE products ("
          "name varchar(255) NOT NULL,"
          "price int NOT NULL,"
          "PRIMARY KEY (name)"
        ") ENGINE=InnoDB")
        
    
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
  
def get_proxies(url):
    res = requests.get(url)
    m = re.findall('\d+\.\d+\.\d+\.\d+:\d+', res.text)
    validips = []
    for ip in m[:100]:
        try:
            res = requests.get('https://api.ipify.org?format=json',proxies = {'http':ip, 'https':ip}, timeout = 2)
            validips.append({'ip':"http://"+ip})
            print(res.json())
        except:
            print('FAIL', ip )
        
    return validips



def main():
    load_dotenv()
    db_settings = {
    "host": os.getenv('host'),
    "port": os.getenv('port'),
    "user": os.getenv('user'),
    "password": os.getenv('password'),
    "charset": os.getenv('charset')
    }
    cursor,cnx=mysql_connection(**db_settings)
    DB_NAME='pchome'
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor,DB_NAME)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)
    create_table(cursor,DB_NAME)     
    add_product = ("INSERT IGNORE INTO products "
                   "(name, price) "
                   "VALUES (%s, %s)")
    count=0
    validips=get_proxies('https://free-proxy-list.net/')
    for i in range(1, 101):
        SSD_PCHOME_URL = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=ssd%20&page={}&sort=sale/dc'\
            .format(i)
        proxy=random.choice(validips)['ip']
        try:
            print(f'正在爬第{i}頁')
            reqs = requests.get(SSD_PCHOME_URL,proxies={'http':proxy, 'https':proxy},timeout=15)
        except:
            count+=1
            validips.remove(dict(ip=proxy))
            continue
        finally:
            time.sleep(1)
        if reqs.status_code == requests.codes.ok:
            data = reqs.json()
            for product in data['prods']:
                name = product['name']
                price = product['price']
                print(name)
                print(price)
                data_product = (name, price)
                # Insert new employee
                cursor.execute(add_product, data_product)
        else:
            count+=1
            validips.remove(dict(ip=proxy))
            print('fail')

    # Make sure data is committed to the database
    cnx.commit()
    
    print(f"總共遺失{count}頁")
    print('closing')
    cursor.close()
    cnx.close()
        
# if __name__ == "__main__":
#     main()


