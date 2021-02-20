import datetime
import sqlite3
import pathlib
from .utils import repo


format = "%Y-%m-%d %H:%M:%S"

# 适配器
def adapt_date(date):
    return datetime.datetime.strftime(format, date)

# 转换器
def convert_date(string):
    return datetime.datetime.strptime(string.decode(), format)

# 注册适配器 & 转换器
sqlite3.register_adapter(datetime.datetime, adapt_date)
sqlite3.register_converter("date", convert_date)


def init():
    conn = sqlite3.connect(pathlib.Path(repo.git_dir)/'gf.db')
    cur = conn.cursor()
    sql_text = '''CREATE TABLE commits
            (author TEXT,
            id TEXT,
            num NUMBER,
            insertions NUMBER,
            deletions NUMBER,
            date DATE
            );'''
    cur.execute(sql_text)
    conn.close()

def fetch():
    conn = sqlite3.connect(pathlib.Path(repo.git_dir)/'gf.db')
    cur = conn.cursor()
    sql_text = '''SELECT * from commits;
            '''
    cur.execute(sql_text)
    data=cur.fetchall()
    print(data)
    conn.close()


def insert(cmt):
    conn = sqlite3.connect(pathlib.Path(repo.git_dir)/'gf.db')
    cur = conn.cursor()
    sql_text = f'''INSERT INTO commits(author, id, num, insertions, deletions, date) VALUES
        ('{cmt.committer.name}', 
        '{cmt.hexsha[:7]}',
        {cmt.count()},
        {cmt.stats.total["insertions"]},
        {cmt.stats.total["deletions"]},
        '{cmt.committed_datetime.strftime(format)}'
        );'''
    print(sql_text)
    cur.execute(sql_text)
    conn.commit()
    data=cur.fetchall()
    print(data)
    conn.close()



class GfDB:
    def __init__(self):
        pass

    def __enter__(self):
        self.conn = sqlite3.connect(pathlib.Path(repo.git_dir)/'gf.db')
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exception_type,exception_value,exception_traceback):
        self.conn.close()

    def create_table(self):
        sql = '''CREATE TABLE commits
            (author TEXT,
            id TEXT,
            num NUMBER,
            insertions NUMBER,
            deletions NUMBER,
            date DATE
            );'''
        try:
            self.cur.execute(sql)
        except sqlite3.OperationalError as e:
            print(e)

    def fetch(self, cmt, *keys):
        values = ','.join(keys) or '*'
        sql = f'''SELECT {values} from commits where id = '{cmt.hexsha}';'''
        try:
            self.cur.execute(sql)
        except sqlite3.OperationalError as e:
            print(e)
            self.create_table()
        return self.cur.fetchone()

    def insert(self, cmt):
        num = cmt.count()
        insertion = cmt.stats.total["insertions"] 
        deletion = cmt.stats.total["deletions"] 
        sql = f'''INSERT INTO commits(author, id, num, insertions, deletions, date) VALUES
            ('{cmt.committer.name}', 
            '{cmt.hexsha}',
            {num},
            {insertion},
            {deletion},
            '{cmt.committed_datetime.strftime(format)}'
            );'''
        self.cur.execute(sql)
        self.conn.commit()
        return num, insertion, deletion

    def setdefault(self, cmt):
        '''Insert commit data of "cmt" if commit_id is not in the database.
        Return the value for commit if commit_id is in the database.
        '''
        try:
            num, ins, de = self.fetch(cmt, 'num', 'insertions', 'deletions') 
        except TypeError:
            num, ins, de =  self.insert(cmt)
        return num, ins, de

    def all(self):
        sql = f'''SELECT * from commits;'''
        self.cur.execute(sql)
        return self.cur.fetchall()
