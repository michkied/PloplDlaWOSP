import discord
import asyncio
import time

applications_channel = 0
bot_id = 0
server_id = 0
mod_role_id = 0

# Auction IDs
auction_organizator_id = 0
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


# User class guilds nickname data
# Structure:
#
# {
# USER_ID: [
#   {'guild': 'GUILD_NAME_1', 'nick': 'NICKNAME_1'},
#   {'guild': 'GUILD_NAME_2', 'nick': 'NICKNAME_2'}, ...
#   ]
# }

users_data = {}
