import discord
from discord.ext import commands
import time
import asyncio
# from nltk.stem.snowball import SnowballStemmer

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='$')
bot.general_channel = None
bot.giver = None
bot.word = None
bot.guess = None
bot.active_clues = []   #Contains list of cluer and clue
bot.used_words = set()
bot.num_contacts = 3
bot.countdown = 12
bot.state = 'clueing'
bot.contacted_clue = None
bot.valid_words = []

class Clue:
	def __init__(self,cluer,clue,word):
		self.cluer    = cluer
		self.clue     = clue 
		self.word     = word
		self.contacts = dict()
		self.timestamp = time.time()
	def __str__(self):
		return ' '.join(self.clue) + "\nGiven by {}".format(self.cluer) + '\n and has {} contacts'.format(len(self.contacts))

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	bot.loop.create_task(check_contact())
	bot.valid_words = open("Words.txt").read().lower().split('\n')
async def check_contact():
	while True:
		if bot.state == 'clueing' or bot.contacted_clue is None:
			bot.countdown = 12
			bot.contacted_clue = None
			await asyncio.sleep(2)
		else:
			if bot.countdown > 0:
				bot.countdown -= 2
				await bot.general_channel.send("Countdown running for clue {}.\n TIK TIK {}".format(bot.contacted_clue,bot.countdown))
				await asyncio.sleep(2)
			else:
				correct = True
				contacted_clue = bot.contacted_clue
				embed = discord.Embed(title="Guesses for clue {}".format(contacted_clue))
				for con in bot.active_clues[int(contacted_clue)-1].contacts.keys():
					embed.add_field(name=con,value=bot.active_clues[int(contacted_clue)-1].contacts[con])
					bot.used_words.add(bot.active_clues[int(contacted_clue)-1].contacts[con])
					correct = correct and (bot.active_clues[int(contacted_clue)-1].contacts[con] == bot.active_clues[int(contacted_clue)-1].word)
				bot.used_words.add(bot.active_clues[int(contacted_clue)-1].word)
				embed.add_field(name="Actual Word",value=bot.active_clues[int(contacted_clue)-1].word)
				await bot.general_channel.send(embed=embed)
				bot.state = 'clueing'
				bot.countdown = 12
				if correct:
					bot.active_clues = []
					bot.guess = bot.word[:len(bot.guess)+1]
					await bot.general_channel.send("{} failed to guess! Current guess is {}".format(bot.giver,bot.guess))
				else:
					bot.active_clues.pop(int(contacted_clue)-1)
					await bot.general_channel.send("All guesses don't match! Tough one")
				if bot.word in bot.used_words:
					giver = bot.giver
					bot.giver = None
					bot.word = None
					bot.guess = None
					bot.active_clues = []   #Contains list of cluer and clue
					bot.used_words = set()
					bot.num_contacts = 3
					bot.countdown = 12
					bot.state = 'clueing'
					bot.contacted_clue = None
					bot.valid_words = []
					await bot.general_channel.send("And {}'s word was {}! GG! ".format(giver,bot.word))                                 


@bot.command()
async def user(ctx):
	if ctx.message.channel.type == "private":
		await ctx.send(ctx.author)
	else:
		await ctx.send("Not in public!")

@bot.command()
async def start(ctx,num_players=3):
	if ctx.message.channel.type == "private":
		await ctx.send("It takes more than 2 to Tango!")
	else:
		bot.general_channel = ctx.message.channel 
		bot.giver = None
		bot.word = None
		bot.guess = None
		bot.active_clues = []   
		bot.used_words = set()
		bot.num_contacts = num_players
		bot.countdown = 15
		bot.state = 'clueing'
		bot.contacted_clue = None

		await ctx.send("Starting on this channel with {} contacts and countdown of {} ".format(bot.num_contacts,bot.countdown))

@bot.command()
async def word(ctx,prop_word):
	# print(ctx.message.channel.type, type(ctx.message.channel.type))
	if not isinstance(ctx.message.channel,discord.DMChannel):
		await ctx.send("DM me to give a word!")
	elif bot.word is not None:
		await ctx.send("Word is already in play")
	elif bot.general_channel is None:
		await ctx.send("No games running currently. You can start a game by sending '$start' on a shared channel")
	elif prop_word.lower() not in bot.valid_words:
		await ctx.send("This is not a word")
	else:
		bot.word  = prop_word.lower()
		bot.giver = ctx.author
		bot.guess = prop_word[:1]
		await bot.general_channel.send("Word given by {}. \n Current guess - {}".format(bot.giver,bot.guess))

@bot.command()
async def clue(ctx,word,*args):
	word = word.lower()
	#TODO uncomment lines below
	if bot.giver == ctx.author:
		await ctx.send("You can't clue on your own word!")
	elif not isinstance(ctx.message.channel,discord.DMChannel):
		await ctx.send("DM me to give a clue!")
	elif bot.word is None:
		await ctx.send("No word in play")
	elif bot.general_channel is None:
		await ctx.send("No games running currently. You can start a game by sending '$start' on a shared channel")
	elif len(args) == 0:
		await ctx.send("Enter a clue please...")
	elif bot.guess != word[:len(bot.guess)]:
		await ctx.send("The word does not match current guess")
	elif word in bot.used_words:
		await ctx.send("Word already used")
	elif word.lower() not in bot.valid_words:
		await ctx.send("This is not a word")
	else:
		bot.active_clues.append(Clue(ctx.author,args,word))
		embed = discord.Embed(title="Active clues")
		for i in range(len(bot.active_clues)):
			embed.add_field(name="{}.".format(i+1),value=str(bot.active_clues[i]),inline=False)
		await bot.general_channel.send(embed=embed)

@bot.command()
async def guess(ctx,clue,word):
	if bot.giver != ctx.author:
		await ctx.send("Only word giver can guess for clues. Use $contact instead")
	elif int(clue) > len(bot.active_clues):
		await ctx.send("Enter a valid clue number")

	else:
		word = word.lower()
		bot.used_words.add(word)
		message = "{} has guessed {} for clue {} ".format(ctx.author,word,clue)
		if bot.active_clues[int(clue)-1].word == word:
			bot.active_clues.pop(int(clue)-1)
			if bot.word == word:
				giver = bot.giver
				bot.giver = None
				bot.word = None
				bot.guess = None
				bot.active_clues = []   #Contains list of cluer and clue
				bot.used_words = set()
				bot.num_contacts = 3
				bot.countdown = 12
				bot.state = 'clueing'
				bot.contacted_clue = None
				bot.valid_words = []
				await bot.general_channel.send("And {}'s word was {}! GG! ".format(giver,word))             
			elif bot.state=='countdown' and clue == bot.contacted_clue:
				bot.contacted_clue = None
				bot.state = 'clueing'
				bot.countdown = 12
				# print("HURRAH")
			message += "correctly"
		await bot.general_channel.send(message)

		embed = discord.Embed(title="Active clues")
		for i in range(len(bot.active_clues)):
			embed.add_field(name="{}.".format(i+1),value=str(bot.active_clues[i]),inline=False)
		await bot.general_channel.send(embed=embed)

@bot.command()
async def contact(ctx,clue,word):
	word = word.lower()
	if bot.state == 'contacting':
		await ctx.send("Already contacting on another clue, please wait")
	elif bot.giver == ctx.author:
		await ctx.send("Only non-word giver can contact for clues. Use $guess instead")
	elif ctx.author == bot.active_clues[int(clue)-1].cluer:
		await ctx.send("You can't contact on your own clue!")
	elif int(clue) > len(bot.active_clues):
		await ctx.send("Enter a valid clue number")
	elif not isinstance(ctx.message.channel,discord.DMChannel):
		await ctx.send("Contact on DM!")
	elif ctx.author in bot.active_clues[int(clue)-1].contacts.keys():
		await ctx.send("You have already contacted on this clue")
	else:
		bot.active_clues[int(clue)-1].contacts[ctx.author] = word
		await bot.general_channel.send("{} has contacted on clue {}".format(ctx.author,clue))
		if len(bot.active_clues[int(clue)-1].contacts) >= bot.num_contacts:
			bot.state = 'countdown'
			bot.contacted_clue = clue
			await bot.general_channel.send("There are now enough contacts for clue {}. Starting countdown".format(clue))

#TODO add command to 
bot.remove_command('help')

@bot.command()
async def status(ctx):
	embed = discord.Embed(title="The current status of the game is", description="The word giver is {}. The current guess is *{}*".format(bot.giver,bot.guess), color=0xeee657)
	for i in range(len(bot.active_clues)):
		embed.add_field(name="{}.".format(i+1),value=str(bot.active_clues[i]),inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
	await ctx.send("I have not implemented this yet...... :(")
@bot.command()
async def help(ctx):
	embed = discord.Embed(title="contact bot", description="A Bot which helps play contact. List of commands are:", color=0xeee657)

	embed.add_field(name="$start num_players", value="Starts a game on this channel where number of players needed to contact is `num_players`", inline=False)
	embed.add_field(name="$word WORD", value="DM this command to give a word(WORD) for contacting", inline=False)
	embed.add_field(name="$clue WORD CLUE", value="Registers a clue (CLUE) having correct answer as WORD. DM please.", inline=False)
	embed.add_field(name="$contact clue_no. word", value="Contact on clue numbered `clue_no` on `word`.DM please", inline=False)
	embed.add_field(name="$guess clue_no. word",value="Guess by word giver for clue numbered `clue_no` on `word`.",inline=False)
	# embed.add_field(name="$cat", value="Gives a cute cat gif to lighten up the mood.", inline=False)
	embed.add_field(name="$info", value="Gives a little info about the bot", inline=False)
	embed.add_field(name="$status", value="Prints the current status of the game", inline=False)
	embed.add_field(name="$help", value="Gives this message", inline=False)

	await ctx.send(embed=embed)

bot.run('NjkwOTc5Njc5NTUyNjY3Nz')