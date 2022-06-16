import discord
import csv
import pandas as pd
from discord.ext import commands
import shutil
import tempfile


bot = commands.Bot(command_prefix='$')

bot.class_logs = "temp"         #.csv file holding class_logs
bot.logs_message = "temp"       #specific message that holds the class_logs file
bot.final_owed = "temp"         #.csv file holding final amounts owed
bot.final_owed_message = "temp" #specific message holding amount owed file
bot.class_cost = "temp"         #.csv file holding class_cost list
bot.class_cost_message = "temp" #specific message holding class cost file
bot.recorded_logs_channel = "temp"  #channel with all stored .csv files


# internal class logs file, stored in .csv format. Instead of redownloading the .csv file to update it, the bot will download it once and
# maintain its internal copy. Whenever an update is made, the bot will replace the current .csv file with its current internal copy
bot.class_logs_internal = tempfile.NamedTemporaryFile(delete=False)


#On start, open recorded-logs channel and parse through messages, if message has an attachment with the 
#proper names, assign those attachments to a variable and print that the proper message has been found
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    guild = bot.get_guild(861399632461299732)
    bot.recorded_logs_channel = discord.utils.get(bot.get_all_channels(), guild__name=guild.name, name='recorded-logs')

    #The contents of the .csv files are stored as a huge string that will be parsed through later because I don't want to download the files locally.

    async for m in bot.recorded_logs_channel.history(limit=100):
        # class logs format is [date, time, first name, last name, subject, amount owed]
        if m.attachments != [] and m.attachments[0].filename == "class_logs.csv":
            temp_holder = await m.attachments[0].read()
            temp_holder = temp_holder.decode("utf-8", "strict")
            temp_holder = temp_holder.replace('\n', '')
            temp_holder = temp_holder.replace('\r', '')
            temp_holder = temp_holder.split(',')
            print("printing temp holder")
            print(temp_holder)
            class_logs_size = int(len(temp_holder)/6)
            bot.class_logs = ['temp'] * (class_logs_size)
            fields = ['date', 'time', 'first_name', 'last_name', 'subject', 'amount_owed']
            with open(bot.class_logs_internal.name, 'w') as class_log_csv:
                print("class logs file opened")
                class_logs_writer = csv.writer(class_log_csv)
                # class_logs_writer.writerow(fields)
                for i in range(class_logs_size):
                    starting_position = 6*i
                    bot.class_logs[i] = [temp_holder[starting_position], temp_holder[starting_position+1], temp_holder[starting_position+2],temp_holder[starting_position+3], temp_holder[starting_position+4], temp_holder[starting_position+5]]
                    new_row = [bot.class_logs[i][0], bot.class_logs[i][1], bot.class_logs[i][2], bot.class_logs[i][3], bot.class_logs[i][4], bot.class_logs[i][5]]
                    class_logs_writer.writerow(new_row)
                    print(new_row)
            # await bot.recorded_logs_channel.send(file = discord.File(bot.class_logs_internal.name, filename = 'class_logs_after.csv'))

            bot.logs_message = m
            print('class_logs found'.format(bot))
            print(bot.class_logs)

        # final owed format is [First_name, Last_name, Amount Due]
        if m.attachments != [] and m.attachments[0].filename == "final_owed.csv":
            temp_holder = await m.attachments[0].read()
            temp_holder = temp_holder.decode("utf-8", "strict")
            temp_holder = temp_holder.replace('\n', '')
            temp_holder = temp_holder.replace('\r', '')
            temp_holder = temp_holder.split(',')
            final_owed_size = int(len(temp_holder)/3)
            bot.final_owed = ['temp'] * (final_owed_size-1)
            for i in range(1, final_owed_size):
                starting_position = 3*i
                bot.final_owed[i-1] = [temp_holder[starting_position], temp_holder[starting_position+1], temp_holder[starting_position+2]]
            bot.final_owed_message = m
            print('final_owed found'.format(bot))
            print(bot.final_owed)
        
        # class cost format is [Subject, Amount]
        if m.attachments != [] and m.attachments[0].filename == "class_cost.csv":
            temp_cost = await m.attachments[0].read()
            temp_cost = temp_cost.decode("utf-8", "strict")
            temp_cost = temp_cost.replace('\n', '')
            temp_cost = temp_cost.replace('\r', '')
            temp_cost = temp_cost.split(',')
            bot.class_cost = temp_cost[2:]
            bot.class_cost_message = m
            print('class_cost found'.format(bot))
            print(bot.class_cost)
    print('Finished!'.format(bot))



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


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')



# test command understand how the bot.commands work, doesnt work for some reason
@bot.command()
async def test(ctx, arg1):
    print('running test command')
    await ctx.send(arg1)


@bot.command()
async def taught(ctx, first_name, last_name, subject, time, date):

    stop_command = 1
    print('command recieved'.format(bot))
    #checks that msg starts with $Taught
    #msg format is $Taught First_name Last_name subject time date

    full_name = first_name + '_' + last_name


    #accessing .csv that holds prices of classes held in dict of subject, amount.
    #takes the subject of the class taught and returns the price of the class taught
    #class_cost csv file format is [subject, amount]
    amount_owed = 0
    print("input subject is " + subject)
    for i in range(len(bot.class_cost)):
        print("Checked subject: " + bot.class_cost[i])
        if subject == bot.class_cost[i]:
            amount_owed = bot.class_cost[i + 1]
            break
    if amount_owed == 0:
        stop_command = 0
        print("Subject does not exist, possible subjects:")
        for elem in bot.class_cost:
            if subject[0] == elem[0]:
                print(elem)


    if stop_command:
        #final owed is a Dictcsv of [First_name, Last_name, Amount Due]. Takes amount_owed
        #and adds it to the person who was taught's final amount owed.
        #Checks beforehand whether the name being queried exists or not.
        temp_csv = tempfile.NamedTemporaryFile(delete=False)
        fields = ['First_name', 'Last_name', 'amount_due,']


        with open(temp_csv.name, 'w') as fake_csv:
            writer = csv.writer(fake_csv)
            writer.writerow(fields)
            name_seen_flag = 0
            print("First name inputed: ", end = '')
            print(first_name)
            print("Last name input: ", end = '')
            print(last_name)
            for row in bot.final_owed:
                print("Row in final owed:")
                print(row)
                print("row[0] is ", end = '')
                print(row[0])
                if row[0] == first_name:
                    if row[1] == last_name:
                        print('updating row',full_name.format(bot))
                        row[2] = int(amount_owed) + int(row[2])
                        name_seen_flag = 1
                new_row = [row[0], row[1], row[2]]
                writer.writerow(new_row)
        
        if name_seen_flag:
            # update 2D array class_logs and add a new row to the internal .csv file
            bot.class_logs.append([date, time, first_name , last_name, subject, amount_owed])
            new_row = [bot.class_logs[-1][0], bot.class_logs[-1][1], bot.class_logs[-1][2], bot.class_logs[-1][3], bot.class_logs[-1][4], bot.class_logs[-1][5]]
            print(new_row)
            # await bot.recorded_logs_channel.send(file = discord.File(bot.class_logs_internal.name, filename = 'class_logs_before_update.csv'))
            with open(bot.class_logs_internal.name, 'w') as class_log_csv:
                class_logs_writer = csv.writer(class_log_csv)
                class_logs_writer.writerow(new_row)
            # await bot.recorded_logs_channel.send(file = discord.File(bot.class_logs_internal.name, filename = 'class_logs_after_update.csv'))

        else:
            print("Name does not exist, please check for spelling mistakes. Potential names:".format(bot))
            #go through all names here and suggest names that either have the same first name spelling, same last name spelling, only have one letter mispelled,
            #or have the same first letter of first or last name and +-2 on the length of the first or last name
            for row in bot.final_owed:
                #prints name if same length and has 2 spelling mistakes or less
                if len(first_name) == len(row[0]):
                    mispelled = 0
                    for i in range(len(first_name)):
                        if first_name[i] != row[0][i]: mispelled += 1
                    if mispelled <= 2:
                        print(row[0].format(bot))
                        print(row[1].format(bot))
                        continue
                
                if len(last_name) == len(row[1]):
                    mispelled = 0
                    for i in range(len(last_name)):
                        if last_name[i] != row[1][i]: mispelled += 1
                    if mispelled <= 2:
                        print(row[0].format(bot))
                        print(row[1].format(bot))
                        continue
                
                #prints name if have the same first starting letter and also have a name length difference of 2 or less
                if len(first_name) >= len(row[0])-1 or len(first_name) <= len(row[0])+1:
                    if first_name[0] == row[0][0]:
                        print(row[0].format(bot))
                        print(row[1].format(bot))
                        continue

                if len(last_name) >= len(row[1])-1 or len(last_name) <= len(row[1])+1:
                    if last_name[0] == row[1][0]:
                        print(row[1].format(bot))
                        print(row[1].format(bot))
                        continue

            return

        # await bot.final_owed_message.edit(embed = tempfile) 
        # directory = fake_csv.gettempdir
        # print(directory)
        print(temp_csv.name)

        await bot.final_owed_message.delete()
        await bot.recorded_logs_channel.send(file = discord.File(temp_csv.name, filename = 'final_owed.csv'))


        # await bot.logs_message.delete()
        await bot.recorded_logs_channel.send(file = discord.File(bot.class_logs_internal.name, filename = 'class_logs_update.csv'))

        async for m in bot.recorded_logs_channel.history(limit=100):
            if m.attachments != [] and m.attachments[0].filename == "class_logs.csv":
                bot.logs_message = m
            if m.attachments != [] and m.attachments[0].filename == "final_owed.csv":
                bot.final_owed_message = m

bot.run('ODQyNTMxMDE3MzM2NDIyNDQw.GhNJJM.PH1jCMu058dvDUx2Zev1ijJFw7OYpYvAEe7QcE')