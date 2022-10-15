import nextcord as discord
from nextcord.ext import commands
import os
import time
import requests
from pytesseract import pytesseract
from PIL import Image
import io
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix = ";", intents = intents, help_command = None, case_insensitive = True)
token = os.getenv("DISCORD_TOKEN")

helper_roles = {994617607862878278: 994618740534689884, 994617634719023234: 994618740534689884, 996227322766176286: 996227520313688074, 996227337010040923: 996227520313688074, 994617722971365386: 994618785740882050, 994617745352171561: 994618785740882050, 995976183650996335: 996184182982189076, 995976217582903326: 996184182982189076, 996185236167720990: 995976597708472320, 996185250654863483: 995976597708472320}

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name = "DM to contact moderators"))
    print("Your wish is my command!")
    my_user = await bot.fetch_user(706855396828250153)
    await my_user.send("Ready!")

@bot.event
async def on_message(ctx: discord.Message):

    if ctx.author == bot.user:
        return

    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        sure = await user.send("Would you like to send this message to the moderators?")
        await sure.add_reaction("✅")
        await sure.add_reaction("❌")
        try:
            reaction, person = await bot.wait_for("reaction_add", check = lambda r, p: p.id == user.id and str(r.emoji) in ["✅", "❌"] and r.message.id == sure.id, timeout = 120.0)
        except asyncio.TimeoutError:
            await sure.reply("Cancelling...", mention_author = False)
        else:
            if str(reaction.emoji) == "✅":
                await ctx.reply("This message will be sent to the moderators! Their reply will be sent to you in this DM!", mention_author = False)
                modmail_channel = bot.get_channel(1023527239574376499)
                modmail_embed = discord.Embed(title = "New message!", description = f'''**User**: <@!{user.id}>

**Message**: {ctx.content}
''', colour = discord.Colour.orange())
                await modmail_channel.send(embed = modmail_embed)

            else:
                await sure.reply("Cancelling...", mention_author = False)

@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.send('''Welcome to Shamo IGCSE!

We appreciate your initiative to join this server. We can tell you really want to improve your studies. You've come to the right place!

We are a community of tutors, helpers and other fellow students with whom you can interact and ask questions regarding your subject, or even life in general!

You can find more information about us in the <#996727429873795153>, <#996730313436823593>, and <#994617934691442738> text channels. Please collect your roles from the <#1007866858592022532> channel!
''')
    except discord.errors.Forbidden:
        pass

@bot.slash_command(name = "reply", description = "Send a reply to a user for their mod mail query", default_member_permissions = discord.Permissions(administrator = True))
async def reply(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name = "user", description = "The user to send the reply to", required = True), message: str = discord.SlashOption(name = "message", description = "The message to be sent", required = True)):
    modmail_reply = discord.Embed(title = "Message from the moderators", description = message, colour = discord.Colour.orange())
    await user.send(embed = modmail_reply)
    await interaction.send(f"The following message has been sent to {user.mention} by {interaction.user.mention}!", embed = modmail_reply)

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
                 query: str = discord.SlashOption(name="query", description="Search query", required=False),
                 image: discord.Attachment = discord.SlashOption(name = "image", description = "Enter the image of the question to be searched", required = False)):

    if image is None and query is None:
        await interaction.send("You have to enter a query string or an image for this command to work!", ephemeral = True)
        return

    if image is not None:
        response = requests.get(image.url, stream = True)
        img = Image.open(io.BytesIO(response.content))
        content = pytesseract.image_to_string(img)
        content = content.replace("\n", " ")
        content = content.replace("  ", " ")
    else:
        content = query
        
    try:
        response = requests.get(f"https://paper.sc/search/?as=json&query={content}").json()
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
            await interaction.send(embed=embed)
    except:
        await interaction.send("No results found in past papers. Try changing your query for better results.", ephemeral=True)

@bot.slash_command(name = "topicals", description = "Fetch the links to view topical papers")
async def topicals(interaction: discord.Interaction, subject: str = discord.SlashOption(name = "subject", description = "Choose your subject", choices = ["Additional Mathematics", "Mathematics", "Physics", "Chemistry", "Biology"], required = True)):
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
    view = discord.ui.View(timeout = None)
    view.add_item(discord.ui.Button(label = subject, style = discord.ButtonStyle.url, url = url))
    await interaction.send(view = view)

@bot.slash_command(name = "worksheets", description = "Fetch the worksheets for different subjects")
async def worksheets(interaction: discord.Interaction, subject: str = discord.SlashOption(name = "subject", description = "Choose your subject", choices = ["Additional Mathematics", "Physics"], required = True)):
    if subject == "Additional Mathematics":
        url = "https://drive.google.com/drive/folders/1Tbs9IumyPNZC3S4O1q2oZpA6Btq0ojeI?usp=sharing"
    elif subject == "Physics":
        url = "https://drive.google.com/drive/folders/13CzK4ZZFK4fSgg4QFb1jkGHxvhGV1qS-?usp=sharing"
    view = discord.ui.View(timeout = None)
    view.add_item(discord.ui.Button(label = subject, style = discord.ButtonStyle.url, url = url))
    await interaction.send(view = view)


bot.run(token)