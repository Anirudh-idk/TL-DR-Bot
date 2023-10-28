from transformers import pipeline
from discord.ext import commands
from dotenv import load_dotenv
import os, datetime, discord

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

# Creating Bot instance
client = commands.Bot(command_prefix="!", intents=intents)

# Creating summarizer model instance
summarizer = pipeline("summarization", model="lidiya/bart-large-xsum-samsum")


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!")


# dm the user a summary
async def dm_tldr(member: discord.Member, dm_msg: str):
    try:
        await member.create_dm()
        await member.dm_channel.send(dm_msg)
    except:
        print("Can't DM this user.")


# function to get all referred messages recursively
async def get_refrence_msgs(
    ctx: commands.context.Context, message: discord.Message
) -> str:
    str_ref: str = str(message.content)
    while message.reference is not None:
        message = await ctx.fetch_message(message.reference.message_id)
        str_ref = str(message.content) + " " + str_ref
    return str_ref


# creating command group for requesting summaries
@client.group(name="tldr", invoke_without_command=True)
async def tldr(ctx):
    print("No subcommand passed.")
    await ctx.message.delete()  # deleting request after it's processed


# command to get summary till your last message
@tldr.command("complete")
async def complete(ctx):
    msgs: list[discord.Message] = []

    fetchmsg: discord.Message = await ctx.channel.history(
        limit=1000, before=ctx.message
    ).find(lambda m: m.author.id == ctx.author.id)

    msgs = await ctx.channel.history(
        limit=1000, after=fetchmsg, before=ctx.message
    ).flatten()

    summary: str = ""
    convo: str = ""

    for msg in msgs:
        # checking if msg has a reference
        if type(msg) == discord.Message and msg.reference is not None:
            temp_msg = await ctx.fetch_message(msg.reference.message_id)
            if (
                temp_msg not in msgs
            ):  # if the referred message is not in requested range
                convo += await get_refrence_msgs(ctx, msg) + "."
        elif type(msg) == discord.Message:
            convo += str(msg.content) + "."

    # checking length of the the conversataion as the model is limited at 1024 characters
    while len(convo) > 1024:
        summary += summarizer((convo[:1024]), max_length=200, do_sample=False)[0].get(
            "summary_text"
        )
        convo = convo[1024:]
    if len(convo) > 0:
        summary += summarizer((convo), max_length=200, do_sample=False)[0].get(
            "summary_text"
        )

    if len(msgs) > 0:
        dm = f"Server - {ctx.guild}\n \
            Channel - {ctx.channel}\n \
            TL;DR from {msgs[0].created_at.strftime('%d-%m-%Y %H:%M')} to {msgs[-1].created_at.strftime('%d-%m-%Y %H:%M')}\n\n \
            TL;DR\n \
            {summary}"

        await dm_tldr(ctx.author, dm)

    await ctx.message.delete()  # deleting request after it's processed


# command for summary from time A to time B
@tldr.command("tminus")
async def tminus(ctx, time_range_start: str = None, time_range_end: str = None):
    msgs: list[discord.Message] = []

    # validating inputs
    if time_range_start.isnumeric() and time_range_end.isnumeric:
        if int(time_range_start) > 0 and int(time_range_end) >= 0:
            # creating datetime for start and end times
            time_start: datetime.datetime = ctx.message.created_at - datetime.timedelta(
                hours=int(time_range_start)
            )
            time_end: datetime.datetime = ctx.message.created_at - datetime.timedelta(
                hours=int(time_range_end)
            )
            msgs = await ctx.channel.history(
                limit=1000, after=time_start, before=time_end
            ).flatten()
        else:
            pass
    else:
        pass

    summary: str = ""
    convo: str = ""

    for msg in msgs:
        if type(msg) == discord.Message and msg.reference is not None:
            convo += await get_refrence_msgs(ctx, msg)
            convo += "."
        elif type(msg) == discord.Message:
            convo += str(msg.content)
            convo += "."

    # checking length of the the conversataion as the model is limited at 1024 characters
    while len(convo) > 1024:
        summary += summarizer((convo[:1024]), max_length=200, do_sample=False)[0].get(
            "summary_text"
        )
        convo = convo[1024:]
    if len(convo) > 0:
        summary += summarizer((convo), max_length=200, do_sample=False)[0].get(
            "summary_text"
        )

    if len(msgs) > 0:
        dm = f"Server - {ctx.guild}\n \
            Channel - {ctx.channel}\n \
            TL;DR from {msgs[0].created_at.strftime('%d-%m-%Y %H:%M')} to {msgs[-1].created_at.strftime('%d-%m-%Y %H:%M')}\n\n \
            TL;DR\n \
            {summary}"

        await dm_tldr(ctx.author, dm)

    await ctx.message.delete()  # deleting request after it's processed


client.run(TOKEN)
