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

# Developer gide
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
Put `ffmpeg.exe` in `py/tools`, 
and make sure you set ffmpeg in to system environment variable
Download ffmpeg from: [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases)
