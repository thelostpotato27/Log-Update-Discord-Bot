import discord
import csv
import gspread
import pandas as pd
from discord import commands

bot = commands.Bot(command_prefix='$')
discord_client = discord.Client()


recorded_logs_channel = discord.utils.get(discord_client.get_all_channels(), name="recorded-logs")
class_logs_channel = discord.utils.get(discord_client.get_all_channels(), name="class-logs")
channel_id = recorded_logs_channel.id
class_logs = "temp"         #.csv file holding class_logs
logs_message = "temp"       #specific message that holds the class_logs file
final_owed = "temp"         #.csv file holding final amounts owed
final_owed_message = "temp" #specific message holding amount owed file

@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))
    async for m in discord_client.logs_from(recorded_logs_channel):
        if m.content() == "name of class logs":
            class_logs = discord.request(discord.GET, m.attachments[0].url)
            logs_message = m
            print('class_logs found'.format(discord_client))
        if m.content() == "name of final owed":
            final_owed = discord.request(discord.GET, m.attachments[0].url)
            final_owed_message = m
            print('final_owed found'.format(discord_client))
    print('Finished!'.format(discord_client))



    #Basically, this will be a check method. Whenever the bot starts itself up,
    #it should do a check to see if the class_logs and final_owed match up with
    #each other. As this is a safety feature and not part of the base functionality,
    #it will be left here until I can get to it.

    # csv_r_class_logs = csv.reader(class_logs, delimiter=' ')
    # csv_r_final_owed = csv.reader(final_owed, delimiter=' ')

    # all_students = []
    # for x in range(sheet_instance.row_count):
    #     full_name = sheet_instance.cell(col=1,row=x+1)
    #     subject = sheet_instance.cell(col=2,row=x+1)
    #     date = sheet_instance.cell(col=3,row=x+1)
    #     student_data = [full_name, subject, date]
    #     all_students.append(student_data)



@bot.command()
async def on_message(message):
    if message.author == discord_client.user:           #checks that it's not responding to itself
        return

    if message.content.startswith('$Taught'):   #checks that msg starts with $Taught
        words = message.content.split()
        date = words[5]
        time = words[4]
        full_name = words[1] + '_' + words[2]
        subject = words[3]
        class_cost = "temp"                     #need to make a csv file to store the prices of certain class types
        with open(class_logs, 'w', newline='') as csvfile:      #change to DictWriter, makes it easier to parse through
            csv_w_class_logs = csv.writer(csvfile, delimiter=' ')
            csv_w_class_logs.writerow([date] + [time] + [full_name] + [subject] + [class_cost])
        await recorded_logs_channel.send(file = class_logs)

        with open(final_owed, 'w', newline='') as csvfile:      #final owed is a Dictcsv of Name, Amount Due
            csv_r_final_owed = csv.DictReader(csvfile)



        await 
        csv_w_final_owed = csv.writer(final_owed, delimiter=' ')

discord_client.run('put token here')
