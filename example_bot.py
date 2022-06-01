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
class_cost = "temp"         #.csv file holding class_cost list
class_cost_message = "temp" #specific message holding class cost file


# internal class logs file, stored in .csv format. Instead of redownloading the .csv file to update it, the bot will download it once and
# maintain its internal copy. Whenever an update is made, the bot will replace the current .csv file with its current internal copy
class_logs_internal = NamedTemporaryFile(mode='w', delete=False)
fields = ['date', 'time', 'first_name', 'last_name', 'subject', 'amount_owed']
class_logs_writer = csv.DictWriter(class_logs_internal, fieldnames=fields)

#On start, open recorded-logs channel and parse through messages, if message has an attachment with the 
#proper names, assign those attachments to a variable and print that the proper message has been found
@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))

    guild = discord_client.get_guild(861399632461299732)
    recorded_logs_channel = discord.utils.get(discord_client.get_all_channels(), guild__name=guild.name, name='recorded-logs')

    #The contents of the .csv files are stored as a huge string that will be parsed through later because I don't want to download the files locally.

    async for m in recorded_logs_channel.history(limit=100):
        # class logs format is [date, time, first name, last name, subject, amount owed]
        if m.attachments != [] and m.attachments[0].filename == "class_logs.csv":
            temp_holder = await m.attachments[0].read()
            temp_holder = temp_holder.decode("utf-8", "strict")
            temp_holder = temp_holder.replace('\n', '')
            temp_holder = temp_holder.replace('\r', '')
            temp_holder = temp_holder.split(',')
            class_logs_size = int(len(temp_holder)/6)
            class_logs = ['temp'] * (class_logs_size-1)
            for i in range(1, class_logs_size):
                starting_position = 6*i
                class_logs[i-1] = [temp_holder[starting_position], temp_holder[starting_position+1], temp_holder[starting_position+2],temp_holder[starting_position+3], temp_holder[starting_position+4], temp_holder[starting_position+5]]
                new_row = {'date': class_logs[i-1][0], 'time': class_logs[i-1][1], 'first_name': class_logs[i-1][2], 'last_name': class_logs[i-1][3], 'subject': class_logs[i-1][4], 'amount_owed': class_logs[i-1][5]}
                class_logs_writer.writerow(new_row)

            logs_message = m
            print('class_logs found'.format(discord_client))
            print(class_logs)

        # final owed format is [First_name, Last_name, Amount Due]
        if m.attachments != [] and m.attachments[0].filename == "final_owed.csv":
            temp_holder = await m.attachments[0].read()
            temp_holder = temp_holder.decode("utf-8", "strict")
            temp_holder = temp_holder.replace('\n', '')
            temp_holder = temp_holder.replace('\r', '')
            temp_holder = temp_holder.split(',')
            final_owed_size = int(len(temp_holder)/3)
            final_owed = ['temp'] * (final_owed_size-1)
            for i in range(1, final_owed_size):
                starting_position = 3*i
                final_owed[i-1] = [temp_holder[starting_position], temp_holder[starting_position+1], temp_holder[starting_position+2]]
            final_owed_message = m
            print('final_owed found'.format(discord_client))
            print(final_owed)
        
        # class cost format is [Subject, Amount]
        if m.attachments != [] and m.attachments[0].filename == "class_cost.csv":
            class_cost = await m.attachments[0].read()
            class_cost = class_cost.decode("utf-8", "strict")
            class_cost = class_cost.replace('\n', '')
            class_cost = class_cost.replace('\r', '')
            class_cost = class_cost.split(',')
            class_cost = class_cost[2:]
            class_cost_message = m
            print('class_cost found'.format(discord_client))
            print(class_cost)
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


# test command understand how the bot.commands work, doesnt work for some reason
@bot.command()
async def test(ctx, arg1):
    await ctx.send(arg1)


@bot.command()
async def taught(ctx, first_name, last_name, subject, time, date):

    stop_command = 1
    print('command recieved'.format(discord_client))
    #checks that msg starts with $Taught
    #msg format is $Taught First_name Last_name subject time date

    full_name = first_name + '_' + last_name


    #accessing .csv that holds prices of classes held in dict of subject, amount.
    #takes the subject of the class taught and returns the price of the class taught
    #class_cost csv file format is [subject, amount]
    amount_owed = 0
    for i in range(len(class_cost)):
        if subject == class_cost[i]:
            amount_owed = class_cost[i + 1]
            break
    if amount_owed == 0:
        stop_command = 0
        print("Subject does not exist, possible subjects:")
        for elem in class_cost:
            if subject[0] == elem[0]:
                print(elem)


    if stop_command:
        #final owed is a Dictcsv of [First_name, Last_name, Amount Due]. Takes amount_owed
        #and adds it to the person who was taught's final amount owed.
        #Checks beforehand whether the name being queried exists or not.
        tempfile = NamedTemporaryFile(mode='w', delete=False)
        fields = ['First_name', 'Last_name', 'amount_due']

        writer = csv.DictWriter(tempfile, fieldnames=fields)
        name_seen_flag = 0
        for row in final_owed:
            if row[0] == first_name:
                if row[1] == last_name:
                    print('updating row',full_name.format(discord_client))
                    row[2] += amount_owed
                    name_seen_flag = 1
            new_row = {'First_name': row[0], 'Last_name': row[1], 'amount_due': row[2]}
            writer.writerow(new_row)
        if name_seen_flag:
            # update 2D array class_logs and add a new row to the internal .csv file
            class_logs.append([date, time, first_name , last_name, subject, amount_owed])
            new_row = {'date': class_logs[-1][0], 'time': class_logs[-1][1], 'first_name': class_logs[-1][2], 'last_name': class_logs[-1][3], 'subject': class_logs[-1][4], 'amount_owed': class_logs[-1][5]}
            class_logs_writer.writerow(new_row)
        else:
            print("Name does not exist, please check for spelling mistakes. Potential names:".format(discord_client))
            #go through all names here and suggest names that either have the same first name spelling, same last name spelling, only have one letter mispelled,
            #or have the same first letter of first or last name and +-2 on the length of the first or last name
            for row in final_owed:
                #prints name if same length and has 2 spelling mistakes or less
                if first_name.len() == row[0].len():
                    mispelled = 0
                    for i in range(first_name.len()):
                        if first_name[i] != row[0][i]: mispelled += 1
                    if mispelled <= 2:
                        print(row[0].format(discord_client))
                        print(row[1].format(discord_client))
                        continue
                
                if last_name.len() == row[1].len():
                    mispelled = 0
                    for i in range(last_name.len()):
                        if last_name[i] != row[1][i]: mispelled += 1
                    if mispelled <= 2:
                        print(row[0].format(discord_client))
                        print(row[1].format(discord_client))
                        continue
                
                #prints name if have the same first starting letter and also have a name length difference of 2 or less
                if first_name.len() >= row[0].len()-1 or first_name.len() <= row[0].len()+1:
                    if first_name[0] == row[0][0]:
                        print(row[0].format(discord_client))
                        print(row[1].format(discord_client))
                        continue

                if last_name.len() >= row[1].len()-1 or last_name.len() <= row[1].len()+1:
                    if last_name[0] == row[1][0]:
                        print(row[1].format(discord_client))
                        print(row[1].format(discord_client))
                        continue

            return
        # shutil.move(tempfile.name, final_owed)
        await final_owed_message.edit(embed = tempfile)
        await logs_message.edit(embed = class_logs_internal)


discord_client.run('token')
