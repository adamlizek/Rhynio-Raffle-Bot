import config
import time
import re
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from src.utils import log_data

def account_to_webhook(account, site):
    webhook_url = config.global_webhook
    webhook = DiscordWebhook(url=webhook_url)
    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    desc = timestampStr
    embed = DiscordEmbed(title=site + ' Account Created!', description=desc, color=14177041)

    email = "||" + account['email'] + "||"
    password = "||" + account['password'] + "||"
    embed.add_embed_field(name='Email', value=email)
    embed.add_embed_field(name='Password', value=password)

    webhook.add_embed(embed)
    try:
        if webhook_url != "":
            webhook.execute()
    except Exception as e:
        if config.DEBUG_MODE:
            print('[Webhook] Rate Limited')


def raffle_to_webhook(account, site, raffle, name=None, zip_code=None):
    webhook_url = config.global_webhook
    webhook = DiscordWebhook(url=webhook_url)

    title = 'Account entered into ' + site + ' raffle!'
    raffle_name = raffle.replace ("_", " ")

    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    desc = timestampStr

    embed = DiscordEmbed(title=title, description=desc, color=14177041)

    if isinstance(account, dict):
        email = "||" + account['email'] + "||"
        password = "||" + account['password'] + "||"
        embed.add_embed_field(name='Email', value=email)
        embed.add_embed_field(name='Password', value=password)
        embed.add_embed_field(name="Raffle", value=raffle_name)
    else:
        email = "||" + account + "||"
        embed.add_embed_field(name='Email', value=email)
        embed.add_embed_field(name="Raffle", value=raffle_name)

    if name is not None:
        name = "||" + name + "||"
        embed.add_embed_field(name='Name', value=name)
    if zip_code is not None:
        zip_code = "||" + zip_code + "||"
        embed.add_embed_field(name='Zip Code', value=zip_code)

    webhook.add_embed(embed)
    try:
        if webhook_url != "":
            webhook.execute()
    except Exception as e:
        if config.DEBUG_MODE:
            print('[Webhook] Rate Limited')


def confirmation_to_webhook(account, site, raffle):
    webhook_url = config.global_webhook
    webhook = DiscordWebhook(url=webhook_url)

    title = 'Entry confirmed for ' + site + '!'
    raffle_name = raffle.replace ("_", " ")

    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    desc = timestampStr

    embed = DiscordEmbed(title=title, description=desc, color=14177041)

    if isinstance(account, dict):
        email = "||" + account['email'] + "||"
        password = "||" + account['password'] + "||"
        embed.add_embed_field(name='Email', value=email)
        embed.add_embed_field(name='Password', value=password)
        embed.add_embed_field(name="Raffle", value=raffle_name)
    else:
        email = "||" + account + "||"
        embed.add_embed_field(name='Email', value=email)
        embed.add_embed_field(name="Raffle", value=raffle_name)

    webhook.add_embed(embed)
    try:
        if webhook_url != "":
            webhook.execute()
    except Exception as e:
        if config.DEBUG_MODE:
            print('[Webhook] Rate Limited')


def raffle_entry_complete(site, raffle, confirmation=False):
    webhook_url = config.global_webhook
    webhook = DiscordWebhook(url=webhook_url)

    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

    if confirmation:
        keyword = 'confirmed'
    else:
        keyword = 'entered'

    desc = 'Entries complete at ' + timestampStr

    raffle_name = raffle.replace("_", " ")

    title = 'All accounts have been ' + keyword + ' into ' + site + '\'s ' + raffle_name + ' raffle!'

    embed = DiscordEmbed(title=title, description=desc, color=242424)

    webhook.add_embed(embed)
    try:
        if webhook_url != "":
            webhook.execute()
    except Exception as e:
        if config.DEBUG_MODE:
            print('[Webhook] Rate Limited')
