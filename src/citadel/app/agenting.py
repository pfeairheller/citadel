import flet as ft
from keri import kering
from keri.app import configing, habbing, directing, keeping
from keri.core import coring
from keri.vdr import credentialing

from citadel.app.colouring import Brand
from citadel.core import agenting
from citadel.tasks import oobiing

DEFAULT_USERNAME = "citadel"
DEFAULT_PASSCODE = "DoB26Fj4x9LboAFWJra17O"


class AgentInitialization:

    def __init__(self, app, page: ft.Page):
        super(AgentInitialization, self).__init__()
        self.app = app
        self.page = page
        self.username = ft.TextField(value=DEFAULT_USERNAME)
        self.passcode = ft.TextField(value=DEFAULT_PASSCODE, password=True)

        self.agent_init = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agent Initialization"),
            content=ft.Column([
                ft.Text("New Username"),
                self.username,
                ft.Text("New Passcode"),
                self.passcode,
            ]),
            actions=[
                ft.ElevatedButton("Create", on_click=self.generate_habery,
                                  color=ft.colors.WHITE, bgcolor=Brand.SECONDARY),
                ft.ElevatedButton(
                    "Cancel", on_click=self.close_init, color=Brand.BATTLESHIP_GRAY, ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )

    def build(self):
        return self.agent_init

    async def open_init(self, _):
        print("opening")
        self.agent_init.open = True
        await self.page.update_async()

    async def close_init(self, _):
        print("closing")
        self.agent_init.open = False
        await self.page.update_async()

    async def generate_habery(self, e):
        self.agent_init.open = False
        cf = configing.Configer(name="demo-witness-oobis-schema",
                                base="",
                                headDirPath="./",
                                temp=False,
                                reopen=True,
                                clear=False)
        kwa = dict()

        kwa["salt"] = coring.Salter(raw=self.app.salt.encode("utf-8")).qb64
        kwa["bran"] = self.passcode.value
        kwa["algo"] = self.app.algo
        kwa["tier"] = self.app.tier

        hby = habbing.Habery(name=self.username.value,
                             base=self.app.base, temp=self.app.temp, cf=cf, **kwa)

        directing.runController([oobiing.OOBILoader(hby=hby)])
        directing.runController([oobiing.OOBIAuther(hby=hby)])

        hby.close()

        await self.page.update_async()


class AgentConnection:

    def __init__(self, app, page, username):
        self.app = app
        self.page = page
        self.username = username
        self.passcode = ft.TextField(value=DEFAULT_PASSCODE, password=True)

        column = ft.Column([
            ft.Text("Name"),
            ft.TextField(value=self.username, read_only=True),
            ft.Text("Passcode"),
            self.passcode
        ])

        self.connectDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Open Agent"),
            content=ft.Container(content=column, ),
            actions=[
                ft.ElevatedButton("Open", on_click=self.connect,
                                  color=ft.colors.WHITE, bgcolor=Brand.SECONDARY),
                ft.ElevatedButton(
                    "Cancel", on_click=self.cancel_connect, color=Brand.BATTLESHIP_GRAY, ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        super(AgentConnection, self).__init__()

    def build(self):
        return self.connectDialog

    async def cancel_connect(self, e):
        self.connectDialog.open = False
        await self.page.update_async()

    async def connect(self, e):
        self.connectDialog.open = False
        bran = self.passcode.value

        ks = keeping.Keeper(name=self.username,
                            temp=False,
                            reopen=True)

        aeid = ks.gbls.get('aeid')
        if aeid is None:
            print("Keystore must already exist, exiting")
            await self.page.snack(f"Keystore not correcting initialized...")
            return

        ks.close()

        while True:
            try:
                if bran:
                    bran = bran.replace("-", "")

                hby = habbing.Habery(
                    name=self.username, bran=bran, free=True)
                break
            except (kering.AuthError, ValueError):
                await self.page.snack(f"Invalid Username or Passcode, please try again...")
                return

        rgy = credentialing.Regery(
            hby=hby, name=hby.name, base=self.app.base, temp=False)
        self.app.agent = agenting.runController(app=self, hby=hby, rgy=rgy)
        # self.page.appbar.actions.remove(self.disconnected)
        # self.page.appbar.actions.insert(0, self.connected)

        self.app.reloadNotes()
        self.app.reloadWitnessesAndMembers()

        if self.connectDialog.data is not None:
            await self.app.switchPane(self.connectDialog.data)

        await self.page.update_async()
