import os
import sys
import feedparser
from sql import db
from time import sleep, time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser, tz


try:
    api_id = 1663481   # Get it from my.telegram.org
    api_hash = "5b2a54725e42f321a99bfddfbdc042ca"   # Get it from my.telegram.org
    feed_urls = ["http://feeds.feedburner.com/x265/rip","http://feeds.feedburner.com/pahe/ph","http://feeds.feedburner.com/heteam"]  # RSS Feed URL of the site.
    bot_token = os.environ.get("BOT_TOKEN")   # Get it by creating a bot on https://t.me/botfather
    log_channel = -1001513061317   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))   # Max parallel instance to be used.
except Exception as e:
    print(e)
    print("One or more variables missing. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client(":memory:", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

fmt = '%A, %B %d %H:%M:%S'
def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        entry = FEED.entries[0]
        if entry.id != db.get_link(feed_url).link:
                       # ↓ Edit this message as your needs.
            dt = parser.parse(entry.published)
            published = dt.astimezone(tz.gettz('Asia/Kolkata'))
            date = published.strftime(fmt)
            message = f"**{entry.title}**\n```{entry.link}```\n**{date}**"
            try:
                app.send_message(log_channel, message)
                db.update_link(feed_url, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
app.run()
