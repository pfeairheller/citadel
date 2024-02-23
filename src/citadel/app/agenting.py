import flet as ft
from keri.app import configing, habbing, directing
from keri.core import coring

from citadel.app.colouring import Brand
from citadel.tasks import oobiing

DEFAULT_USERNAME = "citadel"
DEFAULT_PASSCODE = "DoB26Fj4x9LboAFWJra17O"


class AgentInitialization(ft.UserControl):

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
        print(f"loading {cf.path}")
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

        agents = []
        if await self.page.client_storage.contains_key_async("gleif.citadel.agents"):
            agents = await self.page.client_storage.get_async("gleif.citadel.agents")

        agents.append(self.username.value)

        actions = []
        for a in agents:
            actions.append(ft.PopupMenuItem(text=a, on_click=self.open), )

        await self.page.client_storage.set_async("gleif.citadel.agents", agents)
        await self.page.update_async()


class AgentConnection(ft.UserControl):

    def __init__(self):
        super(AgentConnection, self).__init__()
