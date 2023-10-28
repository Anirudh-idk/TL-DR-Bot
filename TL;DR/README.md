# TL;DR

Ever opened a discord channel and felt like in a chat battefield with no context of what's happening?Relate too much?

**TL;DR** is a discord bot made just for that.
Get quick summaries since the last time you were alive in that channel or maybe just the faithful hours you wished to do something productive.

As of right now TL;DR offers two possible ways to request a summary:
1. !tldr complete - get the summary since your last message
2. !tldr tminus <start(hours)> <end(hours)> - get a summary between t-start and t-end

The summary is sent to your dm ,to keep channel uncluttered, along with all relevant information regarding the request.

Another important mention is the fact that if the requested range of messages contain a reference to some messages that do not lie in the range they are still included while summarizing to try and preserve context.

The bot also includes the code to take and send attachments as well but is commented as it affects the performance quite a bit.
It can be used as preferred.

## usage
1. Clone this repository or download the zip and extract in your local machine.

2. `cd` to the TL;DR directory.

3. Follow [this tutorial](https://discordpy.readthedocs.io/en/stable/discord.html) to make a discord application and copy the token.

4. Replace the `.env.example` file with `.env` file and paste your token.

5. Run `pip install -r requirements.txt` to install dependencies.

6. Run `main.py`.

## Additional information
The bot uses HuggingFace's Transformers along with bart model specifically trained for the job, for more information about the model go [here].(https://huggingface.co/lidiya/bart-large-xsum-samsum).

This was my first dive into bots and models or working with this particular library but I am open to any support, ideas where I can improve or features that I can include.Just open an issue or if you have something you believe you can improve open a pull-request.

