from typing import Dict
from multiprocessing import Process
from ..LauncherComponents import Component, components, Type
from ..AutoWorld import WebWorld, World


def run_client():
    from worlds.necrohinter.Client import main
    p = Process(target=main)
    p.start()


components.append(Component("NecroHinter Client", func=run_client, component_type=Type.CLIENT))


class NecrohinterWebWorld(WebWorld):
    options_page = "games/Sudoku/info/en"
    theme = 'partyTime'
    
    tutorials = []


class NecroHinterWorld(World):
    """
    Play Crypt of the Necrodancer to earn Location Hints
    """
    game = "NecroHinter"
    web = NecrohinterWebWorld()
    data_version = 1

    item_name_to_id: Dict[str, int] = {}
    location_name_to_id: Dict[str, int] = {}

    @classmethod
    def stage_assert_generate(cls, multiworld):
        raise Exception("NecroHinter cannot be used for generating worlds, the client can instead connect to any other world")
