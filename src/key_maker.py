import sqlite3
import os
import datetime
import pandas as pd
import secrets
import random
current_directory=os.path.dirname(os.path.realpath(__file__))
log_location=os.path.join(current_directory,'key_db')
class DB_Managements(object):
    def __init__(self):
        self.con = sqlite3.connect(os.path.join(log_location,'key.db'),check_same_thread=False)
        self.cursor_obj=None

    def cursor(self):
        self.cursor_obj=self.con.cursor()
    def execute_sql(self,sql):
        if self.cursor_obj is not None:
            return self.cursor_obj.execute(sql)
        else:
            raise Exception("Cursor Required")
    def commit(self):
        self.con.commit()
    def rollback(self):
        self.con.rollback()
    def close(self):
        self.cursor_obj.close()
        self.con.close()
    def select_statement(self,query):
        if self.cursor_obj is None:self.cursor()
        self.execute_sql(query)
        while True:
            row = self.cursor_obj.fetchone()
            if row == None:
                break
            else:
                yield row
    def ddl_statement(self,query):
        if self.cursor_obj is None:self.cursor()
        try:
            self.execute_sql(query)
        except Exception as err:
            print(err)
            self.rollback()
            return False
        else:
            self.commit()
            return True

class apiKeyManagement(DB_Managements):
    def __init__(self):
        self.table_name = 'api_key'
        super().__init__()
        self.cursor()
        if not tableExists(self.table_name):self.createTable()
    def createTable(self):
        query="""create table {table_name} (id integer, email text,key text, created text ,expired text)""".format(table_name=self.table_name)
        self.ddl_statement(query)
    def selectQuery(self,query):
        self.execute_sql(query)
        rows = self.cursor_obj.fetchall()
        cols = [column[0] for column in self.cursor_obj.description]
        df = pd.DataFrame.from_records(data=rows, columns=cols)
        return df
    def insertQuery(self,query):
        self.ddl_statement(query)
    def key_registered(self,email,key,created,expired):
        max_id=max_idx(self.table_name)
        query="""insert into {table_name} (id,email,key,created,expired)values({id},'{email}','{key}','{created}','{expired}')""".format(table_name=self.table_name,id=max_id+1,email=email,key=key,created=created,expired=expired)
        return self.insertQuery(query)
    def isapiKeyValid(self,key):
        query="""select * from {table_name} where key='{key}'""".format(table_name=self.table_name,key=key)
        df=self.selectQuery(query)
        if df.empty: return False
        else:
            expired_date=datetime.datetime.strptime(df['expired'][0], '%Y-%m-%d %H:%M:%S') #'%Y-%m-%d %H:%M:%S'
            if (expired_date-datetime.datetime.now()).total_seconds() >0:return True
            else:return False
    def isemailValid(self,email):
        query = """select * from {table_name} where email='{email}'""".format(table_name=self.table_name, email=email)
        df = self.selectQuery(query)
        if df.empty:
            return False
        return True
    def delete(self,email):
        query="""delete from {table_name} where email='{email}'""".format(table_name=self.table_name,email=email)
        self.insertQuery(query)
    def prolong_expiredDate(self,days,key=None,email=None):
        if key is None and email is None:
            raise Exception("No inputs are detected")
        else:
            expired = datetime.datetime.now() + datetime.timedelta(days=days)
            expired = expired.strftime('%Y-%m-%d %H:%M:%S')
            if key is None and email is not None:
                query="""update {table_name} set expired = '{expired}' where email='{email}'""".format(table_name=self.table_name,expired=expired,email=email)
            elif key is not None and email is None:
                query="""update {table_name} set expired = '{expired}' where key='{key}'""".format(table_name=self.table_name,expired=expired,key=key)
            else:
                query="""update {table_name} set expired = '{expired}' where key='{key}' and email='{email}'""".format(table_name=self.table_name,expired=expired,key=key, email=email)
            self.insertQuery(query)

class Logs(DB_Managements):
    def __init__(self):
        self.table_name = 'logs'
        super().__init__()
        self.cursor()
        if not tableExists(self.table_name): self.createTable()

    def createTable(self):
        query = """create table {table_name} (id integer, key text, datetime text ,ip text,status text ,result text)""".format(
            table_name=self.table_name)
        self.ddl_statement(query)
    def insert(self,key,ip,status,result):
        max_id=max_idx(self.table_name)
        query="""insert into {table_name} (id,key,datetime,ip,status,result) values({id},'{key}','{datetime}','{ip}','{status}','{result}')""".format(
            table_name=self.table_name,id=max_id+1,datetime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),key=key,ip=ip,status=status,result=result
        )
        self.ddl_statement(query)
    def selectQuery(self):
        query="""select * from {}""".format(self.table_name)

        list_result = []
        for i in self.select_statement(query):
            list_result.append(list(i))
        return list_result


def key_generator():
    length=random.randint(32,40)
    return secrets.token_urlsafe(length)


def tableExists(tableName):
    instance_db=DB_Managements()
    instance_db.cursor()
    if tableName=='' or tableName is None:
        raise Exception("Not valid table Name")
    query = """SELECT COUNT(*) FROM sqlite_master WHERE name='{}'""".format(tableName)
    instance_db.execute_sql(query)
    result=instance_db.cursor_obj.fetchone()[0]
    instance_db.close()
    return True if result==1 else False


def max_idx(table_name):
    if tableExists(table_name):
        select_instance=DB_Managements()
        select_instance.cursor()
        query="""select MAX(id) as max_index from {}""".format(table_name)
        for row in select_instance.select_statement(query):result=row[0]
        #result=select_instance.cursor_obj.fetchone()[0]
        select_instance.close()
        return 0 if result is None else result
    else:
        raise Exception("Not valid table Name")

def addToMainLogs(blogurl,status,script,msg):
    date_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_instance=DDLStatement()
    query="""insert into MAIN_LOG (BLOG_URL,STATUS,SCRIPT,MESSAGES,DATETIME)values('{blog_url}','{status}','{script}','{message}','{datetime}')""".format(blog_url=blogurl,status=status,script=script,message=msg,datetime=date_time)
    result=insert_instance.insert(query)
    insert_instance.close()
    return result
def addToSystemLogs(status,msg):
    date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_instance = DDLStatement()
    query="""insert into SYSTEM_LOG (STATUS,MESSAGES,DATETIME)values('{status}','{message}','{datetime}')""".format(status=status,message=msg,datetime=date_time)
    result=insert_instance.insert(query)
    insert_instance.close()
    return result
def getSystemLogs():
    sql="""select * from SYSTEM_LOG"""
    instance_select = SelectStatement()
    list_result = []
    for i in instance_select.getSelectResults(sql):
        list_result.append(list(i))
    instance_select.close()
    return list_result
def getLogs(idx=None):
    if idx is None:
        sql="""select * from MAIN_LOG"""
    else:
        sql="""select * from MAIN_LOG where IDX={}""".format(idx)
    instance_select=SelectStatement()
    list_result=[]
    for i in instance_select.getSelectResults(sql):
        list_result.append(list(i))
    instance_select.close()
    return list_result
