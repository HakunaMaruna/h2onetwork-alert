import aiosqlite

DB_NAME = "hosting_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS hostings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hosting_id INTEGER,
            name TEXT,
            ip TEXT,
            domain TEXT,
            user TEXT,
            password TEXT,
            location TEXT,
            cost REAL,
            next_payment DATE,
            interval_days INTEGER DEFAULT 30,
            FOREIGN KEY(hosting_id) REFERENCES hostings(id)
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER,
            amount REAL,
            payment_date DATE,
            FOREIGN KEY(server_id) REFERENCES servers(id)
        )''')
        await db.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)')
        await db.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', ('admin_id', '8012532918'))
        await db.commit()

async def get_hostings():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM hostings') as cursor:
            return await cursor.fetchall()

async def add_hosting(name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO hostings (name) VALUES (?)', (name,))
        await db.commit()

async def add_server(hosting_id, name, ip, domain, user, password, location, cost, date, interval):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT INTO servers 
            (hosting_id, name, ip, domain, user, password, location, cost, next_payment, interval_days) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (hosting_id, name, ip, domain, user, password, location, cost, date, interval))
        await db.commit()

async def get_servers(hosting_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM servers WHERE hosting_id = ?', (hosting_id,)) as cursor:
            return await cursor.fetchall()

async def get_server(server_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM servers WHERE id = ?', (server_id,)) as cursor:
            return await cursor.fetchone()

async def record_payment(server_id, amount, date):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO payments (server_id, amount, payment_date) VALUES (?, ?, ?)', (server_id, amount, date))
        await db.execute('''UPDATE servers SET next_payment = date(next_payment, '+' || interval_days || ' days') WHERE id = ?''', (server_id,))
        await db.commit()
