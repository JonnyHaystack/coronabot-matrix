import asyncio
from datetime import datetime
from json import JSONDecodeError

from nio import AsyncClient
from nio import RoomMessageText
from nio import MatrixRoom
from nio import InviteEvent

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
        self.client.add_event_callback(self.invite_handler, InviteEvent)

    async def run(self):
        await self.client.login(settings.MATRIX_PASSWORD)
        await self.client.sync_forever(timeout=30000)

    async def invite_handler(self, room: MatrixRoom, event: InviteEvent):
        await self.client.join(room.room_id)

    async def message_handler(self, room, event: RoomMessageText):
        # Set up command handlers
        args = event.body.split(" ")
        if len(args) > 0 and args[0].startswith("!"):
            command = args[0][1:]
            if command in self.command_handlers:
                await self.command_handlers[command](room, event)

    async def send_message(self, room, message):
        await self.client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "body": message,
                "formatted_body": message,
            },
        )

    async def start(self, room, _):
        await self.send_message(room, "Running")

    async def cbstats(self, room, event):
        args = event.body.split(" ")[1:]
        message = ""
        country_info = None
        try:
            if len(args) == 0:
                stats, updated = data.get_global_cases()
            else:
                country = " ".join(args)
                stats, country_info, updated = data.get_country_cases(country)
            last_updated = datetime.fromtimestamp(int(updated) / 1000)
            message = formatting.format_stats(
                stats, country_info, last_updated
            )
        except JSONDecodeError:
            if country is not None:
                message = f"{country} doesn't exist lmao"
            else:
                message = "Error: Could not look up stats"
        await self.send_message(room, message)


if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.run())
