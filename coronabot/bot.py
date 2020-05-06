import asyncio
import shlex
from datetime import datetime
from json import JSONDecodeError

from flag import flagize
from markdown import markdown
from nio import AsyncClient
from nio import RoomMessageText

from coronabot import data
from coronabot import formatting
from coronabot import settings


class Bot:
    def __init__(self):
        self.client = AsyncClient(
            settings.MATRIX_SERVER, settings.MATRIX_USERNAME
        )
        self.command_handlers = {
            "cbstart": self.start,
            "cbstats": self.cbstats,
        }
        self.client.add_event_callback(self.message_handler, RoomMessageText)

    async def run(self):
        await self.client.login(settings.MATRIX_PASSWORD)
        await self.client.sync_forever(timeout=30000)

    async def message_handler(self, room, event):
        # Set up command handlers
        args = event.body.split(" ")
        if len(args) > 0 and args[0].startswith("!"):
            command = args[0][1:]
            if command in self.command_handlers:
                await self.command_handlers[command](room, event)

    async def send_message(self, room, message):
        message_markdown = markdown(message, extensions=["nl2br"])
        await self.client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "body": message,
                "formatted_body": message_markdown,
            },
        )

    async def start(self, room, _):
        await self.send_message(room, "Running")

    async def cbstats(self, room, event):
        args = event.body.split(" ")[1:]
        message = ""
        try:
            if len(args) == 0:
                stats, updated = data.get_global_cases()
                message = "**Global stats** "
            else:
                country = " ".join(args)
                stats, country_info, updated = data.get_country_cases(country)
                message = flagize(
                    f":{country_info['country_code']}: "
                    f"**{country_info['country_name']}** "
                )
            last_updated = datetime.fromtimestamp(
                int(updated) / 1000
            ).strftime("%Y-%m-%d %H:%M")
            message += f"({last_updated})\n"
            message += formatting.format_stats(stats)
        except JSONDecodeError:
            if country is not None:
                message = f"{country} doesn't exist lmao"
            else:
                message = "Error: Could not look up stats"
        await self.send_message(room, message)


if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.run())
