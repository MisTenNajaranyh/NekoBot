from discord.ext import commands
import logging, traceback, sys, discord, json, dbl, asyncio
from collections import Counter

import config

log = logging.getLogger('NekoBot')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='NekoBot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

startup_extensions = {
    'modules.general',
    'modules.mod',
    'modules.economy',
    'modules.reactions',
    'modules.nsfw',
    'modules.levels',
    'modules.imgwelcome',
    'modules.fun',
    'modules.dbl',
    'modules.osu'
}

class NekoBot(commands.AutoShardedBot):
    """NekoBot Rewrite OwO"""

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(config.prefix),
                         description=config.description,
                         pm_help=None,
                         help_attrs=dict(hidden=True))
        self.bot = NekoBot
        self.counter = Counter()
        self.token = config.dbots.key
        self.dblpy = dbl.Client(self.bot, self.token)

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print("Failed to load {}.".format(extension), file=sys.stderr)
                traceback.print_exc()

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(exception, commands.DisabledCommand):
            await ctx.send('This command is disabled...')
        elif isinstance(exception, commands.CommandInvokeError):
            em = discord.Embed(color=0xDEADBF,
                               title="Error",
                               description=f"Error in command {ctx.command.qualified_name}, [Support Server](https://discord.gg/q98qeYN)")
            await ctx.send(embed=em)
            print('In {}:'.format(ctx.command.qualified_name), file=sys.stderr)
            traceback.print_tb(exception.original.__traceback__)
            print('{}: {}'.format(exception.original.__class__.__name__, exception.original), file=sys.stderr)
        elif isinstance(exception, commands.BadArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await self.send_cmd_help(ctx)
        elif isinstance(exception, commands.CheckFailure):
            await ctx.send('You are not allowed to use that command.')
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.send('Command is on cooldown... {:.2f}s left'.format(exception.retry_after))
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.BotMissingPermissions):
            await ctx.send("Im missing permissions ;-;")
        else:
            log.exception(type(exception).__name__, exc_info=exception)

    async def on_message(self, message):
        self.counter["messages_read"] += 1
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command(self, command):
        self.counter["commands"] += 1

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print("Ready OwO")
        print(self.shard_count)
        print(f"Servers {len(self.guilds)}")
        print(f"Users {len(set(self.get_all_members()))}")
        while True:
            print("Attempting to update server count.")
            try:
                await self.dblpy.post_server_count(shard_count=self.shard_count, shard_no=self.shard_id)
                print("Posted server count. {}".format(len(self.bot.guilds)))
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

    def run(self):
        super().run(config.token, reconnect=True)

def run_bot():
    bot = NekoBot()
    bot.run()

if __name__ == '__main__':
    run_bot()