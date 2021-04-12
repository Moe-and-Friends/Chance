import asyncio
import datetime
import discord
import random
import shelve

from ayumi import Ayumi
from collections import defaultdict
from config import settings
from discord.ext.tasks import loop
from functools import partial

WEEKS_IN_MINUTES = 10080
DAYS_IN_MINUTES = 1440
HOURS_IN_MINUTES = 60
MINUTES_IN_MINUTES = 1

TIME_INTERVALS = (
    ('weeks', WEEKS_IN_MINUTES),
    ('days', DAYS_IN_MINUTES),
    ('hours', HOURS_IN_MINUTES),
    ('minutes', MINUTES_IN_MINUTES),
)


def convert_interval_str_to_minutes(input):
    time = int("".join(filter(str.isdigit, input)))
    if input.endswith("m"):
        return time * MINUTES_IN_MINUTES # lol
    elif input.endswith("h"):
        return time * HOURS_IN_MINUTES 
    elif input.endswith("d"):
        return time * DAYS_IN_MINUTES
    elif input.endswith("w"):
        return time * WEEKS_IN_MINUTES


def select_gacha_time():
    """
    Returns the time in minutes. Defaults to 0.
    """
    intervals_raw = settings.get("INTERVALS")
    if not intervals_raw:
        return 0

    weights = list()
    intervals = list()

    for interval_raw in intervals_raw:
        weights.append(int("".join(filter(str.isdigit, interval_raw['probability']))))
        intervals.append((
            convert_interval_str_to_minutes(interval_raw['lower']),
            convert_interval_str_to_minutes(interval_raw['upper']))
        )

    if sum(weights) != 100:
        Ayumi.warning("Configuration for probabilities does not sum to 100%", color=Ayumi.LRED)
        return 0
    else:
        try:
            interval = random.choices(intervals, weights)[0]
            minutes = random.randint(interval[0], interval[1])
            Ayumi.info("Generated a roll time of {} minutes".format(minutes))
            return minutes
        except:
            return 0


def display_time(minutes, granularity=2):
    """
    Converts the minutes we have into an English string to display to users.
    """
    result = []
    for name, count in TIME_INTERVALS:
        value = minutes // count
        if value:
            minutes -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    start, _, end = ', '.join(result[:granularity]).rpartition(',')
    return start + " and" + end if start else end


# Enable the members intents so we can remove the mute role once the timeout gives up.
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

muted_users = shelve.open("muted_users.data", writeback=True)  # For tracking when users get muted.


@ loop(seconds=5)
async def countdown_to_unmute():
    await client.wait_until_ready()

    now = datetime.datetime.now()
    Ayumi.debug("Background loop processing potential unmute jobs at {time} for: {users}".format(
        time=now.strftime("%c"), users=[x['author_name'] for x in muted_users.values()]
    ))

    for uid, mdata in dict(muted_users).items():
        if now > mdata['expiry']:  # If the current time is greater than the predetermined ban time.

            guild = client.get_guild(mdata['gid'])
            author = guild.get_member(int(uid))
            roles = [guild.get_role(rid) for rid in settings.get("LETHAL_ROLE_IDS", [])]

            Ayumi.info("Time has passed for user {id} {name}, removing role(s).".format(id=int(uid), name=mdata['author_name']))
            for role in roles:
                await author.remove_roles(role, atomic=True)
            muted_users.pop(uid)


@ client.event
async def on_message(message):

    Ayumi.debug("Processing message: [{author}@{id}: {content}".format(author=message.author.name, id=message.id, content=message.content))

    # Ignore messages sent by other bots, including oneself.
    if message.author.bot:
        Ayumi.debug("Ignoring message as it is a bot message")
        return

    if message.guild.id not in settings.get("DISCORD_GUILD_IDS"):
        Ayumi.debug("Ignoring message sent as it is from external guild with id {id}".format(id=message.guild.id))
        return

    if any(emoji in message.content for emoji in settings.get('TRIGGERS', [])):

        Ayumi.info("Found emoji in message {id}, proceeding to process.".format(id=message.id), color=Ayumi.GREEN)

        effect_time = select_gacha_time()
        Ayumi.info("{id}: Generated effect time at {mins} minutes".format(id=message.id, mins=effect_time))

        exclude_roles = [message.guild.get_role(sid) for sid in settings.get('COMRADE_ROLE_IDS', [])]
        author_roles = message.author.roles
        roles_to_add = [message.guild.get_role(rid) for rid in settings.get('LETHAL_ROLE_IDS', [])]

        is_user_safe = any(role in author_roles for role in exclude_roles)
        Ayumi.info("{id}: User safety: {safe}".format(id=message.id, safe=is_user_safe))

        if effect_time > 0:

            # Get the roles for comparison

            # Don't mute any excluded roles (yes this is inefficient)
            if is_user_safe:

                await message.reply(settings.get('NANA_COMRADE_LETHAL_MESSAGE').format(
                    time=display_time(effect_time, 3)
                ))

            else:

                # Wait for the role add to go through BEFORE calculating remove time.
                for role in roles_to_add:
                    await message.author.add_roles(role, atomic=True)

                now = datetime.datetime.now()
                uneffect_time = now + datetime.timedelta(minutes=effect_time)
                muted_users[str(message.author.id)] = {"expiry": uneffect_time, "gid": message.guild.id, "mid": message.id, "author_name": message.author.name}
                Ayumi.info("Adding lethal roles to user {id} ({name}) at {time}".format(id=message.author.id, name=message.author.name, time=now.strftime("%c")))

                await message.reply(settings.get('NANA_CAPITALIST_LETHAL_MESSAGE').format(
                    time=display_time(effect_time, 3)
                ))

        else:

            if is_user_safe:
                await message.reply(settings.get('NANA_COMRADE_SAFE_MESSAGE'))
            else:
                await message.reply(settings.get('NANA_CAPITALIST_SAFE_MESSAGE'))


if __name__ == "__main__":
    countdown_to_unmute.start()
    client.run(settings.get("DISCORD_TOKEN"))
