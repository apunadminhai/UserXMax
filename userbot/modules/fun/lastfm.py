# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
import os
import lyricsgenius

from asyncio import sleep
from pylast import User, WSError
from re import sub
from urllib import parse
from os import environ
from sys import setrecursionlimit
from ..help import add_help_item

from telethon.errors import AboutTooLongError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import FloodWaitError

from userbot import (BOTLOG, BOTLOG_CHATID, DEFAULT_BIO,
                     BIO_PREFIX, lastfm, LASTFM_USERNAME, GENIUS, bot)
from userbot.events import register

# =================== CONSTANT ===================
LFM_BIO_ENABLED = "```last.fm current music to bio is now enabled.```"
LFM_BIO_DISABLED = "```last.fm current music to bio is now disabled. Bio reverted to default.```"
LFM_BIO_RUNNING = "```last.fm current music to bio is already running.```"
LFM_BIO_ERR = "```No option specified.```"
LFM_LOG_ENABLED = "```last.fm logging to bot log is now enabled.```"
LFM_LOG_DISABLED = "```last.fm logging to bot log is now disabled.```"
LFM_LOG_ERR = "```No option specified.```"
ERROR_MSG = "```last.fm module halted, got an unexpected error.```"

ARTIST = 0
SONG = 0
USER_ID = 0

if BIO_PREFIX:
    BIOPREFIX = BIO_PREFIX
else:
    BIOPREFIX = None

LASTFMCHECK = False
RUNNING = False
LastLog = False
# ================================================


@register(outgoing=True, pattern="^.lastfm$")
async def last_fm(lastFM):
    """ For .lastfm command, fetch scrobble data from last.fm. """
    await lastFM.edit("`Processing...`")
    preview = None
    playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
    username = f"https://www.last.fm/user/{LASTFM_USERNAME}"
    if playing is not None:
        try:
            image = User(LASTFM_USERNAME,
                         lastfm).get_now_playing().get_cover_image()
        except IndexError:
            image = None
            pass
        tags = await gettags(isNowPlaying=True, playing=playing)
        rectrack = parse.quote(f"{playing}")
        rectrack = sub("^", "https://open.spotify.com/search/",
                       rectrack)
        if image:
            output = (f"[‎]({image})[{LASTFM_USERNAME}]({username}) __is now listening to:"
                      f"__\n\n• [{playing}]({rectrack})\n`{tags}`")
            preview = True
        else:
            output = (f"[{LASTFM_USERNAME}]({username}) __is now listening to:"
                      f"__\n\n• [{playing}]({rectrack})\n`{tags}`")
    else:
        recent = User(LASTFM_USERNAME, lastfm).get_recent_tracks(limit=3)
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        output = f"[{LASTFM_USERNAME}]({username}) __was last listening to:__\n\n"
        for i, track in enumerate(recent):
            print(i)
            printable = await artist_and_song(track)
            tags = await gettags(track)
            rectrack = parse.quote(str(printable))
            rectrack = sub("^",
                           "https://open.spotify.com/search/",
                           rectrack)
            output += f"• [{printable}]({rectrack})\n"
            if tags:
                output += f"`{tags}`\n\n"
    if preview is not None:
        await lastFM.edit(f"{output}", parse_mode='md', link_preview=True)
    else:
        await lastFM.edit(f"{output}", parse_mode='md')


async def gettags(track=None, isNowPlaying=None, playing=None):
    if isNowPlaying:
        tags = playing.get_top_tags()
        arg = playing
        if not tags:
            tags = playing.artist.get_top_tags()
    else:
        tags = track.track.get_top_tags()
        arg = track.track
    if not tags:
        tags = arg.artist.get_top_tags()
    tags = "".join([" #" + t.item.__str__() for t in tags[:5]])
    tags = sub("^ ", "", tags)
    tags = sub(" ", "_", tags)
    tags = sub("_#", " #", tags)
    return tags


async def artist_and_song(track):
    return f"{track.track}"


async def get_curr_track(lfmbio):
    global ARTIST
    global SONG
    global LASTFMCHECK
    global RUNNING
    global USER_ID
    oldartist = ""
    oldsong = ""
    while LASTFMCHECK:
        try:
            if USER_ID == 0:
                USER_ID = (await lfmbio.client.get_me()).id
            user_info = await bot(GetFullUserRequest(USER_ID))
            RUNNING = True
            playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
            SONG = playing.get_title()
            ARTIST = playing.get_artist()
            oldsong = environ.get("oldsong", None)
            oldartist = environ.get("oldartist", None)
            if playing is not None and SONG != oldsong and ARTIST != oldartist:
                environ["oldsong"] = str(SONG)
                environ["oldartist"] = str(ARTIST)
                if BIOPREFIX:
                    lfmbio = f"{BIOPREFIX} 🎧: {ARTIST} - {SONG}"
                else:
                    lfmbio = f"🎧: {ARTIST} - {SONG}"
                try:
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID,
                            f"Attempted to change bio to\n{lfmbio}")
                    await bot(UpdateProfileRequest(about=lfmbio))
                except AboutTooLongError:
                    short_bio = f"🎧: {SONG}"
                    await bot(UpdateProfileRequest(about=short_bio))
            else:
                if playing is None and user_info.about != DEFAULT_BIO:
                    await sleep(6)
                    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID, f"Reset bio back to\n{DEFAULT_BIO}")
        except AttributeError:
            try:
                if user_info.about != DEFAULT_BIO:
                    await sleep(6)
                    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID, f"Reset bio back to\n{DEFAULT_BIO}")
            except FloodWaitError as err:
                if BOTLOG and LastLog:
                    await bot.send_message(BOTLOG_CHATID,
                                           f"Error changing bio:\n{err}")
        except FloodWaitError as err:
            if BOTLOG and LastLog:
                await bot.send_message(BOTLOG_CHATID,
                                       f"Error changing bio:\n{err}")
        except WSError as err:
            if BOTLOG and LastLog:
                await bot.send_message(BOTLOG_CHATID,
                                       f"Error changing bio:\n{err}")
        await sleep(2)
    RUNNING = False


@register(outgoing=True, pattern=r"^.lastbio (on|off)")
async def lastbio(lfmbio):
    arg = lfmbio.pattern_match.group(1).lower()
    global LASTFMCHECK
    global RUNNING
    if arg == "on":
        setrecursionlimit(700000)
        if not LASTFMCHECK:
            LASTFMCHECK = True
            environ["errorcheck"] = "0"
            await lfmbio.edit(LFM_BIO_ENABLED)
            await sleep(4)
            await get_curr_track(lfmbio)
        else:
            await lfmbio.edit(LFM_BIO_RUNNING)
    elif arg == "off":
        LASTFMCHECK = False
        RUNNING = False
        await bot(UpdateProfileRequest(about=DEFAULT_BIO))
        await lfmbio.edit(LFM_BIO_DISABLED)
    else:
        await lfmbio.edit(LFM_BIO_ERR)


@register(outgoing=True, pattern=r"^.lastlog (on|off)")
async def lastlog(lstlog):
    arg = lstlog.pattern_match.group(1).lower()
    global LastLog
    LastLog = False
    if arg == "on":
        LastLog = True
        await lstlog.edit(LFM_LOG_ENABLED)
    elif arg == "off":
        LastLog = False
        await lstlog.edit(LFM_LOG_DISABLED)
    else:
        await lstlog.edit(LFM_LOG_ERR)


if GENIUS is not None:
    genius = lyricsgenius.Genius(GENIUS)


@register(outgoing=True, pattern="^.lyrics (?:(now)|(.*) - (.*))")
async def lyrics(lyric):
    await lyric.edit("`Getting information...`")
    if GENIUS is None:
        await lyric.edit(
            "`Provide genius access token to Heroku ConfigVars...`")
        return False
    if lyric.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            await lyric.edit(
                "`No information current lastfm scrobbling...`"
            )
            return False
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = lyric.pattern_match.group(2)
        song = lyric.pattern_match.group(3)
    await lyric.edit(f"`Searching lyrics for {artist} - {song}...`")
    songs = genius.search_song(song, artist)

    if songs is None:
        await lyric.edit(f"`Song`  **{artist} - {song}**  `not found...`")
        return False
    if len(songs.lyrics) > 4096:
        await lyric.edit("`Lyrics is too big, view the file to see it.`")
        with open("lyrics.txt", "w+") as f:
            f.write(f"Search query: \n{artist} - {song}\n\n{songs.lyrics}")
        await lyric.client.send_file(
            lyric.chat_id,
            "lyrics.txt",
            reply_to=lyric.id,
        )
        os.remove("lyrics.txt")
        return True
    else:
        await lyric.edit(
            f"**Search query**:\n`{artist}` - `{song}`"
            f"\n\n```{songs.lyrics}```"
        )
        return True
        
        
add_help_item(
    "lastfm",
    "Fun",
    "Userbot module containing various scrapers.",
    """
    `.lastfm`
    **Usage:** Shows currently playing track or most recent played if nothing is playing.
    
    `.lastbio <on/off>`
    **Usage:** Enables/Disables last.fm current playing to bio.
    
    `.lastlog <on/off>`
    **Usage:** Enable/Disable last.fm bio logging in the bot-log group.
    
    `.lyrics <artist name> - <song name>`
    **Usage:** Get lyrics of matched artist and song.
    
    `.lyrics now`
    **Usage:** Gets the lyrics artist and song from current playing track on lastfm.
    """
)