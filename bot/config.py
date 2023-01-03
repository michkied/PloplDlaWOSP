import discord
import asyncio
import time

TOKEN = ''
TEACHER_KEY = ''
VERIFICATION_IMAGE_URL = ''

# General config
AUCTION_GUILD = 0
VERIFIER_ROLE = 0


# Verification config
VERIFICATION_CHANNEL = 0


# Auction config
ORGANIZER_ROLE = 0
AUCTION_CHANNEL = 0
LOG_CHANNEL = 0


# Role IDs
#  0 - Student
#  1 - Graduate
#  2 - Teacher
UNVERIFIED_ROLES = [0, 1, 2]
VERIFIED_ROLES = [0, 1, 2]


# List of teacher ids
TEACHERS = []


# User guilds nickname data
# Structure:
#
# {
# USER_ID: [
#   {'guild': 'GUILD_NAME_1', 'nick': 'NICKNAME_1'},
#   {'guild': 'GUILD_NAME_2', 'nick': 'NICKNAME_2'}, ...
#   ]
# }

STUDENT_DATA = {}
