import discord
from discord.ext import commands
from discord.utils import get
import random
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pymongo
from pymongo import MongoClient

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds-sheet.json", scope)

gclient = gspread.authorize(creds)
sheet = gclient.open_by_key('1Q5IoaWo0YvdZFpO8sR2CIo2ZJNGkZwjsqStKg04gPo4').worksheet("Equipment")

client = commands.Bot(command_prefix='!')

cluster = MongoClient("mongodb+srv://Bad_Wolf:TZ8nRcNL0SskMvyb@dnd.y1p4h.gcp.mongodb.net/DnD?retryWrites=true&w=majority")
db = cluster["DnD"]
collection = db["Characters"]

@client.event
async def on_ready():
    print("I am ready")

@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "general": # We check to make sure we are sending the message in the general channel
            tour = client.get_channel(736472147773620224)
            await channel.send_message(f"""Welcome to the server {member.mention}. checkout {tour.mention} to get an idea of how this server works""")



bad_dice = ["hmmm.....this could be a problem","This hurts to watch","The force is not with this one","whelp...see you on the other side",
           "this isn't going to end well","oof, this wont be pretty","I know what this looks like. But I swear I'm not doing this on purpose",""]

perfect_dice = ["this....doesnt happen often","The Force is with this one","It seems I've been hacked","this gon be good"]


@client.command()
async def clear(ctx, amount = 3):
    await ctx.channel.purge(limit=amount)


@client.command(aliases=['roll','rolls','dice'])
async def roll_dice(ctx, dice):
    text_channel = client.get_channel(735915657610133614)
    flag = 0
    if (ctx.channel.id != 735915657610133614 and ctx.channel.id != 735874266389807124 and ctx.channel.id != 735842146564702218):
        await ctx.send(f"tsk..tsk..tsk\n why would your try to roll a dice here\n try{text_channel.mention} instead")
        return
    saving = ["strength","dexterity","wisdom","intelligence","charisma","constitution"]
    skills = ["acrobatics","animal handling","arcana","athletics","desception","history","insight","intimidation","investigation","medicine","nature","perception","performance","persuasion","religion","sleight","stealth","survival"]
    additive = 0
    if((dice in saving)or(dice in skills)or(dice=="initiative")):
        id = 7
        if(ctx.author.id == 400734279040237588):
            id = 0
        elif(ctx.author.id == 736599151164260444):
            id = 1
        elif(ctx.author.id == 736565980171468890):
            id = 2
        else:
            id = 3
        result = collection.find_one({"_id":id})
        if(dice in saving):
            additive = result["Saving Throws"][dice.capitalize()]
        elif(dice in skills):
            if(dice == "sleight"):
                dice = "sleight of hand"
            additive = result["Skills"][dice.capitalize()]
        else:
            additive = result["Initiative"]
        w = random.randint(1,20)
        await ctx.send(f"{str(ctx.author).split('#')[0]} rolled: {w}")
        await ctx.send(f"{ctx.author.mention}'s total is: {w + additive} with the bonus from {dice.capitalize()} = {additive}")
        if((w + additive)<=20*0.25):
            await ctx.send(random.choices(bad_dice)[0])
        if((w + additive) >= 20):
            await ctx.send(random.choices(perfect_dice)[0])
        return
    number_of_dice, value = dice.split('d')
    if('+' in value):
        value, additive = value.split('+')
    additive = int(additive)
    summ = 0
    if(int(number_of_dice) <= 0 or int(number_of_dice) >10 or int(value) not in [4,6,8,10,12,20,100]):
        await ctx.send("invalid input\n to roll a dice the format is xdy \n x is a number between 0 and 10\n y is 4 or 6 or 8 or 10 or 20 or 100")
        return
    w = random.randint(1,int(value))
    if(int(number_of_dice) == 1):
        await ctx.send(f"{ctx.author.mention} rolled: {w + additive} with bonus +{additive}")
        return
    await ctx.send(f"{ctx.author.mention} rolled: {w}")
    if(int(number_of_dice) > 1):
        for i in range(int(number_of_dice)-1):
            x = random.randint(1,int(value))
            summ += x
            await ctx.send(f"and: {x}")
        await ctx.send(f"{ctx.author.mention}'s total is: {summ + w + additive} with bonus +{additive}")
    summ = summ + w
    if(summ<=int(value)*int(number_of_dice)*0.25):
        await ctx.send(random.choices(bad_dice)[0])
    if(summ == int(value)*int(number_of_dice)):
        await ctx.send(random.choices(perfect_dice)[0])

@client.command()
async def my(ctx, *,com):

    if(ctx.author.id == 400734279040237588):
        id = 0
    elif(ctx.author.id == 736599151164260444):
        id = 1
    elif(ctx.author.id == 736565980171468890):
        id = 2
    else:
        id = 3
    if (ctx.channel.id != 765875748774215710 and ctx.channel.id != 765875818114318357 and ctx.channel.id != 765875858501271552 and ctx.channel.id != 765875918295269417):
        await ctx.send("try your personal channel")
        return
    result = collection.find_one({"_id":id})
    if(com == "spells"):
        all_spells = result["spells"]
        message = ""
        if(len(all_spells) == 1):
            message = all_spells[0]
        else:
            for element in all_spells:
                message = message + element + " , "
        await ctx.send(message[:-2])
    if(com == "abilities"):
        total_abilities = result["abilities"]
        message = []
        temp_message = ""
        for key in total_abilities.keys():
            temp = ""
            temp = temp + "**" + total_abilities[key]["name"] + "**\n"
            temp = temp + total_abilities[key]["description"] + "\n"
            if(len(temp_message + temp)>= 2000):
                message.append(temp_message[:-1])
                temp_message = temp
            else:
                temp_message = temp_message + temp
        message.append(temp_message[:-1])
        for element in message:
            await ctx.send(element)
    if(com == "weapons"):
        equipment = result["equipment"]
        message = ""
        for key in equipment.keys():
            if("weapon" in equipment[key]["tags"] and "damage" in equipment[key].keys()):
                print(equipment[key].keys())
                message = message + "**" + equipment[key]["name"] + "**\n" + "**Damage**:  "+equipment[key]["damage"] + "\n"
                if("notes" in equipment[key].keys()):
                    message = message + equipment[key]["notes"] + "\n"
        await ctx.send(message[:-1])


@client.command()
async def search(ctx, *,name):
    if(ctx.channel.id != 735874266389807124 and ctx.channel.id != 735934181632245911 and ctx.channel.id != 735842146564702218):
        await ctx.send(f"i cant do whatever you wants wherever you want. try this in {client.get_channel(735934181632245911).mention} instead")
        return
    name = ' '.join(name.split())
    spell_name = name.replace(' ','+').lower()
    link = "https://www.dnd5eapi.co/api/spells/?name="
    response = requests.get(link + spell_name)
    if(response.status_code == 404):
        await ctx.send("somethings not right....this is worrying")
    spell_names = response.json()
    count = spell_names["count"]
    spells = spell_names["results"]
    if(count == 0):
        await ctx.send("No spell seems to exist with those letters in that order. check your spelling or just use less words and letters")
        return
    actually_names = ""
    for i in range(count):
        actually_names = spells[i]["name"] + "\n" + actually_names
    await ctx.send("This are the spell i could find\n" + actually_names)

@client.command()
async def msearch(ctx, *,name):
    if(ctx.channel.id != 735842146564702218 and ctx.channel.id != 735874266389807124):
        await ctx.send(f"Only the Dungeon Master {client.get_channel(735874266389807124).mention} is entitled to this information\n YOU ARE UNWORTHY")
        return
    link = "https://www.dnd5eapi.co/api/monsters/?name="
    name = ' '.join(name.split())
    monster_name = name.replace(' ','+').lower()
    response = requests.get(link + monster_name)
    if(response.status_code == 404):
        await ctx.send("somethings not right....this is worrying")
    monster_names = response.json()
    count = monster_names["count"]
    monsters = monster_names["results"]
    if(count == 0):
        await ctx.send("No spell seems to exist with those letters in that order. check your spelling or just use less words and letters")
        return
    actually_names = ""
    for i in range(count):
        actually_names = monsters[i]["name"] + "\n" + actually_names
    await ctx.send("This are the monsters I could find\n" + actually_names)

@client.command(aliases=["monsters"])
async def monster(ctx, *,name):
    if(ctx.channel.id != 735842146564702218 and ctx.channel.id != 735874266389807124):
        await ctx.send(f"Only the Dungeon Master {client.get_channel(735874266389807124).mention} is privy to this information\n YOU ARE UNWORTHY")
        return
    link = "https://www.dnd5eapi.co/api/monsters/"
    name = ' '.join(name.split())
    monster_name = name.replace(' ','-').lower()
    response = requests.get(link + monster_name + '/')
    if(response.status_code == 404):
        await ctx.send("This monster is extinct")
    print(response.status_code)
    monster = response.json()
    monster_details = """ """
    profiencies = """ """
    abilities = """Actions: \n"""
    special_abilities = """ """
    legendary_abilities = """ """
    if("name" in monster.keys()):
        monster_details = monster_details + "**Name: **" +monster["name"] + "\n"
    if("size" in monster.keys()):
        monster_details = monster_details + "**Size: **" + monster["size"] + "\n"
    if("type" in monster.keys()):
        monster_details = monster_details + "**Type: **" + monster["type"] + "\n"
    if("alignment" in monster.keys()):
        monster_details = monster_details + "**Alignment: **" + monster["alignment"] + "\n"
    if("armor_class" in monster.keys()):
        monster_details = monster_details + "**Armour Class: **" + str(monster["armor_class"]) + "\n"
    if("hit_points" in monster.keys()):
        monster_details = monster_details + "**Hit Points: **" + str(monster["hit_points"]) + "\n"
    if("hit_dice" in monster.keys()):
        monster_details = monster_details + "**Hit Dice: **" + monster["hit_dice"] + "\n"
    if("speed" in monster.keys()):
        if type(monster["speed"]) is dict:
            monster_details = monster_details + "**Speed:**\n"
            if("walk" in monster["speed"].keys()):
                monster_details = monster_details + "     **Walk**:" + monster["speed"]["walk"] + "\n"
            if("fly" in monster["speed"].keys()):
                monster_details = monster_details + "     **Fly**:" + monster["speed"]["fly"] + "\n"
            if("swim" in monster["speed"].keys()):
                monster_details = monster_details + "     **Swim**:" + monster["speed"]["swim"] + "\n"
        else:
            monster_details = monster_details + "**Speed: **" + str(monster["speed"]) + "\n"
    if("strength" in monster.keys()):
        monster_details = monster_details + "**Strength: **" + str(monster["strength"]) + "\n"
    if("dexterity" in monster.keys()):
        monster_details = monster_details + "**Dexterity: **" + str(monster["dexterity"]) + "\n"
    if("constitution" in monster.keys()):
        monster_details = monster_details + "**Constitution: **" + str(monster["constitution"]) + "\n"
    if("intelligence" in monster.keys()):
        monster_details = monster_details + "**Intelligence: **" + str(monster["intelligence"]) + "\n"
    if("wisdom" in monster.keys()):
        monster_details = monster_details + "**Wisdom: **" + str(monster["wisdom"]) + "\n"
    if("charisma" in monster.keys()):
        monster_details = monster_details + "**Charisma: **" + str(monster["charisma"]) + "\n"
    if("proficiencies" in monster.keys()):
        if(type(monster["proficiencies"]) is list):
            profiencies = profiencies + "**Proficiencies: **\n"
            for pro in monster["proficiencies"]:
                if("name" in pro.keys()):
                    profiencies = profiencies +"     **Name:**" + pro["name"] + "\n"
                if("value" in pro.keys()):
                    profiencies = profiencies +"          **Value:**" + str(pro["value"]) + "\n"
        else:
            profiencies = profiencies + "**Proficiencies: **" + str(monster["proficiencies"]) + "\n"
    if("damage_vulnerabilities" in monster.keys()):
        if(type(monster["damage_vulnerabilities"]) is list):
            if(len(monster["damage_vulnerabilities"]) == 0):
                profiencies = profiencies + "**Damage Vulnerabilities: **" + "None" + "\n"
            else:
                profiencies = profiencies + "**Damage Vulnerabilities: **\n"
                for vulner in monster["damage_vulnerabilities"]:
                    profiencies = profiencies + vulner + "    "
                profiencies = profiencies + "\n"
        else:
            profiencies = profiencies + "**Damage Vulnerabilities: **" + str(monster["damage_vulnerabilities"]) + "\n"
    if("damage_resistances" in monster.keys()):
        if(type(monster["damage_resistances"]) is list):
            if(len(monster["damage_resistances"]) == 0):
                profiencies = profiencies + "**Damage Resistances: **" + "None" + "\n"
            else:
                profiencies = profiencies + "**Damage Resistances: **\n"
                for vulner in monster["damage_resistances"]:
                    profiencies = profiencies + vulner + "    "
                profiencies = profiencies + "\n"
        else:
            profiencies = profiencies + "**Damage Resistances: **" + str(monster["damage_resistances"]) + "\n"
    if("damage_immunities" in monster.keys()):
        if(type(monster["damage_immunities"]) is list):
            if(len(monster["damage_immunities"]) == 0):
                profiencies = profiencies + "**Damage Immunities: **" + "None" + "\n"
            else:
                profiencies = profiencies + "**Damage Immunities: **\n"
                for vulner in monster["damage_immunities"]:
                    profiencies = profiencies + vulner + "    "
                profiencies = profiencies + "\n"
        else:
            profiencies = profiencies + "**Damage Immunities: **" + str(monster["damage_immunities"]) + "\n"
    if("condition_immunities" in monster.keys()):
        if(type(monster["condition_immunities"]) is list):
            if(len(monster["condition_immunities"]) == 0):
                profiencies = profiencies + "**Condition Immunities: **" + "None" + "\n"
            else:
                profiencies = profiencies + "**Condition Immunities: **\n"
                for vulner in monster["condition_immunities"]:
                    profiencies = profiencies + vulner + "    "
                profiencies = profiencies + "\n"
        else:
            profiencies = profiencies + "**Condition Immunities: **" + str(monster["condition_immunities"]) + "\n"
    if("senses" in monster.keys()):
        if(type(monster["senses"]) is dict):
            profiencies = profiencies + "**Senses: **\n"
            for key in monster["senses"].keys():
                profiencies = profiencies + "     " + str(key) + ":" + str(monster["senses"][key]) + "\n"
        else:
            profiencies = profiencies + "**Senses: **" + str(monster["senses"]) + "\n"
    if("languages" in monster.keys()):
        profiencies = profiencies + "**Languages: **" + str(monster["languages"]) + "\n"
    if("challenge_rating" in monster.keys()):
        profiencies = profiencies + "**Challenge Rating: **" + str(monster["challenge_rating"]) + "\n"
    if("special_abilities" in monster.keys()):
        if(type(monster["special_abilities"]) is list):
            special_abilities = special_abilities +  "** Special Abilities: **\n"
            for element in monster["special_abilities"]:
                special_abilities = special_abilities + "\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\n"
                if(type(element) is dict):
                    for key in element.keys():
                        special_abilities = special_abilities + "    " + "**" + str(key) + ": **" + str(element[key]) + "\n"
                else:
                    special_abilities = special_abilities + "     " + str(element) + "\n"
        else:
            special_abilities = special_abilities + "**Special Abilities: **" + str(monster["special_abilities"]) + "\n"
    await ctx.send(monster_details)
    await ctx.send(profiencies)
    await ctx.send(special_abilities)
    if("actions" in monster.keys()):
        await ctx.send("**Actions: **\n\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\\n")
        for action in monster["actions"]:
            act = "     "
            if type(action) is dict:
                for key in action.keys():
                    act = act + "          **" + str(key) + ":**    " + str(action[key]) + "\n"
                await ctx.send(act)
            else:
                await ctx.send(str(action))

    if("legendary_actions" in monster.keys()):
        if(type(monster["legendary_actions"]) is list):
            legendary_abilities = legendary_abilities + "**Legendary Actions: **\n"
            for action in monster["legendary_actions"]:
                if type(action) is dict:
                    legendary_abilities = legendary_abilities + "\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\n"
                    for key in action.keys():
                        legendary_abilities = legendary_abilities + "      **" + str(key) + ":** " + str(action[key]) + "\n"
                else:
                    legendary_abilities = legendary_abilities + str(action) + "\n"
        else:
            legendary_abilities = legendary_abilities + "**Legendary Actions: **" + str(monster["legendary_actions"]) + "\n"

    await ctx.send(legendary_abilities)

@client.command(aliases=['spells'])
async def spell(ctx, *,name):
    text_channel = client.get_channel(735934181632245911)
    if (ctx.channel.id != 735934181632245911 and ctx.channel.id != 735874266389807124 and ctx.channel.id != 735842146564702218):
        await ctx.send(f"YOU DARE INQUIRE ABOUT THE INTRICACIES OF MAGIC HERE????\n you are hereby banished to {text_channel.mention} ")
        return
    name = ' '.join(name.split())
    spell_name = name.replace(' ','-').lower()
    link = "https://www.dnd5eapi.co/api/spells/"
    response = requests.get(link + spell_name + '/')
    if(response.status_code == 404):
        await ctx.send("the spell you seek does not exist... thats wierd\ncheck your spelling\nor ask your DM\n")
    print(response.status_code)
    spell_info = response.json()
    spell_details = " "
    name = "**Name:** "
    if("name" in spell_info.keys()):
        name = name + spell_info["name"]
    classes = "**Classes:** "
    if("classes" in spell_info.keys()):
        for i in range(len(spell_info["classes"])):
            classes = classes + " " + spell_info["classes"][i]["name"]
    components = "**Components:** "

    if("components" in spell_info.keys()):
        for i in range(len(spell_info["components"])):
            components = components + " " + spell_info["components"][i]
    materials = "**Material (if any):** "
    if("material" in spell_info.keys()):
        materials = materials + spell_info["material"]
    school = "**School**: "
    if("school" in spell_info.keys()):
        if(type(spell_info["school"]) is list):
            for item in spell_info["school"]:
                school = school + str(item["name"]) + " "
        else:
            school = school + spell_info["school"]["name"]
    description = "**Description**: "
    if("desc" in spell_info.keys()):
        if(type(spell_info["desc"]) is list):
            for element in spell_info["desc"]:
                description = description + element + "\n"
        else:
            description = description + spell_info["desc"]
    spell_details = name + "\n" + description + "\n" + school + "\n" + classes + "\n" + components + "\n" + materials + "\n"
    regulars = ["name","classes","components","material","school","desc","url","index","_id","subclasses"]
    for key in spell_info.keys():
        if(key not in regulars):
            spell_details = spell_details + "**" + str(key) + ":** " + str(spell_info[key]) + "\n"

    await ctx.send(spell_details)

def normalize(plat, gold, electrum, silver, copper):
    if(copper >= 10):
        silver = silver + copper//10
        copper = copper%10
    if(silver >= 5):
        electrum = electrum + silver//5
        silver = silver%5
    if(electrum >= 2):
        gold = gold + electrum//2
        electrum = electrum%2
    if(gold>=10):
        plat = plat + gold//10
        gold = gold%10
    return   plat, gold, electrum, silver, copper

@client.command()
async def deduct(ctx, *, amount):
    text_channel = client.get_channel(747102380235161650)
    if (ctx.channel.id != 735842146564702218 and ctx.channel.id != 747102380235161650):
        await ctx.send(f"I'm not gonna stop you but... you sure you wanna do this here??\n I mean the {text_channel.mention} may be safer\n")
        return
    if(ctx.author.id == 400734279040237588):
        row = 3
    if(ctx.author.id == 736599151164260444):
        row = 4
    if(ctx.author.id == 736595930333315173):
        row = 5
    if(ctx.author.id == 736565980171468890):
        row = 6
    current_plat = int(sheet.cell(row,2).value)
    current_gold = int(sheet.cell(row,3).value)
    current_electrum = int(sheet.cell(row,4).value)
    current_silver = int(sheet.cell(row,5).value)
    current_copper = int(sheet.cell(row,6).value)
    current_plat, current_gold, current_electrum, current_silver, current_copper = normalize(current_plat, current_gold, current_electrum, current_silver, current_copper)
    await ctx.send(f"{ctx.author.mention}'s' current balance is:\t {current_plat}tp  {current_gold}gp  {current_electrum}ep  {current_silver}sp  {current_copper}cp")
    amount = amount.lower()
    amount = amount.replace(" ","")
    amt = amount.split('p')
    amt.remove('')
    deduct_plat = 0
    deduct_gold = 0
    deduct_electrum = 0
    deduct_silver = 0
    deduct_copper = 0
    proper = ['t','g','e','s','c']
    total = []
    for element in amt:
        total.append(element[-1])
        if(element[-1] not in proper):
            await ctx.send("I haven't seen this type of metal here before, u sure you wanna use this? Maybe try tp, gp, ep, sp, or cp, we cant accept this\n" + str(amount))
            return
    temp = ""
    for element in total:
        temp = element + "p, "
    if len(total) != len(set(total)):

        await ctx.send("please collect all pieces of the same type and try again. this... "+ temp +" wont do")
        return
    del temp

    for element in amt:
        if(element[-1] == 't'):
            deduct_plat = int(element[:-1])
        if(element[-1] == 'g'):
            deduct_gold = int(element[:-1])
        if(element[-1] == 'e'):
            deduct_electrum = int(element[:-1])
        if(element[-1] == 's'):
            deduct_silver = int(element[:-1])
        if(element[-1] == 'c'):
            deduct_copper = int(element[:-1])
    total_deduct = deduct_plat*1000 + deduct_gold*100 + deduct_electrum*50 + deduct_silver*10 + deduct_copper
    total_current = current_plat*1000 + current_gold*100 + current_electrum*50 + current_silver*10 + current_copper
    if(total_deduct > total_current):
        await ctx.send("you dont have enough pieces for the transaction")
        return
    current_plat = current_plat-deduct_plat
    current_gold = current_gold-deduct_gold
    current_silver = current_silver-deduct_silver
    current_electrum = current_electrum-deduct_electrum
    current_copper = current_copper-deduct_copper
    if(current_plat<0):
        await ctx.send("somethings gone wrong. you've run out of platinum. please try again with a lower amount maybe")
        return
    if(current_gold<0):
        current_gold = current_gold+current_plat*10
        current_plat = 0
    if(current_electrum<0):
        current_electrum = current_electrum+ current_gold*2+current_plat*20
        current_gold = 0
        current_plat = 0
    if(current_silver<0):
        current_silver = current_silver + current_electrum*5 +current_gold*10 + current_plat*100
        current_electrum = 0
        current_gold = 0
        current_plat = 0
    if(current_copper<0):
        current_copper = current_plat*1000 + current_gold*100 + current_electrum*50 + current_silver*10 + current_copper
        current_silver = 0
        current_electrum = 0
        current_gold = 0
        current_plat = 0
    current_plat, current_gold, current_electrum, current_silver, current_copper = normalize(current_plat, current_gold, current_electrum, current_silver, current_copper)
    cell_list = "B"+str(row)+":F"+str(row)
    sheet.update(cell_list, [[current_plat, current_gold, current_electrum, current_silver, current_copper]])
    await ctx.send(f"{ctx.author.mention}'s' new balance is:\t {current_plat}tp  {current_gold}gp  {current_electrum}ep  {current_silver}sp  {current_copper}cp")

@client.command()
async def balance(ctx):
    text_channel = client.get_channel(747102380235161650)
    if (ctx.channel.id != 735842146564702218 and ctx.channel.id != 747102380235161650):
        await ctx.send(f"I'm not gonna stop you but... you sure you wanna announce your wealh here??\n I mean the {text_channel.mention} was made for this\n")
        return
    if(ctx.author.id == 400734279040237588):
        row = 3
    if(ctx.author.id == 736599151164260444):
        row = 4
    if(ctx.author.id == 736595930333315173):
        row = 5
    if(ctx.author.id == 736565980171468890):
        row = 6
    current_plat = int(sheet.cell(row,2).value)
    current_gold = int(sheet.cell(row,3).value)
    current_electrum = int(sheet.cell(row,4).value)
    current_silver = int(sheet.cell(row,5).value)
    current_copper = int(sheet.cell(row,6).value)
    current_plat, current_gold, current_electrum, current_silver, current_copper = normalize(current_plat, current_gold, current_electrum, current_silver, current_copper)
    await ctx.send(f"{ctx.author.mention}'s' current balance is:\t {current_plat}tp  {current_gold}gp  {current_electrum}ep  {current_silver}sp  {current_copper}cp")


@client.command()
async def add(ctx, *,amount):
    text_channel = client.get_channel(747102380235161650)
    if (ctx.channel.id != 735842146564702218 and ctx.channel.id != 747102380235161650):
        await ctx.send(f"I dont think you can do that here. you're free to try but dont look at me when you loose your money.\n You could try the {text_channel.mention} though\n")
        return
    if(ctx.author.id == 400734279040237588):
        row = 3
    if(ctx.author.id == 736599151164260444):
        row = 4
    if(ctx.author.id == 736595930333315173):
        row = 5
    if(ctx.author.id == 736565980171468890):
        row = 6
    current_plat = int(sheet.cell(row,2).value)
    current_gold = int(sheet.cell(row,3).value)
    current_electrum = int(sheet.cell(row,4).value)
    current_silver = int(sheet.cell(row,5).value)
    current_copper = int(sheet.cell(row,6).value)
    current_plat, current_gold, current_electrum, current_silver, current_copper = normalize(current_plat, current_gold, current_electrum, current_silver, current_copper)
    await ctx.send(f"{ctx.author.mention}'s' current balance is:\t {current_plat}tp  {current_gold}gp  {current_electrum}ep  {current_silver}sp  {current_copper}cp")
    amount = amount.lower()
    amount = amount.replace(" ","")
    amt = amount.split('p')
    added_plat = 0
    added_gold = 0
    added_electrum = 0
    added_silver = 0
    added_copper = 0
    proper = ['t','g','e','s','c']
    total = []
    amt.remove('')
    for element in amt:
        total.append(element[-1])
        if(element[-1] not in proper):
            await ctx.send("I haven't seen this type of metal here before, u sure you wanna use this? Maybe try tp, gp, ep, sp, or cp, we cant accept this\n" + str(amount))
            return
    temp = ""
    for element in total:
        temp = element + "p, "
    if len(total) != len(set(total)):

        await ctx.send("please collect all peices of the same type and try again. this... "+ temp +" wont do")
        return
    del temp

    for element in amt:
        if(element[-1] == 't'):
            added_plat = int(element[:-1])
        if(element[-1] == 'g'):
            added_gold = int(element[:-1])
        if(element[-1] == 'e'):
            added_electrum = int(element[:-1])
        if(element[-1] == 's'):
            added_silver = int(element[:-1])
        if(element[-1] == 'c'):
            added_copper = int(element[:-1])

    str_cell_list = "B"+str(row)+":F"+str(row)

    current_plat, current_gold, current_electrum, current_silver, current_copper = normalize(current_plat + added_plat, current_gold + added_gold,
                                                                                    current_electrum + added_electrum, current_silver + added_silver, current_copper + added_copper)
    sheet.update(str_cell_list,[[current_plat, current_gold, current_electrum, current_silver, current_copper]])
    await ctx.send(f"{ctx.author.mention}'s' new balance is:\t {current_plat}tp  {current_gold}gp  {current_electrum}ep  {current_silver}sp  {current_copper}cp")

client.run('NzM1NDEzODM1NTM5Njc3MTk1.XxgN8g.neohegKKIsadhFT6UgFp8YMsdR4')
