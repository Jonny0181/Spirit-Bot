import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import motor.motor_asyncio as motor

load_dotenv()

class SpiritBot(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        self.db = motor.AsyncIOMotorClient(os.getenv('MONGO_DB'))[os.getenv('MONGO_DB_COLLECTION')]
        
    async def on_ready(self):
        print(f'[Main] Logged in as: {self.user.name}')
        
        try:
            await self.load_extension('jishaku')
            print(f"Loaded jishaku!")
        except Exception as e:
            print(f'ERR loading Jishaku: {str(e)}')
            
        await self.load_modules()

    async def load_modules(self):
        modulesLoaded = 0
        modules = [e for e in os.listdir('modules') if e.endswith('.py')]

        for module in modules:
            try:
                await self.load_extension(f'modules.{module[:-3]}')
                modulesLoaded += 1
            except commands.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                print(f'[Main] Err: {e}')
        print(f'[Main] Loaded {modulesLoaded} module(s).')

        print('[Main] Attempting to sync application commands...')
        try:
            synced = await self.tree.sync()
        except Exception as e:
            print(f'[Main] Err: {e}')
        print(f'[Main] Synced {len(synced)} application command(s).')
        
if __name__ == "__main__":
    Spirit = SpiritBot(command_prefix=commands.when_mentioned_or(os.getenv('PREFIX')), intents=discord.Intents.all())
    Spirit.run(os.getenv("TOKEN"))