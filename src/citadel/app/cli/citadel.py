# -*- encoding: utf-8 -*-
"""
watopnet.app.cli module

"""
import asyncio

import multicommand
from keri import help

from keri.app import directing
from citadel.app.cli import commands

logger = help.ogler.getLogger()


def main():
    parser = multicommand.create_parser(commands)
    args = parser.parse_args()

    if not hasattr(args, 'handler'):
        parser.print_help()
        return

    try:
        asyncio.run(args.handler(args))

    except Exception as ex:
        import os
        if os.getenv('DEBUG_WAllET'):
            import traceback
            traceback.print_exc()
        else:
            print(f"ERR: {ex}")
        return -1


if __name__ == "__main__":
    main()
