import sqlite3
from config import DATABASE

statuses = [ (_,) for _ in (["Выполняется", "Выполнено", "Не выполнено"])]

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE tasks (
                            task_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            task_name TEXT NOT NULL,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                         )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                         )''')
            conn.commit()
        print("База Данных успешно создана!")

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()


    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_task(self, data):
        sql = 'INSERT OR IGNORE INTO tasks (user_id, task_name, status_id) values(?, ?, ?)'
        self.__executemany(sql, data)

    def get_statuses(self):
        sql = 'SELECT status_name FROM status'
        return self.__select_data(sql)
    
    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_tasks(self, user_id):
        return self.__select_data(sql='SELECT * FROM tasks WHERE user_id = ?', data=(user_id,))
    
    def get_task_id(self, task_name, user_id):
        return self.__select_data(sql='SELECT task_id FROM tasks WHERE task_name = ? AND user_id = ?', data=(task_name, user_id,))[0][0]
    
    def get_task_info(self, user_id, task_name):
        sql = '''
        SELECT task_name, status_name FROM projects
        JOIN status ON
        status.status_id = tasks.status_id
        WHERE task_name = ? AND user_id = ?
        '''
        return self.__select_data(sql=sql, data=(task_name, user_id))
    
    def update_tasks(self, param, data):
        self.__executemany(f'UPDATE tasks SET {param} = ? WHERE task_name = ? AND user_id = ?', [data])

    def delete_task(self, user_id, task_id):
        sql = 'DELETE FROM tasks WHERE user_id = ? AND task_id = ?'
        self.__executemany(sql, [(user_id, task_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()