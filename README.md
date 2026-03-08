# ChatSpeaker - Discord Bot
This is a Discord bot that I made for my visually impaired friend, whitch can:
 1. Voice announcements for somebody join the voice channel.
 2. "Read-out mode" for voice announcements when someone leave message in chat.
 3. Read out the YouTube stream chat. (Twitch chat feature is comming soon in schedule)
 4. You can set your own command prefix for your Discord server

[\[Invite my bot\]](https://discord.com/oauth2/authorize?client_id=1368220788875989032)\
※ It might be down sometimes, I'll fix it ASAP when I notice.\
※ It's now running on Raspberrypi 4B so the reactions would be a little bit slow, please be patient.

### Known issue:
 - [Fixed] I just noticed this bot is not working for multiple server, I'll try to refactor it later. // Fixed in 2026.03.08
 - Welcome message not working and not server customized, yet.

### Log
 - **2025.08.09** Bot repeatedly connect to vc and fail.
    - Reason by [issue #10207](https://github.com/Rapptz/discord.py/issues/10207?utm_source=chatgpt.com) of discord.py; Fixed by update discord.py to version 2.6.0a5243+gec409a0a (alpha ver. of 2.6.0)
 - **2026.03.08** Bot repeatedly connect to vc and fail.
    - Again, Discord updated the new DAVE (Data And Voice Encryption), just update the discord lib (above v2.7.1) [pip install -U "discord.py[voice]"]
 - **2026.03.08** Fix issue: Bot would not work for multiple server in a same time.
    - Now the bot can speak in different server in the same time without waiting the queue.

## Commands
### General commands
- `>helps`
    - show helps
- `>join`
    - Join the voice channel (to the vc where the user who sent cmd)
- `>leave`
    - Leave the voice channel
- `>say_yt_chat <YouTube URL>`
    - Read out YouTube live chat
- `>stop_yt_chat`
    - Stop reading YouTube live chat
- `>say <words>`
    - Say the words
- `>readout`
    - Start reading mode (play massage on server)
- `>noreadout`
    - Stop reading mode
### Server admin commands
- `>set_prefix`
    - Set the prefix for commands in server
### Bot owner
- `>shutdown`
    - shutdown the bot

# Developer guide
## Private files format:
On the same dir level of `main_ChatSpeaker.py`
### .env
```
DC_BOT_TOKEN=<your_bot_token>
ADMIN_ID=<your_id>
```
### server_config.json
```
{
    "<server_id>": {
        "prefix": ">"
    },
    "<server_id>": {
        "prefix": ">"
    }
}
```
## Notes:
### Remember to pip the requirements
```
pip3 install -r requirements.txt
```
### Windows
 - Make sure you set ffmpeg folder in to system environment variable if you are using Windows.
 - Download ffmpeg from: [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases)
### Linux
Download FFmpeg:
```
sudo apt update
sudo apt upgrade
sudo apt install ffmpeg
```
Check installation:
```
ffmpeg -version
```

