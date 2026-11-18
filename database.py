import aiosqlite

DB_NAME = "hosting_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS hostings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cost REAL,
                next_payment_date DATE,
                interval_days INTEGER DEFAULT 30
            )
        ''')
        # Таблица истории оплат
        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hosting_id INTEGER,
                amount REAL,
                payment_date DATE,
                FOREIGN KEY(hosting_id) REFERENCES hostings(id)
            )
        ''')
        await db.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', ('admin_id', '8012532918'))
        await db.commit()

async def update_hosting(hosting_id, name, cost, next_date, interval):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE hostings 
            SET name = ?, cost = ?, next_payment_date = ?, interval_days = ?
            WHERE id = ?
        ''', (name, cost, next_date, interval, hosting_id))
        await db.commit()

async def record_payment(hosting_id, amount, date):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO payments (hosting_id, amount, payment_date) VALUES (?, ?, ?)', (hosting_id, amount, date))
        # Обновляем дату следующего платежа
        await db.execute('''
            UPDATE hostings 
            SET next_payment_date = date(next_payment_date, '+' || interval_days || ' days')
            WHERE id = ?
        ''', (hosting_id,))
        await db.commit()

async def get_hostings():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM hostings') as cursor:
            return await cursor.fetchall()

async def get_config(key):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT value FROM config WHERE key = ?', (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_config(key, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        await db.commit()
