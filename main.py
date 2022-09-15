import nextcord as discord
from nextcord.ext import commands
import os
import dotenv
import time

dotenv.load_dotenv()

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
    await member.send('''Welcome to Shamo classes! 

We value each and every one of you who has joined this server. You can get information about us from the <#996727429873795153> <#996730313436823593> <#994617934691442738> text channels. Please collect your roles from <#1007866858592022532>!

To get it straight, we care for you and want to help you in your IGCSE journey. Have any questions, feeling low on motivation, not sure what to do... get help here!

We are glad to see you here!
''')

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


@bot.slash_command(description="Ping a helper in any subject channel")
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

bot.run(token)