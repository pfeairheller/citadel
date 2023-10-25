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
parser.set_defaults(handler=lambda args: launch(args))


def launch(args):
    help.ogler.level = logging.CRITICAL
    help.ogler.reopen(name="wallet", temp=True, clear=True)

    def main(page: ft.Page):
        page.fonts = {
            "SourceCodePro": "/source_code_pro_static/SourceCodePro-Regular.ttf"
        }

        app = CitadelApp(page)
        page.add(
            app.build()
        )

    ft.app(target=main, assets_dir="/Users/pfeairheller/git_root/citadel/assets")
