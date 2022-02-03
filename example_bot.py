import discord
import csv
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('add_json_file_here.json', scope)
sheet_client = gspread.authorize(creds)

sheet = sheet_client.open('commentary data')
sheet_instance = sheet.get_worksheet(0)

all_students = []
for x in range(sheet_instance.row_count):
    full_name = sheet_instance.cell(col=1,row=x+1)
    subject = sheet_instance.cell(col=2,row=x+1)
    date = sheet_instance.cell(col=3,row=x+1)
    student_data = [full_name, subject, date]
    all_students.append(student_data)




discord_client = discord.Client()


@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))


@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:           #checks that it's not responding to itself
        return

    if message.content.startswith('$Taught'):   #checks that msg starts with $Taught
        words = message.content.split()
        full_name = words[1] + words[2]
        
        await message.channel.send('Hello!')

discord_client.run('put token here')
