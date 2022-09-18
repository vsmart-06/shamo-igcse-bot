import nextcord as discord
from nextcord.ext import commands
import os
import time
import requests
import json

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix = ";", intents = intents, help_command = None, case_insensitive = True)
token = os.getenv("DISCORD_TOKEN")

helper_roles = {994617607862878278: 994618740534689884, 994617634719023234: 994618740534689884, 996227322766176286: 996227520313688074, 996227337010040923: 996227520313688074, 994617722971365386: 994618785740882050, 994617745352171561: 994618785740882050, 995976183650996335: 996184182982189076, 995976217582903326: 996184182982189076, 996185236167720990: 995976597708472320, 996185250654863483: 995976597708472320}

@bot.event
async def on_ready():
    print("Your wish is my command!")
    shamit = await bot.fetch_user(720437409573240914)
    await shamit.send("I'm ready!")

@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.send('''Welcome to Shamo classes! 

We value each and every one of you who has joined this server. You can get information about us from the <#996727429873795153> <#996730313436823593> <#994617934691442738> text channels. Please collect your roles from <#1007866858592022532>!

To get it straight, we care for you and want to help you in your IGCSE journey. Have any questions, feeling low on motivation, not sure what to do... get help here!

We are glad to see you here!
''')
    except discord.errors.Forbidden:
        pass

class CancelPingBtn(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=890)
        self.value = True

    @discord.ui.button(label="Cancel Ping", style=discord.ButtonStyle.blurple)
    async def cancel_ping_btn(self, button: discord.ui.Button, interaction_b: discord.Interaction):
        button.disabled = True
        self.value = False
        await self.message.edit(content=f"Ping cancelled by {interaction_b.user}", view=None)

    async def on_timeout(self): # 15 minutes has passed so execute the ping.
        await self.message.edit(view=None) # Remove Cancel Ping button
        if self.value:
            await self.message.channel.send(f"{self.helper_role.mention}\n(Requested by {self.user.mention})")  # Execute ping
            await self.message.delete()  # Delete original message


@bot.slash_command(name = "helper", description="Ping a helper in any subject channel")
async def helper(interaction: discord.Interaction):
    try:
        helper_role = discord.utils.get(interaction.guild.roles, id=helper_roles[interaction.channel.id])
    except:
        await interaction.send("There are no helper roles specified for this channel.", ephemeral=True)
        return
    await interaction.response.defer()
    roles = [role.name.lower() for role in interaction.user.roles]
    if "server booster" in roles:
        await interaction.send(f"{helper_role.mention}\n(Requested by {interaction.user.mention})")
        return
    view = CancelPingBtn()
    message = await interaction.send(
        f"The helper role for this channel, `@{helper_role.name}`, will automatically be pinged (<t:{int(time.time() + 890)}:R>). Please click on the `Cancel Ping` button if your question has been solved",
        view=view)
    view.message = message
    view.helper_role = helper_role
    view.user = interaction.user

@bot.slash_command(name = "search", description="Search for IGCSE past papers with subject code/question text")
async def search(interaction: discord.Interaction,
                 query: str = discord.SlashOption(name="query", description="Search query", required=True)):
    await interaction.response.defer(ephemeral=True)
    try:
        response = requests.get(f"https://paper.sc/search/?as=json&query={query}").json()
        if len(response['list']) == 0:
            await interaction.send("No results found in past papers. Try changing your query for better results.", ephemeral=True)
        else:
            embed = discord.Embed(title="Potential Match",
                                  description="Your question matched a past paper question!",
                                  colour=discord.Colour.green())
            for n, item in enumerate(response['list'][:3]):
                embed.add_field(name="Subject", value=item['doc']['subject'], inline=True)
                embed.add_field(name="Paper", value=item['doc']['paper'], inline=True)
                embed.add_field(name="Session", value=item['doc']['time'], inline=True)
                embed.add_field(name="Variant", value=item['doc']['variant'], inline=True)
                embed.add_field(name="QP Link", value=f"https://paper.sc/doc/{item['doc']['_id']}", inline=True)
                embed.add_field(name="MS Link", value=f"https://paper.sc/doc/{item['related'][0]['_id']}",
                                inline=True)
            await interaction.send(embed=embed, ephemeral=True)
    except:
        await interaction.send("No results found in past papers. Try changing your query for better results.", ephemeral=True)

class TopicalSubjects(discord.ui.Select):
    def __init__(self):
        options = ["Additional Mathematics", "Mathematics", "Physics", "Chemistry", "Biology"]
        super().__init__(placeholder = "Choose a subject", min_value = 1, max_value = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        subject = self.values[0]
        view = discord.ui.View(timeout = None)
        if subject == "Additional Mathematics":
            url = "https://alvinacademy.com/igcse/0606-additional-mathematics-past-year-papers/0606-past-year-by-topics/"
        elif subject == "Mathematics":
            url = "https://gceguide.com/Books/tpp/Math-Classified-IGCSE.pdf"
        elif subject == "Physics":
            url = "https://www.physicsandmathstutor.com/physics-revision/igcse-cie/"
        elif subject == "Chemistry":
            url = "https://www.physicsandmathstutor.com/chemistry-revision/igcse-cie/"
        elif subject == "Biology":
            url = "https://www.physicsandmathstutor.com/biology-revision/igcse-cie/"
        view.add_item(discord.ui.Button(label = subject, style = discord.ButtonStyle.url, url = url))
        await interaction.response.edit_message(view = view)

class TopicalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(TopicalSubjects())

@bot.slash_command(name = "topicals", description = "Fetch the links to view topical papers")
async def topicals(interaction: discord.Interaction):
    await interaction.send(view = TopicalView())


bot.run(token)