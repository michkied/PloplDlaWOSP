import discord
import asyncio
import time
import os

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


# Old guild data used for verification
OLD_GUILD = 0
OLD_VERIFIED_ROLES = [0, 1, 2]


# List of teacher ids
TEACHERS = []


