import os, datetime
from transformers import pipeline
import discord, time
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
summarizer = pipeline("summarization", model="lidiya/bart-large-xsum-samsum")


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!")


async def dm_tldr(member, dm_msg):
    try:
        await member.create_dm()
        await member.dm_channel.send(dm_msg)
    except:
        print("Can't DM this user.")


async def get_refrence_msgs(
    ctx: commands.context.Context, message: discord.Message
) -> str:
    str_ref: str = str(message.content)
    while message.reference is not None:
        message = await ctx.fetch_message(message.reference.message_id)
        str_ref = str(message.content) + " " + str_ref
    return str_ref


@client.command("tldr")
async def tldr(ctx, time_range_start: str = None, time_range_end: str = None):
    msgs: list[discord.Message] = []
    if time_range_start is None and time_range_end is None:
        fetchmsg: discord.Message = await ctx.channel.history(
            limit=1000, before=ctx.message
        ).find(lambda m: m.author.id == ctx.author.id)

        msgs = await ctx.channel.history(
            limit=1000, after=fetchmsg, before=ctx.message
        ).flatten()

    elif time_range_start.isnumeric() and time_range_end.isnumeric:
        if int(time_range_start) > 0 and int(time_range_end) >= 0:
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
            return
    else:
        return

    summary: str = ""
    convo: str = ""

    for msg in msgs:
        if type(msg) == discord.Message and msg.reference is not None:
            convo += await get_refrence_msgs(ctx, msg)
            convo += "."
        elif type(msg) == discord.Message:
            convo += str(msg.content)
            convo += "."
    print(convo)

    if len(convo) > 1024:
        while len(convo) > 1024:
            summary += summarizer((convo[:1024]), max_length=200, do_sample=False)[
                0
            ].get("summary_text")
            convo = convo[1024:]
    elif len(convo) > 0:
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


client.run(TOKEN)
