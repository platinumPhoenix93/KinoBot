import discord
import os
import re
import datetime
import pytz
import random
import requests
import urllib.request
import json
import emoji
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
my_secret = os.environ.get("TOKEN")
print(my_secret)
defaultHour = 20
defaultMinute = 30

r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

fileList = ["emojiRecover.txt", "films.txt", "recover.txt", "usedEmoji.txt", "savedMessages.txt","config.txt"]
memeList = ["Paul Masson's Pro Wine Taster 1980", "Flight Plan Simulator (CIA Edition)",
            "Huey Lewis and the News while putting on a raincoat", "Five Nights at Freddy Got Fingered",
            "Among Us (in Antarctica)", "King Kong vs. Godzilla vs. Marvel vs. Capcom", "Reservoir Petz: Dogz",
            "Spiderman 2 (PS2)", "Robot Jox: The Video Game"]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=random.choice(memeList)))
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    id = str(message.guild.id)
    filepath = "servers/" + id + "/"

    if message.author == client.user:

        if message.content.startswith("Films: "):
            await reactWithAllEmoji(message, filepath)
        return

    await checkFilesExist(message, filepath)
   

    if message.content.startswith('!nominate'):
        await nominate(message, filepath)

    if message.content.startswith('!movieLink'):
        await movieLink(message, filepath)

    if message.content.startswith('!champagne'):
        await message.channel.send("https://www.youtube.com/watch?v=Nvxwf1jxdaM")

    if message.content.startswith('!printFilms'):
        print(filepath)
        f = open(filepath + "films.txt", 'r')
        movieNum = 1
        i = 0
        filmList = ""
        for line in f:
            if(i % 2 == 0):
                filmList = filmList + str(movieNum) + ". " + line
                movieNum = movieNum + 1
            else:
                filmList = filmList + line
            i = i + 1
        f.close()
        
        await message.channel.send(filmList)
        
    if message.content.startswith('!kinoHelp'):
        await PrintHelp(message)

    if message.content.startswith('!startVote'):
        await startVote(message, filepath)

    if message.content.startswith('!emoji'):
        f = open("usedEmoji.txt")

        currentEmoji = f.readline()
        emojiList = []

        while (currentEmoji):
            emojiList.append(currentEmoji.rstrip())
            currentEmoji = f.readline()

        await message.channel.send("Emoji currently in use: \n\n" + str(emojiList))

    if message.content.startswith('!purge'):

        user = message.author
        roles = user.roles

        # Check user has corret permissions
        for role in roles:
            if role.name == "Keeper of the List":
                await purgeLists(filepath)
                await message.channel.send(
                    user.name + '#' + user.discriminator + " has purged the film list. If this was a mistake please type !recover")
                return

        await message.channel.send("Insufficient permissions to purge list.")
        
        
    if message.content.startswith('!callVote'):
        await callVote(filepath, message)
        
    if message.content.startswith('!remove'):
        await remove(filepath, message)
        
    #Trollface    
    if message.content.startswith('!CallVotes'):
        await message.channel.send("Error...winning film is film for children.\n\nRecalculating...\n\nAnother Round (film) 🍹\n🍹")


def findTitle(url):
    webpage = urllib.request.urlopen(url).read()
    title = str(webpage).split('<title>')[1].split('</title>')[0].split(" - Wikipedia")[0]
    return title


async def nominate(message, filepath):
    txt = str(message.content)
    textlist = re.split(" ", txt)

    f = open(filepath + "usedEmoji.txt", "r")

    for line in f:
        if textlist[2] in line:
            await message.channel.send("Emoji already in use: " + textlist[2] + "\nPlease select another")
            return

    if "wikipedia" not in textlist[1]:
        await message.channel.send("")

    if (await MovieIsValid(textlist, message, filepath)):
        title = findTitle(textlist[1])
        nominationEmoji = emoji.emojize(textlist[2])
        url = "<" + textlist[1] + ">"
        
        lineOne = title + " " + nominationEmoji
        f = open(filepath + "films.txt", 'a')

        f.write(lineOne + "\n")
        f.write(url + "\n")
        f.close()

        f = open(filepath + "usedEmoji.txt", 'a')
        f.write(nominationEmoji + "\n")
        f.close()

        await message.channel.send(title + " added with the emoji " + nominationEmoji)

    else:
        await message.channel.send("Movie already added, dumb idiot")


async def movieLink(message, filepath):
    # takes a string of the form !movieLink [filmId] [film link] [time]
    # currently only works for today, or tomorrow
    # no error checking on whether the film or time exists
    txt = str(message.content)
    textlist = re.split(" ", txt)

    lines = open(filepath + "films.txt").readlines()
    filmName = lines[(int(textlist[1]) - 1) * 2]

    hour = defaultHour
    minute = defaultMinute
    if len(textlist) > 3:
        timeList = re.split(":", textlist[3])
        hour = int(timeList[0])
        minute = int(timeList[1])

    movieTime = datetime.datetime.now(pytz.timezone('Europe/London')).replace(hour=hour, minute=minute, second=0)

    seconds = (movieTime - datetime.datetime.now(pytz.timezone('Europe/London'))).seconds

    await message.channel.send(
        "@here\nWhat: " + filmName + "When: Tonight, " + movieTime.strftime("%I:%M%p ") + "(" + str(
            seconds // 3600) + " hours and " + str(seconds % 3600 // 60) + " minutes from now)" + "\nHow: " + textlist[
            2])


async def MovieIsValid(textlist, message, filepath):
    f = open(filepath + "films.txt", 'r')
    url = textlist[1]
    print(url)
    line = f.readline()

    while line:
        print(line)

        if (str.rstrip(line) == str(url)):
            return False

        line = f.readline()

    return True

async def PrintHelp(message):
    await message.channel.send("")

async def reactWithAllEmoji(message, filepath):
    f = open(filepath + "usedEmoji.txt", 'r')

    line = f.readline()
    currentEmoji = str.rstrip(line)

    while line:
        print(line)
        await message.add_reaction(currentEmoji)

        line = f.readline()
        currentEmoji = str.rstrip(line)


# Copies the contents of films.txt and usedEmoji.txt to recovery files and clears their content.
async def purgeLists(filepath):
    # Clear the recovery file of any previous content
    open(filepath + "recover.txt", 'w').close()

    # Write the contents of films.txt to the recovery file
    with open(filepath + 'films.txt', 'r') as original, open(filepath + 'recover.txt', 'a') as backup:
        for line in original:
            backup.write(line)

    original.close()
    backup.close()

    # Clear films list
    open(filepath + "films.txt", 'w').close()
    open(filepath + 'emojiRecover.txt', 'w').close()

    # Copy contents of usedEmoji to emojiRecover
    with open(filepath + 'usedEmoji.txt', 'r') as original, open(filepath + 'emojiRecover.txt', 'a') as backup:
        for line in original:
            backup.write(line)

    original.close()
    backup.close()

    # Clear contents of used emoji
    open(filepath + "usedEmoji.txt", 'w').close()


async def checkFilesExist(message, filepath):
    if not os.path.exists(filepath):
        print("not found")
        await message.channel.send("New server detected, creating files...")
        os.makedirs(filepath)
    else:
        print("found")

    for fileName in fileList:
        file = filepath + fileName
        if (not os.path.exists(file)):
            f = open(file, 'w+')
            f.close()


async def startVote(message, filepath):

    await message.channel.send("@here Voting begins now, voting will end on Saturday at 3pm")
    
    f = open(filepath + "films.txt", 'r')
    movieNum = 1
    i = 0
    filmList = ""
    for line in f:
        if(i % 2 == 0):
            filmList = filmList + str(movieNum) + ". " + line
            movieNum = movieNum + 1
        else:
            filmList = filmList + line
        i = i + 1
    f.close()
        
    lastMessage = await message.channel.send("Films: \n" + filmList)
    print(str(lastMessage.id))
    f = open(filepath + "config.txt",'w+')
    f.write(str(lastMessage.id))
    f.close()
    # make this save the id to a file with the identifer lastVote

async def callVote(filepath, message):
    
    highestReactNum = 0
    
    f = open(filepath + "config.txt",'r')
    id = f.read()
    f.close()
    
    msg = await message.channel.fetch_message(id)
    reactions = msg.reactions
    
    for reaction in reactions:
       if reaction.count > highestReactNum:
        highestReactNum = reaction.count
        
    winningNoms = []
        
    for reaction in reactions:
        if (reaction.count == highestReactNum):
            winningNoms.append(reaction)
    
    winner = random.choice(winningNoms)
    
    f = open(filepath + "films.txt")
    
    nomination = f.readline()
    
    while(nomination):
        if (str(winner) in nomination):
            await message.channel.send(nomination)
            break
            
        nomination = f.readline()
    
    await message.channel.send(winner)
    
async def remove(filepath, message):
    
    try:
        msgString = message.content
        delete = int (msgString)
        print(str(delete))
        
    except ValueError:
        await message.channel.send("Please enter an integer")

client.run(my_secret)

# TODO: Call won movie
#       Remove movie when it has won
#       Manually remove movie
#       Manually call winner if different
#       Feed it a mega link and have it print out the 'What when how message'
#       Purge entire list
#       !help function
#       user role permissions? - Partially implemented
#       recover past list after purge
#       watch history?? (nice to have)
#       Random emoji selected if user does not use one in nomination
#       allow users to set custom emoji, add them to a txt file
#       Save file for mega link, date/time? Useful if bot goes down for any reason, just load back from file.

#       command to link back to the message ID of the current vote, might want to save this when it's posted
#       grab  list of voters at time of locking in the winner, command to show list of them and have orson yell at specific ones
