import flet as ft

from citadel.app import notifying, identifying, contacting, setting, splashing
from citadel.app.colouring import Brand


# from navbar import Navbar


class Layout(ft.Row):
    def __init__(self, app, page: ft.Page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.page = page
        self.navbar = Navbar(self, page)
        self.notifications = notifying.Notifications(app)
        self.identifiers = identifying.Identifiers(app)
        self.contacts = contacting.Contacts(app)
        self.credentials = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Type")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Issued Date")),
            ]
        )
        self.settings = setting.Settings(app)
        self.splash = splashing.Splash().build()

        self._active_view = self.splash

        if self.app.agent is None:
            self.navbar.visible = False

        self.controls = [self.navbar, self.active_view]

    @property
    def active_view(self):
        return self._active_view

    @active_view.setter
    def active_view(self, view):
        self._active_view = view
        self.controls[-1] = self._active_view

    async def set_identifiers_view(self):
        self.active_view = self.identifiers
        self.navbar.rail.selected_index = Navbar.IDENTIFIERS
        await self.navbar.update_async()
        await self.page.update_async()

    async def set_contacts_view(self):
        print("contacts")
        self.active_view = self.identifiers
        self.navbar.rail.selected_index = 0
        await self.navbar.update_async()
        await self.page.update_async()

    async def set_credentials_view(self):
        print("credentials")
        self.active_view = self.identifiers
        self.navbar.rail.selected_index = 0
        await self.navbar.update_async()
        await self.page.update_async()

    async def set_settings_view(self):
        print("settings")
        self.active_view = self.settings
        self.navbar.rail.selected_index = Navbar.SETTINGS
        await self.navbar.update_async()
        await self.page.update_async()

    async def set_splash_view(self):
        print("splash")
        self.active_view = self.splash
        self.navbar.rail.selected_index = None
        await self.navbar.update_async()
        await self.page.update_async()

    async def set_oh_no_view(self):
        print("oh no!")


class Navbar(ft.UserControl):
    IDENTIFIERS = 0
    WITNESSES = 1
    CREDENTIALS = 2
    CONTACTS = 3
    SETTINGS = 4

    def __init__(self, layout: Layout, page: ft.Page):
        super().__init__()
        self.layout = layout
        self.page = page

        destinations = [
            ft.NavigationRailDestination(
                icon=ft.icons.PEOPLE_ALT_SHARP,
                selected_icon=ft.icons.PEOPLE_ALT_OUTLINED,
                label="Identifiers"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.BADGE_SHARP),
                selected_icon_content=ft.Icon(ft.icons.BADGE_OUTLINED),
                label="Credentials",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.CONTACTS_SHARP),
                selected_icon_content=ft.Icon(ft.icons.CONTACTS_OUTLINED),
                label="Contacts",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text("Settings"),
            ),
        ]

        self.rail = ft.NavigationRail(
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            destinations=destinations,
            on_change=self.nav_change,
            expand=True,
        )

    def build(self):
        return self.rail

    async def nav_change(self, e):
        index = e if (type(e) is int) else e.control.selected_index
        self.rail.selected_index = None
        if index == self.IDENTIFIERS:
            self.page.route = "/identifiers"
        elif index == self.CREDENTIALS:
            self.page.route = "/credentials"
        elif index == self.CONTACTS:
            self.page.route = "/contacts"
        elif index == self.SETTINGS:
            self.page.route = "/settings"

        await self.page.update_async()

    async def show_identifiers(self):
        # self.main.controls.pop()
        # self.main.controls.append(self.identifiers)
        # await self.main.update_async()
        await self.refresh_identifiers()
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=self.layout.identifiers.add_identifier, bgcolor=Brand.SECONDARY
        )
        await self.page.update_async()

    async def refresh_identifiers(self):
        aids = self.layout.app.agent.hby.habs.values()

        await self.layout.identifiers.setIdentifiers(aids)
        await self.layout.identifiers.update_async()
