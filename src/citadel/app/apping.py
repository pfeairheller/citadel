from pathlib import Path

import flet as ft
from keri.app import connecting
from keri.app.keeping import Algos
from keri.core import coring
from keri.core.coring import Tiers

from citadel.app import drawing
from citadel.app.colouring import Brand
from citadel.app.layout import Layout

SALT = "0ACDEyMzQ1Njc4OWxtbm9dEf"
CONFIG_FILE = 'demo-witness-oobis-schema'


class CitadelApp:

    def __init__(self, page: ft.Page):
        super().__init__()
        self.layout = None
        self.page = page
        self.agent = None
        self.notifier = None
        self.rail = None
        self.notes = []
        self.witnesses = []
        self.members = []
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.title = "Citadel"
        self.page.window_width = 1024
        self.page.window_height = 768
        self.page.on_route_change = self.route_change
        self.base = ""
        self.temp = False
        self.tier = Tiers.low
        self.algo = Algos.salty
        self.salt = coring.randomNonce()[2:23]
        self.agentDrawer = drawing.AgentDrawer(app=self, page=page, open=True)
        self.agentDrawerButton = ft.IconButton(ft.icons.WALLET_ROUNDED,
                                               tooltip="Agents", on_click=self.toggle_drawer)

        self.notificationsButton = ft.IconButton(
            ft.icons.NOTIFICATIONS_NONE_SHARP, on_click=self.showNotifications)

        actions = [self.agentDrawerButton]
        if self.agent is not None:
            actions = [
                self.notificationsButton,
            ]

        self.page.appbar = ft.AppBar(
            leading=ft.Container(ft.Image(src="gleif-logo-new.svg", width=40),
                                 padding=ft.padding.only(left=10), opacity=0.5),
            leading_width=40,
            title=ft.Text("Citadel"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=actions
        )

        # self.inceptionData = ft.Text(value="", tooltip="Inception Data", max_lines=10, size=12,
        #                              overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD,
        #                              font_family="SourceCodePro", width=300)
        #
        # self.inceptionData = ft.Text(value="", tooltip="Inception Data", max_lines=10, size=12,
        #                              overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD,
        #                              font_family="SourceCodePro", width=300)

        # nav
        # detail

        # start up
        # [self.splash],
        # alignment=ft.alignment.top_left, expand=1

        # self.main = ft.Column()
        #
        # self.uninitialized = ft.IconButton(ft.icons.CIRCLE_OUTLINED, icon_color=Brand.RED,
        #                                    tooltip="Uninitialized", on_click=self.open_init_modal)
        #
        # self.disconnected = ft.IconButton(ft.icons.LINK_OFF_SHARP, icon_color="red",
        #                                   tooltip="Disconnected",
        #                                   on_click=self.open_dlg_modal)
        # self.connected = ft.IconButton(ft.icons.LINK_SHARP,
        #                                icon_color=Brand.SECONDARY, tooltip="Connected", on_click=self.open_dlg_modal)
        #
        #
        # self.agentList = ft.PopupMenuButton(icon=ft.icons.WALLET_SHARP, items=[])

    async def toggle_drawer(self, _):
        self.page.end_drawer = self.agentDrawer.build()
        await self.page.show_end_drawer_async(self.page.end_drawer)
        await self.page.end_drawer.update_async()

    async def route_change(self, _):
        tr = ft.TemplateRoute(self.page.route)
        if tr.match("/"):
            await self.page.go_async("/splash")
        elif tr.match("/identifiers"):
            await self.layout.set_identifiers_list()
        elif tr.match("/identifiers/:prefix/view"):
            await self.layout.set_identifier_view(tr.prefix)
        elif tr.match("/witnesses"):
            await self.layout.set_witnesses_view()
        elif tr.match("/credentials"):
            await self.layout.set_credentials_view()
        elif tr.match("/contacts"):
            await self.layout.set_contacts_view()
        elif tr.match("/settings"):
            await self.layout.set_settings_view()
        elif tr.match("/splash"):
            await self.layout.set_splash_view()
        else:
            await self.layout.set_oh_no_view()

        await self.page.update_async()

    async def showNotifications(self, e=None):
        # self.main.controls.pop()
        # self.main.controls.append(self.notifications)
        self.page.floating_action_button = None

        await self.page.update_async()
        self.reloadNotes()
        await self.notifications.setNotes(self.notes)
        self.rail.selected_index = None

    def reloadNotes(self):
        if self.notifier is None:
            return

        count = self.notifier.getNoteCnt()
        self.notes = self.notifier.getNotes(start=0, end=count)

        if len(self.notes) == 0:
            self.notificationsButton.icon = ft.icons.NOTIFICATIONS_NONE_SHARP
        else:
            self.notificationsButton.icon = ft.icons.NOTIFICATIONS_ACTIVE_SHARP
            self.notificationsButton.icon_color = "yellow"

    async def showCredentials(self):
        # self.main.controls.pop()
        # self.main.controls.append(self.credentials)
        self.page.floating_action_button = None
        # await self.main.update_async()
        await self.page.update_async()
        self.refreshCredentials()

    def refreshCredentials(self):
        pass

    async def showContacts(self):
        # self.main.controls.pop()
        # self.main.controls.append(self.contacts)
        # await self.main.update_async()
        await self.refreshContacts()
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=self.contacts.addContact, bgcolor=Brand.SECONDARY
        )
        await self.page.update_async()

    async def refreshContacts(self):
        org = connecting.Organizer(hby=self.agent.hby)
        contacts = []
        for c in org.list():
            aid = c['id']
            accepted = [
                saider.qb64 for saider in self.agent.hby.db.chas.get(keys=(aid,))]
            received = [
                saider.qb64 for saider in self.agent.hby.db.reps.get(keys=(aid,))]
            valid = set(accepted) & set(received)

            challenges = []
            for said in valid:
                exn = self.agent.hby.db.exns.get(keys=(said,))
                challenges.append(
                    dict(dt=exn.ked['dt'], words=exn.ked['a']['words']))

            c["challenges"] = challenges

            wellKnowns = []
            wkans = self.agent.hby.db.wkas.get(keys=(aid,))
            for wkan in wkans:
                wellKnowns.append(dict(url=wkan.url, dt=wkan.dt))

            c["wellKnowns"] = wellKnowns

            contacts.append(c)

        await self.contacts.setContacts(contacts)
        await self.contacts.update_async()

    def reloadWitnessesAndMembers(self):
        org = connecting.Organizer(hby=self.agent.hby)

        self.witnesses.clear()
        self.members.clear()
        for contact in org.list():
            prefixer = coring.Prefixer(qb64=contact['id'])
            if not prefixer.transferable:
                self.witnesses.append(contact)
            else:
                self.members.append(contact)

    def build(self):
        self.layout = Layout(
            self,
            self.page,
            tight=True,
            expand=True,
            vertical_alignment="start",
        )
        return self.layout

    # on_change
    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent):
        self._agent = agent
        if self._agent is not None:
            self.layout.navbar.visible = True

    async def exitApp(self, e):
        await self.page.window_destroy_async()

    async def snack(self, message, duration=5000):
        self.page.snack_bar = ft.SnackBar(ft.Text(message),
                                          duration=duration)
        self.page.snack_bar.open = True
        await self.page.update_async()

    @property
    def hby(self):
        return self.agent.hby if self.agent is not None else None

    @staticmethod
    def environments():
        dbhome = Path("/usr/local/var/keri/db")
        if not dbhome.exists():
            dbhome = Path(f"{Path.home()}/.keri/db")

        if not dbhome.is_dir():
            return []

        envs = []
        for p in dbhome.iterdir():
            envs.append(p.stem)

        return envs
