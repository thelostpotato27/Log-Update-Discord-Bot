import discord
import csv
import gspread
import pandas as pd
from discord import commands
import shutil
from tempfile import NamedTemporaryFile


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


#this bot command should take in a msg of form ($Taught First_name Last_name subject time date) and
#1. Add a log to the class_logs .csv file
#2. Find out how much is owed for that specific class that was taught
#3. Add the amount owed to that specific students final_owed .csv
#4. replace the .csv files on the discord channel with the newly updated ones


@bot.command()
async def on_message(message):
    #checks that it's not responding to itself
    if message.author == discord_client.user:
        return

    #checks that msg starts with $Taught
    #msg format is $Taught First_name Last_name subject time date
    if message.content.startswith('$Taught'):   
        words = message.content.split()         
        date = words[5]
        time = words[4]
        full_name = words[1] + '_' + words[2]
        subject = words[3]
        class_cost = "temp"                     #need to make a csv file to store the prices of certain class types
        with open(class_logs, 'w', newline='') as csvfile:      #.csv to hold classes held
            csv_w_class_logs = csv.writer(csvfile, delimiter=' ')
            csv_w_class_logs.writerow([date] + [time] + [full_name] + [subject] + [class_cost])
        await recorded_logs_channel.send(file = class_logs)

        #accessing .csv that holds prices of classes held in dict of subject, amount.
        #takes the subject of the class taught and returns the price of the class taught

        amount_owed = 0
        with open(class_cost, 'r', newline='') as csvfile:      
            reader = csv.DictReader(csvfile, delimiter=' ')
            for row in reader:
                if row['subject'] == subject:
                    amount_owed = row['amount']

        #final owed is a Dictcsv of Name, Amount Due. Takes amount_owed
        #and adds it to the person who was taught's final amount owed
        
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        fields = ['Name', 'amount_due']

        with open(final_owed, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, fieldnames=fields)
            writer = csv.DictWriter(tempfile, fieldnames=fields)
            for row in reader:
                if row['Name'] == full_name:
                    print('updating row', full_name)
                    row['amount_due'] = amount_owed
                row = {'Name': row['Name'], 'amount_due': row['amount_due']}
                writer.writerow(row)

        shutil.move(tempfile.name, final_owed)

discord_client.run('put token here')
