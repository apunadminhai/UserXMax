# Uniborg Plugin for getting list of sites where you can watch a particular Movie or TV-Show
# Author: Sumanjay (https://github.com/cyberboysumanjay) (@cyberboysumanjay)
# All rights reserved.

import asyncio
import requests

from justwatch import JustWatch

from userbot.events import register
from userbot import (WATCH_COUNTRY, bot)
from ..help import add_help_item

def get_stream_data(query):
    stream_data = {}

    # ENV For Country Change
    try:
        country = WATCH_COUNTRY
    except Exception:
        country = "IN"

    # Cooking Data
    just_watch = JustWatch(country = country)
    results = just_watch.search_for_item(query = query)
    movie = results['items'][0]
    stream_data['watch_title'] = movie['watch_title']
    stream_data['movie_thumb'] = "https://images.justwatch.com"+movie['poster'].replace("{profile}","")+"s592"
    stream_data['release_year'] = movie['original_release_year']
    try:
        print(movie['cinema_release_date'])
        stream_data['release_date'] = movie['cinema_release_date']
    except KeyError:
        try:
            stream_data['release_date'] = movie['localized_release_date']
        except KeyError:
            stream_data['release_date'] = None

    stream_data['type'] = movie['object_type']

    available_streams = {}
    for provider in movie['offers']:
        provider_ = get_provider(provider['watch_urls']['standard_web'])
        available_streams[provider_] = provider['watch_urls']['standard_web']
    
    stream_data['providers'] = available_streams

    scoring = {}
    for scorer in movie['scoring']:
        if scorer['provider_type']=="tmdb:score":
            scoring['tmdb'] = scorer['value']

        if scorer['provider_type']=="imdb:score":
            scoring['imdb'] = scorer['value']
    stream_data['score'] = scoring
    return stream_data

#Helper Functions
def pretty(name):
    if name=="play":
        name = "Google Play Movies" 
    return name[0].upper()+name[1:]

def get_provider(watch_url):
    watch_url = watch_url.replace("https://www.","")
    watch_url = watch_url.replace("https://","")
    watch_url = watch_url.replace("http://www.","")
    watch_url = watch_url.replace("http://","")
    watch_url = watch_url.split(".")[0]
    return watch_url

@register(outgoing=True, pattern="^\.watch (.*)")
async def watch(event):
    if event.fwd_from:
        return
    query = event.pattern_match.group(1)
    await event.edit("Finding Sites...")
    streams = get_stream_data(query)
    watch_title = streams['watch_title']
    thumb_link = streams['movie_thumb']
    release_year = streams['release_year']
    release_date = streams['release_date']
    scores = streams['score']
    try:
        imdb_score = scores['imdb']
    except KeyError:
        imdb_score = None
    
    try:
        tmdb_score = scores['tmdb']
    except KeyError:
        tmdb_score = None
        
    stream_providers = streams['providers']
    if release_date is None:
        release_date = release_year

    watch_output = f"**Movie:**\n`{watch_title}`\n**Release Date:**\n`{release_date}`"
    if imdb_score:
        watch_output = watch_output + f"\n**IMDB: **{imdb_score}"
    if tmdb_score:
        watch_output = watch_output + f"\n**TMDB: **{tmdb_score}"

    watch_output = watch_output + "\n\n**Available on:**\n"
    for provider,link in stream_providers.items():
        if 'sonyliv' in link:
            link = link.replace(" ","%20")
        watch_output += f"[{pretty(provider)}]({link})\n"
    
    await bot.send_file(event.chat_id, caption=watch_output, file=thumb_link,force_document=False,allow_cache=False, silent=True)
    await event.delete()


add_help_item(
    "watch",
    "Misc",
    "Userevent module to scarp info from justwatch",
    """
    `.watch <Movie/Tv Show Name>`
    **Usage:** Provides Info From JustWatch
    """
)
