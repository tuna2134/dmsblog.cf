from aiosqlite3 import connect

class Cursor:
    def __init__(self, connect, cursor):
        self.connect = connect
        self.cursor = cursor

    def execute(self, *args, **kwargs):
        return self.cursor.execute(*args, **kwargs)

    async def create_table(self, tablename, data:dict):
        values = ", ".join(f"{t} {data[t]}" for t in data)
        await self.execute(f"CREATE TABLE IF NOT EXISTS {tablename}({values})")

    def from_dict(self, datas:dict):
        args = [datas[data] for data in datas]
        co = ", ".join(data for data in datas)
        return co, args

    async def insert_data(self, tablename, data:dict):
        co, args = self.from_dict(data)
        query = ("?, " * len(args))[:-2]
        await self.execute(f"INSERT INTO {tablename} ({co}) VALUES({query})" , args)

    async def delete_data(self, tablename, where = None):
        list = []
        where_text = ""
        if where is not None:
            where_text = "WHERE "
            for name in where:
                where_text += f"{name}=? AND"
                list.append(where[name])
        where_text = where_text[:-4]
        await self.execute(f"DELETE FROM {tablename} {where_text}", list)
    
    async def update_data(self, tablename, where, data):
        list = []
        set = ", ".join(f"{name}=?" for name in data)
        for name in data:
            list.append(data[name])
        wh = "WHERE "
        for w in where:
            wh += f"{w}=? AND "
            list.append(where[w])
        wh = wh[:-5]
        cmd = f"UPDATE {tablename} SET {set} {wh}"
        await self.execute(cmd, list)

    async def get_datas(self, tablename, data:dict = None):
        where = ""
        list = []
        if data is not None:
            where = "WHERE "
            for d in data:
                where += f"{d}=? AND "
                list.append(data[d])
            where = where[:-5]
        await self.execute(f"SELECT * FROM {tablename} {where}", list)
        carams = [description[0] for description in self.cursor.description]
        rows = await self.cursor.fetchall()
        result = []
        for row in rows:
            dt = {}
            for caram, r in zip(carams, row):
                dt[caram] = r
            result.append(dt)
        return result

    async def get_data(self, tablename, data:dict = None):
        where = ""
        list = []
        if data is not None:
            where = "WHERE "
            for d in data:
                where += f"{d}=? AND "
                list.append(data[d])
            where = where[:-5]
        await self.execute(f"SELECT * FROM {tablename} {where}", list)
        carams = [description[0] for description in self.cursor.description]
        rows = await self.cursor.fetchone()
        if rows is None:
            return None
        result = {}
        for caram, row in zip(carams, rows):
            result[caram] = row
        return result

class aiodatabase:
    """aiosqlite3をもっと簡単にしたやつです
    
    Parameters
    ----------
    filename:str
      データベースのファイルの名前"""
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.paramater = (args, kwargs)
        
    async def __aenter__(self, *args, **kwargs):
        self.connect = await connect(self.filename)
        self.cursor = await self.connect.cursor()
        return Cursor(self.connect, self.cursor)

    async def __aexit__(self, *args, **kwargs):
        await self.connect.commit()
        await self.cursor.close()
        await self.connect.close()