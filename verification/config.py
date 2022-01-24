import discord
import asyncio
import time

applications_channel = 0  # ID

# Role IDs
#  0 - Student
#  1 - Graduate
#  2 - Teacher

unverified_roles = {}

verified_roles = {}


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
