from __future__ import annotations
import asyncio
import random
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import os

import ModuleUpdate
ModuleUpdate.update()

import Utils

if __name__ == "__main__":
    Utils.init_logging("NecroHinterClient", exception_logger="Client")

from CommonClient import gui_enabled, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop


class NecroDancerClientCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx: NecroDancerContext):
        self.ctx = ctx
    def _cmd_set_log_file(self):
        """Locate the Necrodancer Log File."""
        root = tk.Tk()
        root.withdraw()

        self.ctx.game_communication_path = filedialog.askopenfilename()
        self.output(f"Log File Set to {self.ctx.game_communication_path}")


class NecroDancerContext(CommonContext):
    command_processor: int = NecroDancerClientCommandProcessor
    tags = CommonContext.tags | {"TextOnly", "NecroHinter"}
    game = ""  # empty matches any game since 0.3.2
    items_handling = 0b111  # receive all items for /received
    want_slot_data = False  # Can't use game specific slot_data

    def __init__(self, server_address, password):
        super(NecroDancerContext, self).__init__(server_address, password)
        self.game_communication_path = None
        self.starting_time = datetime.now()

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(NecroDancerContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(NecroDancerContext, self).connection_closed()
        pass

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(NecroDancerContext, self).shutdown()
        pass

    def on_package(self, cmd: str, args: dict):
        pass

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class NecroDancerManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago NecroHinter Client"

        self.ui = NecroDancerManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def game_watcher(ctx: NecroDancerContext):
    while not ctx.exit_event.is_set():
        if not ctx.game_communication_path:
            await asyncio.sleep(0.1)
            continue
        training = False
        logfile = open(ctx.game_communication_path, "r")
        while not ctx.exit_event.is_set():
            line = logfile.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            print(line)
            if "Starting Training run" in line:
                ctx.command_processor.output("Training Mode Detected, Disabling Hints.")
                print("Training Mode Detected, Disabling Hints.")
                training = True
            if "[NecrodancerAPHints] [info] bossclear" in line:
                if datetime.fromisoformat(line[1:23]) < ctx.starting_time or training:
                    continue
                print(ctx.missing_locations)
                location = random.choice(list(ctx.missing_locations))
                message = [{"cmd": 'LocationScouts', "locations": [location], 'create_as_hint': 1}]
                await ctx.send_msgs(message)


def main():
    async def _main(args):
        ctx = NecroDancerContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        progression_watcher = asyncio.create_task(
            game_watcher(ctx), name="NecrodancerProgressionWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await progression_watcher

        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Necrodancer Hint Client")

    args, rest = parser.parse_known_args()
    colorama.init()
    asyncio.run(_main(args))
    colorama.deinit()


if __name__ == '__main__':
    main()
