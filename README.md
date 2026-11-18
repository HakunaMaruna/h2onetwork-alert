# H2ONetwork Alert Bot

Бот для Telegram, созданный для автоматизации напоминаний об оплате хостинга и управления серверами.

## Авторы
- **AI Agent (PocketCode)** — разработка логики, БД и архитектуры бота.
- **HakunaMaruna** — идея, управление и финальное развертывание.

## Функционал
- **Иерархическая структура:** Хостинг -> Серверы.
- **Управление:** Добавление, редактирование и удаление данных.
- **Копирование данных:** Удобный просмотр параметров (IP, пароли, домены).
- **Статистика:** Общий обзор количества серверов и сумм затрат.

---

## Установка на сервер (Инструкция для чайников)

Для работы бота вам понадобится сервер с **Ubuntu** (например, 22.04) и установленным Python 3.

### Шаг 1: Подключение
Зайдите на свой сервер через SSH (используйте Terminal или PuTTY).

### Шаг 2: Подготовка сервера
Выполните команды по очереди:

1. **Обновите систему:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Установите необходимое ПО:**
   ```bash
   sudo apt install git python3 python3-pip -y
   ```

### Шаг 3: Настройка бота
1. Переименуйте файл `.env.example` (или создайте `.env`) и укажите в нем свои данные:
   ```bash
   cp .env.example .env
   nano .env
   ```
   Впишите туда:
   - `BOT_TOKEN` — токен вашего бота от @BotFather.
   - `ADMIN_ID` — ваш ID в Telegram.
   - `ALERT_CHAT_ID` — ID группы или канала для уведомлений.

2. Установите библиотеки:
   ```bash
   pip3 install aiogram aiosqlite python-dotenv --break-system-packages
   ```

### Шаг 4: Запуск
1. **Первый запуск (тестовый):**
   ```bash
   python3 bot.py
   ```
   Если вы видите в консоли надпись про "polling" — бот работает. Нажмите `Ctrl+C`, чтобы остановить.

2. **Настройка автозапуска (чтобы бот работал 24/7):**
   Выполните эту команду целиком, чтобы создать службу:
   ```bash
   cat <<EOF | sudo tee /etc/systemd/system/hostingbot.service
   [Unit]
   Description=Hosting Alert Bot
   After=network.target

   [Service]
   User=root
   WorkingDirectory=$(pwd)
   ExecStart=/usr/bin/python3 $(pwd)/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   EOF

   sudo systemctl daemon-reload
   sudo systemctl enable hostingbot
   sudo systemctl start hostingbot
   ```

Бот запущен! Теперь он будет автоматически стартовать при включении сервера.
