# -*- encoding: utf-8 -*-
"""
KERI
keri.kli.witness module

Witness command line interface
"""
import argparse
import logging

import flet as ft
from flet_core import theme
from keri import help
from citadel.app.apping import CitadelApp

d = "Runs Citadel.\n"
parser = argparse.ArgumentParser(description=d)


async def launch(args):
    help.ogler.level = logging.CRITICAL
    help.ogler.reopen(name="wallet", temp=True, clear=True)

    async def main(page: ft.Page):
        await page.client_storage.remove_async("gleif.citadel.agents")

        page.title = "Citadel"
        page.padding = 0
        page.theme = theme.Theme(font_family="Verdana")
        page.theme.page_transitions.windows = "cupertino"
        await page.update_async()

        page.agents = await page.client_storage.contains_key_async("gleif.citadel.agents")

        app = CitadelApp(page)
        await page.add_async(
            app.build()
        )

    await ft.app_async(target=main, assets_dir="../../../citadel/assets")


parser.set_defaults(handler=launch)
