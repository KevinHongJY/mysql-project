import pymysql

class MySqlHelper:
    def __init__(self, host, user, password, database, port=3306, charset='utf8mb4'):
        """
        初始化连接参数
        :param host: 数据库主机地址，如 'localhost'
        :param user: 数据库用户名，如 'root'
        :param password: 数据库密码
        :param database: 要操作的数据库名，如 'school'
        :param port: 数据库端口，默认 3306
        :param charset: 字符编码，默认 utf8mb4
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.conn = None  
        self.cursor = None  

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
        except pymysql.MySQLError as e:
            print(f"连接数据库失败：{e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def query(self, sql, params=None):
        """
        执行 SELECT 查询，返回所有记录列表。
        :param sql: 带占位符的 SQL 查询，如 "SELECT * FROM student WHERE height > %s"
        :param params: 与 SQL 中 %s 对应的参数元组或列表，如 (170,)
        :return: 查询结果列表，列表中每个元素为字典（DictCursor 输出格式）
        """
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchall()
            return result
        except pymysql.MySQLError as e:
            print(f"查询失败：{e}")
            return None

    def fetch_one(self, sql, params=None):
        """
        执行 SELECT 查询，只返回第一条记录。
        :param sql: 带占位符的 SQL 查询
        :param params: 参数元组或列表
        :return: 单条记录字典，若无记录则返回 None
        """
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchone()
            return result
        except pymysql.MySQLError as e:
            print(f"单条查询失败：{e}")
            return None

    def execute(self, sql, params=None):
        """
        执行 INSERT/UPDATE/DELETE 等写操作，并自动提交事务。
        :param sql: 带占位符的 SQL 语句
        :param params: 参数元组或列表
        :return: 受影响的行数
        """
        try:
            affected = self.cursor.execute(sql, params or ())
            self.conn.commit()
            return affected
        except pymysql.MySQLError as e:
            print(f"执行失败，正在回滚：{e}")
            self.conn.rollback()
            return 0

    def get_latest_hot_search(self, limit=10):
        """
        获取最新的热搜数据
        :param limit: 返回的记录数量，默认10条
        :return: 热搜数据列表
        """
        sql = """
        SELECT ranking, title, url, ts 
        FROM hot_search 
        WHERE ts >= DATE_SUB(NOW(), INTERVAL 1 DAY)
        ORDER BY ts DESC, ranking ASC
        LIMIT %s
        """
        return self.query(sql, (limit,))

    def get_hot_search_by_date(self, date):
        """
        获取指定日期的热搜数据
        :param date: 日期字符串，格式：'YYYY-MM-DD'
        :return: 热搜数据列表
        """
        sql = """
        SELECT ranking, title, url, ts 
        FROM hot_search 
        WHERE DATE(ts) = %s
        ORDER BY ts DESC, ranking ASC
        """
        return self.query(sql, (date,))
