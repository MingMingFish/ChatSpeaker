# ChatSpeaker - Discord Bot
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

