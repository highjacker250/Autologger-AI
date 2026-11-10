#!/bin/bash
# Webhook aur Dashboard start karo background me
python main.py &
# Telegram bot start karo foreground me
python bot.py
