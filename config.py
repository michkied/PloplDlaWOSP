import discord
import asyncio
import time

TOKEN = ''

# General config
bot_id = 0
server_id = 0
mod_role_id = 0


# Verification config
only_verification_channel = 0
applications_channel = 0


# Auction config
auction_organizer_id = 0
auction_channel = 0
log_channel = 0


# Role IDs
#  0 - Student
#  1 - Graduate
#  2 - Teacher
unverified_roles = [0, 1, 2]
verified_roles = [0, 1, 2]


# List of teacher ids
teachers = []


# User guilds nickname data
# Structure:
#
# {
# USER_ID: [
#   {'guild': 'GUILD_NAME_1', 'nick': 'NICKNAME_1'},
#   {'guild': 'GUILD_NAME_2', 'nick': 'NICKNAME_2'}, ...
#   ]
# }

users_data = {}
