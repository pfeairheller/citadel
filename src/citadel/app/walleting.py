from time import sleep

import flet as ft
from keri.vdr import credentialing

from citadel.core import agenting
from citadel.tasks import oobiing
from keri import kering
from keri.app import configing, habbing, keeping, connecting, directing
from keri.app.keeping import Algos
from keri.core import eventing, coring
from keri.core.coring import Tiers
from citadel.app import identifying, contacting, setting

SALT = "0ACDEyMzQ1Njc4OWxtbm9dEf"
CONFIG_FILE = 'demo-witness-oobis-schema'

DEFAULT_USERNAME = "citadel"
DEFAULT_PASSCODE = "DoB26Fj4x9LboAFWJra17O"


class CitadelApp:

    def __init__(self, page):
        self.page = page
        self.agent = None
        self.notifier = None
        self.rail = None
        self.temp = False
        self.tier = Tiers.low
        self.algo = Algos.salty
        self.salt = coring.randomNonce()[2:23]
        self.base = ""

        self.notes = []
        self.witnesses = []
        self.members = []

        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.title = "Citadel"

        self.page.window_width = 800
        self.page.window_height = 600

        self.username = ft.TextField(value=DEFAULT_USERNAME)
        self.passcode = ft.TextField(value=DEFAULT_PASSCODE, password=True)

        column = ft.Column([
            ft.Text("Name"),
            self.username,
            ft.Text("Passcode"),
            self.passcode
        ])

        self.connectDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Open Wallet"),
            content=column,
            actions=[
                ft.TextButton("Open", on_click=self.connect),
                ft.TextButton("Cancel", on_click=self.cancel_connect),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,


        )
        self.inceptionData = ft.Text(value="", tooltip="Inception Data", max_lines=10, size=12,
                                     overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD,
                                     font_family="SourceCodePro", width=300)

        self.initializeDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agent Initialization"),
            content=ft.Column([
                ft.Text("New Username"),
                self.username,
                ft.Text("New Passcode"),
                self.passcode,
            ]),
            actions=[
                ft.TextButton("Create", on_click=self.generateHby),
                ft.TextButton("Cancel", on_click=self.closeInitialize),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.inceptionData = ft.Text(value="", tooltip="Inception Data", max_lines=10, size=12,
                                     overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD,
                                     font_family="SourceCodePro", width=300)

        self.main = ft.Column(
            [self.splash],
            alignment=ft.alignment.top_left, expand=1)

        self.disconnected = ft.IconButton(ft.icons.LINK_OFF_SHARP, icon_color="red", tooltip="Disconnected",
                                          on_click=self.open_dlg_modal)
        self.connected = ft.IconButton(ft.icons.LINK_SHARP,
                                       icon_color="#51dac5", tooltip="Connected", on_click=self.open_dlg_modal)

        self.notificationsButton = ft.IconButton(ft.icons.NOTIFICATIONS_NONE_SHARP, on_click=self.showNotifications)
        page.appbar = ft.AppBar(
            leading=ft.Container(ft.Image(src="gleif-logo-new.svg", width=40),
                                 padding=ft.padding.only(left=10)),
            leading_width=40,
            title=ft.Text("Citadel"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                self.disconnected,
                self.notificationsButton,
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Open", on_click=self.open_dlg_modal),
                        ft.PopupMenuItem(text="Initialize", on_click=self.initialize),
                        ft.PopupMenuItem(text="Exit", on_click=self.exitApp),
                    ]
                ),
            ],
        )

        # All Panels
        self.notifications = Notifications(self)
        self.identifiers = identifying.Identifiers(self)
        self.contacts = contacting.Contacts(self)
        self.credentials = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Type")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Issued Date")),
            ]
        )
        self.settings = setting.Settings(self)

    @property
    def splash(self):
        return ft.Column([
            ft.Row([
                ft.Container(ft.Image(src="gleif-logo-new.svg", height=200),
                             expand=True)
            ], expand=True),
            ft.Row([ft.Text(
                "Click on the red link to connect",
                italic=True, color="red",
                text_align=ft.TextAlign.CENTER,
                expand=True, size=14
            )]),
        ], expand=True)

    async def switchPane(self, idx):
        match idx:
            case 0:
                if self.agent is None:
                    await self.open_dlg_modal(idx)
                    return

                await self.showIdentifiers()
            case 1:
                if self.agent is None:
                    await self.open_dlg_modal(idx)
                    return

                self.showWitnesses()
            case 2:
                if self.agent is None:
                    await self.open_dlg_modal(idx)
                    return

                await self.showCredentials()
            case 3:
                if self.agent is None:
                    await self.open_dlg_modal(idx)
                    return

                await self.showContacts()

            case 4:
                await self.showSettings()

    async def showNotifications(self, e=None):
        self.main.controls.pop()
        self.main.controls.append(self.notifications)
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

    async def showIdentifiers(self):
        self.main.controls.pop()
        self.main.controls.append(self.identifiers)
        await self.main.update_async()
        await self.refreshIdentifiers()
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=self.identifiers.add_identifier, bgcolor="#51dac5"
        )
        await self.page.update_async()

    async def refreshIdentifiers(self):
        aids = self.agent.hby.habs.values()

        await self.identifiers.setIdentifiers(aids)
        await self.identifiers.update_async()

    async def showCredentials(self):
        self.main.controls.pop()
        self.main.controls.append(self.credentials)
        self.page.floating_action_button = None
        await self.main.update_async()
        await self.page.update_async()
        self.refreshCredentials()

    def refreshCredentials(self):
        pass

    async def showContacts(self):
        self.main.controls.pop()
        self.main.controls.append(self.contacts)
        await self.main.update_async()
        await self.refreshContacts()
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=self.contacts.addContact, bgcolor="#51dac5"
        )
        await self.page.update_async()

    async def refreshContacts(self):
        org = connecting.Organizer(hby=self.agent.hby)
        contacts = []
        for c in org.list():
            aid = c['id']
            accepted = [saider.qb64 for saider in self.agent.hby.db.chas.get(keys=(aid,))]
            received = [saider.qb64 for saider in self.agent.hby.db.reps.get(keys=(aid,))]
            valid = set(accepted) & set(received)

            challenges = []
            for said in valid:
                exn = self.agent.hby.db.exns.get(keys=(said,))
                challenges.append(dict(dt=exn.ked['dt'], words=exn.ked['a']['words']))

            c["challenges"] = challenges

            wellKnowns = []
            wkans = self.agent.hby.db.wkas.get(keys=(aid,))
            for wkan in wkans:
                wellKnowns.append(dict(url=wkan.url, dt=wkan.dt))

            c["wellKnowns"] = wellKnowns

            contacts.append(c)

        await self.contacts.setContacts(contacts)
        await self.contacts.update_async()

    def showWitnesses(self):
        pass

    async def showSettings(self):
        self.main.controls.pop()
        self.main.controls.append(self.settings)
        await self.main.update_async()
        self.page.floating_action_button = None
        await self.page.update_async()

    async def cancel_connect(self, e):
        self.connectDialog.open = False
        await self.page.update_async()

    async def initialize(self, e):
        self.connectDialog.open = False
        await self.page.update_async()

        self.page.dialog = self.initializeDialog
        self.initializeDialog.open = True
        await self.page.update_async()

    async def closeInitialize(self, e):
        self.initializeDialog.open = False
        await self.page.update_async()

    async def generateHby(self, e):
        self.initializeDialog.open = False
        cf = configing.Configer(name="demo-witness-oobis-schema",
                                base="",
                                headDirPath="./",
                                temp=False,
                                reopen=True,
                                clear=False)
        print(f"loading {cf.path}")
        kwa = dict()

        kwa["salt"] = coring.Salter(raw=self.salt.encode("utf-8")).qb64
        kwa["bran"] = self.passcode.value
        kwa["algo"] = self.algo
        kwa["tier"] = self.tier

        hby = habbing.Habery(name=self.username.value,
                             base=self.base, temp=self.temp, cf=cf, **kwa)

        directing.runController([oobiing.OOBILoader(hby=hby)])
        directing.runController([oobiing.OOBIAuther(hby=hby)])

        hby.close()
        await self.page.update_async()

    async def connect(self, e):
        self.connectDialog.open = False
        bran = self.passcode.value

        cf = configing.Configer(name=CONFIG_FILE,
                                base="",
                                headDirPath=".",
                                temp=False,
                                reopen=True,
                                clear=False)

        ks = keeping.Keeper(name=self.username.value,
                            temp=False,
                            cf=cf,
                            reopen=True)

        aeid = ks.gbls.get('aeid')
        if aeid is None:
            print("Keystore must already exist, exiting")
            await self.snack(f"Invalid Username or Passcode, please try again...")
            return

        ks.close()

        while True:
            try:
                if bran:
                    bran = bran.replace("-", "")

                hby = habbing.Habery(name=self.username.value, bran=bran, cf=cf, free=True)
                break
            except (kering.AuthError, ValueError):
                await self.snack(f"Invalid Username or Passcode, please try again...")
                return

        rgy = credentialing.Regery(hby=hby, name=hby.name, base=self.base, temp=self.temp)
        self.agent = agenting.runController(app=self, hby=hby, rgy=rgy)
        self.page.appbar.actions.remove(self.disconnected)
        self.page.appbar.actions.insert(0, self.connected)

        self.reloadNotes()
        self.reloadWitnessesAndMembers()

        if self.connectDialog.data is not None:
            await self.switchPane(self.connectDialog.data)

        await self.page.update_async()

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
        async def switch(e):
            await self.switchPane(e.control.selected_index)

        self.rail = ft.NavigationRail(
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.PEOPLE_ALT_SHARP, selected_icon=ft.icons.PEOPLE_ALT_OUTLINED, label="Identifers"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.FRONT_HAND_ROUNDED),
                    selected_icon_content=ft.Icon(ft.icons.FRONT_HAND_OUTLINED),
                    label="Witnesses",
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
            ],
            on_change=switch,
        )

        return ft.Row(
            [
                self.rail,
                ft.VerticalDivider(width=1),
                self.main,
            ],
            expand=True,
        )

    async def open_dlg_modal(self, idx):
        self.page.dialog = self.connectDialog
        self.connectDialog.open = True
        self.connectDialog.data = idx
        await self.page.update_async()

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


class Notifications(ft.Container):

    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.selected = None

        self.title = ft.Text("Notifications", size=32)
        self.list = ft.Column(spacing=0)
        self.card = ft.Card(
            content=ft.Container(
                content=self.list,
                padding=ft.padding.symmetric(vertical=10, horizontal=5),
                alignment=ft.alignment.top_left, expand=True
            ), expand=True)
        super(Notifications, self).__init__(expand=True, alignment=ft.alignment.top_left)

    async def setNotes(self, notes):
        self.list.controls.clear()
        for note in notes:
            attrs = note['a']
            route = attrs['r']
            match route:
                case "/multisig/icp":
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.icons.PEOPLE_SHARP),
                        title=ft.Text("Group Inception Request"),
                        trailing=ft.PopupMenuButton(
                            tooltip=None,
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.view),
                                ft.PopupMenuItem(text="Delete", icon=ft.icons.DELETE_FOREVER),
                            ],
                        ),
                    )
                    self.list.controls.append(tile)
                case "/multisig/vcp":
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.icons.BADGE_ROUNDED),
                        title=ft.Text("Group Credential Registry Inception Request"),
                        trailing=ft.PopupMenuButton(
                            tooltip=None,
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.view),
                                ft.PopupMenuItem(text="Delete", icon=ft.icons.DELETE_FOREVER),
                            ],
                        ),
                    )
                    self.list.controls.append(tile)
                case "/multisig/iss":
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.icons.BADGE_SHARP),
                        title=ft.Text("Group Credential Creation Request"),
                        trailing=ft.PopupMenuButton(
                            tooltip=None,
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.viewIss),
                                ft.PopupMenuItem(text="Delete", icon=ft.icons.DELETE_FOREVER),
                            ],
                        ),
                    )
                    self.list.controls.append(tile)

        await self.update_async()

    def view(self, e=None):
        note = e.control.data
        self.selected = note

        attrs = note['a']
        said = attrs['d']

        res = None
        if not res:
            return

        req = res[0]
        exn = req['exn']
        payload = exn['a']
        usage = payload["usage"]
        self.title.value = "Group Credential Registry Creation"
        self.card.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Request For Group: ", width=275, size=16),
                    ft.Text(f"{req['groupName']}", size=20)
                ]),
                ft.Row([
                    ft.Text("Request Sent From: ", width=275, size=16),
                    ft.Text(f"{req['sender']}", size=20)
                ]),
                ft.Row([
                    ft.Text("Usage: ", width=275, size=16),
                    ft.Text(f"{usage}", size=20)
                ]),
                ft.Row(),
                ft.Row([
                    ft.TextButton("Approve", on_click=self.approveVcp, data=req),
                    ft.TextButton("Reject"),
                    ft.TextButton("Cancel")
                ])
            ]),
            padding=ft.padding.symmetric(vertical=10))
        self.update_async()

    def viewIss(self, e=None):
        groups = self.client.groups()

        note = e.control.data
        self.selected = note

        attrs = note['a']
        said = attrs['d']

        res = groups.get_request(said=said)
        if not res:
            return

        req = res[0]
        exn = req['exn']
        self.title.value = "Group Credential Creation"

        data = ft.DataTable([
            ft.DataColumn(ft.Text("Field")),
            ft.DataColumn(ft.Text("Value"))
        ])

        acdc = exn['e']['acdc']
        for k, v in acdc['a'].items():
            if k in ('i', 'd'):
                continue
            data.rows.append(
                ft.DataRow([
                    ft.DataCell(ft.Text(k)),
                    ft.DataCell(ft.Text(v))
                ])
            )

        schemaType = "Qualified vLEI Issuer Credential"
        self.card.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Request For Credential: ", width=275, size=16),
                    ft.Text(f"{req['groupName']}", size=20)
                ]),
                ft.Row([
                    ft.Text("Request Sent From: ", width=275, size=16),
                    ft.Text(f"{req['sender']}", size=20)
                ]),
                ft.Row([
                    ft.Text("Credential Type: ", width=275, size=16),
                    ft.Text(f"{schemaType}", size=20)
                ]),
                data,
                ft.Row([
                    ft.TextButton("Approve", on_click=self.approveVcp, data=req),
                    ft.TextButton("Reject"),
                    ft.TextButton("Cancel")
                ])
            ]),
            padding=ft.padding.symmetric(vertical=10))
        self.update_async()

    async def approveVcp(self, e):
        req = e.control.data
        exn = req['exn']
        exchanges = self.client.exchanges()
        identifiers = self.client.identifiers()
        registries = self.client.registries()
        operations = self.client.operations()

        ghab = identifiers.get(req["groupName"])
        embeds = exn['e']
        vcp = coring.Serder(ked=embeds['vcp'])
        iserder = coring.Serder(ked=embeds['anc'])
        keeper = self.client.manager.get(aid=ghab)
        sigs = keeper.sign(ser=iserder.raw)

        op = registries.create_from_events(ghab, "vLEI", vcp=vcp.ked, ixn=iserder.ked, sigs=sigs)

        embeds = dict(
            vcp=vcp.raw,
            anc=eventing.messagize(serder=iserder, sigers=[coring.Siger(qb64=sig) for sig in sigs])
        )

        recp = ["EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4", "EJccSRTfXYF6wrUVuenAIHzwcx3hJugeiJsEKmndi5q1"]
        exchanges.send("multisig3", "multisig", sender=ghab['group']['mhab'], route="/multisig/vcp",
                       payload=dict(gid=ghab["prefix"], usage="Issue vLEIs"),
                       embeds=embeds, recipients=recp)

        while not op["done"]:
            op = operations.get(op["name"])
            sleep(1)

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Credential Registry Created"),
            content=ft.Text("Do you want to delete this notification?"),
            actions=[
                ft.TextButton("Yes", on_click=self.deleteNote),
                ft.TextButton("No", on_click=self.dismiss),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dlg_modal
        dlg_modal.open = True
        await self.page.update_async()

    def deleteNote(self, e):
        if self.selected is not None:
            notifications = self.client.notifications()
            notifications.delete(self.selected['i'])

        self.dismiss(e)

    async def dismiss(self, e):
        self.page.dialog.open = False
        self.app.reloadNotes()
        await self.setNotes(self.app.notes)

        self.title.value = "Notifications"
        self.card.content = self.list
        await self.update_async()
        await self.page.update_async()

    def build(self):
        return ft.Column([
            ft.Row([ft.Icon(ft.icons.NOTIFICATIONS_NONE, size=32), self.title]),
            ft.Row([self.card])
        ])
