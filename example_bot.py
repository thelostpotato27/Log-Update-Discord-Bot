import discord
import csv
import pandas as pd
from discord.ext import commands
import shutil
from tempfile import NamedTemporaryFile


bot = commands.Bot(command_prefix='$')
discord_client = discord.Client()



class_logs = "temp"         #.csv file holding class_logs
logs_message = "temp"       #specific message that holds the class_logs file
final_owed = "temp"         #.csv file holding final amounts owed
final_owed_message = "temp" #specific message holding amount owed file

#On start, open recorded-logs channel and parse through messages, if message has an attachment with the 
#proper names, assign those attachments to a variable and print that the proper message has been found
@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))

    guild = discord_client.get_guild(861399632461299732)
    recorded_logs_channel = discord.utils.get(discord_client.get_all_channels(), guild__name=guild.name, name='recorded-logs')

    async for m in recorded_logs_channel.history(limit=100):
        if m.attachments != [] and m.attachments[0].filename == "class_logs.csv":
            class_logs = await m.attachments[0].read()
            class_logs = class_logs.decode("utf-8", "strict")
            logs_message = m
            print('class_logs found'.format(discord_client))

        if m.attachments != [] and m.attachments[0].filename == "name of final owed":
            final_owed = await m.attachments[0].read()
            final_owed = final_owed.decode("utf-8", "strict")
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
        first_name = words[1]
        last_name = words[2]
        subject = words[3]
        class_cost = "temp"                     #need to make a csv file to store the prices of certain class types

        #accessing .csv that holds prices of classes held in dict of subject, amount.
        #takes the subject of the class taught and returns the price of the class taught
        #class_cost csv file format is subject, amount
        amount_owed = 0
        with open(class_cost, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=' ')
            for row in reader:
                if row['subject'] == subject:
                    amount_owed = row['amount']

        #final owed is a Dictcsv of [First_name, Last_name, Amount Due]. Takes amount_owed
        #and adds it to the person who was taught's final amount owed.
        #Checks beforehand whether the name being queried exists or not.
        tempfile = NamedTemporaryFile(mode='w', delete=False)
        fields = ['First_name', 'Last_name', 'amount_due']
        with open(final_owed, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, fieldnames=fields)
            writer = csv.DictWriter(tempfile, fieldnames=fields)
            name_seen_flag = 0
            for row in reader:
                if row['First_name'] == first_name:
                    if row['Last_name'] == last_name:
                        print('updating row',full_name.format(discord_client))
                        row['amount_due'] += amount_owed
                        name_seen_flag = 1
                row = {'First_name': row['First_name'], 'Last_name': row['Last_name'], 'amount_due': row['amount_due']}
                writer.writerow(row)
            if not name_seen_flag:
                print("Name does not exist, please check for spelling mistakes. Potential names:".format(discord_client))
                #go through all names here and suggest names that either have the same first name spelling, same last name spelling, only have one letter mispelled,
                #or have the same first letter of first or last name and +-2 on the length of the first or last name
                for row in reader:
                    #prints name if same length and has 2 spelling mistakes or less
                    if first_name.len() == row['First_name'].len():
                        mispelled = 0
                        for i in range(first_name.len()):
                            if first_name[i] != row['First_name'][i]: mispelled += 1
                        if mispelled <= 2:
                            print(row['First_name'].format(discord_client))
                            print(row['Last_name'].format(discord_client))
                            continue
                    
                    if last_name.len() == row['Last_name'].len():
                        mispelled = 0
                        for i in range(last_name.len()):
                            if last_name[i] != row['Last_name'][i]: mispelled += 1
                        if mispelled <= 2:
                            print(row['First_name'].format(discord_client))
                            print(row['Last_name'].format(discord_client))
                            continue
                    
                    #prints name if have the same first starting letter and also have a name length difference of 2 or less
                    if first_name.len() >= row['First_name'].len()-1 or first_name.len() <= row['First_name'].len()+1:
                        if first_name[:1] == row['First_name'][:1]:
                            print(row['First_name'].format(discord_client))
                            print(row['Last_name'].format(discord_client))
                            continue

                    if last_name.len() >= row['Last_name'].len()-1 or last_name.len() <= row['Last_name'].len()+1:
                        if last_name[:1] == row['Last_name'][:1]:
                            print(row['First_name'].format(discord_client))
                            print(row['Last_name'].format(discord_client))
                            continue

                return
        shutil.move(tempfile.name, final_owed)
        await final_owed_message.edit(embed = final_owed)

        #writes row of data on class taught to csv file.
        with open(class_logs, 'w', newline='') as csvfile:      #.csv to hold classes held  
            csv_w_class_logs = csv.writer(csvfile, delimiter=' ')
            csv_w_class_logs.writerow([date] + [time] + [first_name] + [last_name] + [subject] + [amount_owed])
        await logs_message.edit(embed = class_logs)

discord_client.run('ODQyNTMxMDE3MzM2NDIyNDQw.GoZRHW.seoDOBKVNeW6dgC2PXsB4mbKi1-aDXSuxB7qFo')
