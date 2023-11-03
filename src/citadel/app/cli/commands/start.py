# -*- encoding: utf-8 -*-
"""
KERI
keri.kli.witness module

Witness command line interface
"""
import argparse
import logging

import flet as ft
from keri import help
from citadel.app.walleting import CitadelApp

d = "Runs Citadel.\n"
parser = argparse.ArgumentParser(description=d)

async def launch(args):
    help.ogler.level = logging.CRITICAL
    help.ogler.reopen(name="wallet", temp=True, clear=True)

    async def main(page: ft.Page):
        page.fonts = {
            "SourceCodePro": "/source_code_pro_static/SourceCodePro-Regular.ttf"
        }

        app = CitadelApp(page)
        await page.add_async(
            app.build()
        )

    await ft.app_async(target=main, assets_dir="/Users/pfeairheller/git_root/citadel/assets")

parser.set_defaults(handler=launch)
