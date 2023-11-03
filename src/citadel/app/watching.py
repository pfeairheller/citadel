import io
import base64
from time import sleep

import flet as ft
import qrcode
from flet_core import padding


class Watchers(ft.Column):

    def __init__(self, app):
        self.app = app

        self.title = ft.Text("Watchers", size=32)
        self.list = ft.Column([], spacing=0, expand=True)
        self.card = ft.Container(
            content=self.list,
            padding=padding.only(left=10, top=15), expand=True,
            alignment=ft.alignment.top_left
        )

        super(Watchers, self).__init__([
            ft.Row([ft.Icon(ft.icons.SCREEN_SEARCH_DESKTOP_OUTLINED, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True, scroll=ft.ScrollMode.ALWAYS)

    async def addWatcher(self, _):
        self.title.value = "Create Watcher"
        self.app.page.floating_action_button = None

        watcherPanel = CreateWatcherPanel(self.app)
        self.card.content = watcherPanel
        await self.card.update_async()
        await self.app.page.update_async()

        await watcherPanel.update_async()

    def setWatchers(self, watchers):
        self.title.value = "Watchers"
        self.card.content = self.list
        self.list.controls.clear()
        icon = ft.icons.SCREEN_SEARCH_DESKTOP_OUTLINED
        tip = "Watcher"

        for watcher in watchers:
            tile = ft.ListTile(
                leading=ft.Icon(icon, tooltip=tip),
                title=ft.Text(watcher['alias']),
                subtitle=ft.Text(watcher['id'], font_family="SourceCodePro"),
                trailing=ft.PopupMenuButton(
                    tooltip=None,
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, on_click=self.viewWatcher,
                                         data=watcher['id']),
                        ft.PopupMenuItem(text="Delete", icon=ft.icons.DELETE_FOREVER),
                    ],
                ),
            )
            self.list.controls.append(tile)

        self.update_async()

    async def viewWatcher(self, e):
        name = e.control.data
        identifiers = self.app.hby.identifiers()
        aid = identifiers.get(name=name)

        viewPanel = ViewWatcherPanel(self.app, aid)
        self.card.content = viewPanel
        await self.card.update_async()
        await self.app.page.update_async()

        await viewPanel.update_async()

    def build(self):
        return ft.Column([
            ft.Row([ft.Icon(ft.icons.PEOPLE_ALT_SHARP, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True)


class CreateWatcherPanel(ft.UserControl):

    def __init__(self, app):
        self.app = app
        super(CreateWatcherPanel, self).__init__()

        self.alias = ft.TextField(label="Alias", border_color=ft.colors.BLUE_400)
        self.oobi = ft.TextField(label="OOBI", width=400, border_color=ft.colors.BLUE_400)

    async def createWatcher(self, _):

        if self.alias.value == "":
            return

        if self.oobi.value == "":
            return

        self.page.snack_bar = ft.SnackBar(ft.Text(f"Creating watcher {self.alias.value}..."), duration=5000)
        self.page.snack_bar.open = True
        await self.page.update_async()

        oobis = self.app.hby.oobis()
        operations = self.app.hby.operations()
        op = oobis.resolve(oobi=self.oobi.value, alias=self.alias.value)

        while not op["done"]:
            op = operations.get(op["name"])
            sleep(1)

        self.page.snack_bar = ft.SnackBar(ft.Text(f"Watcher {self.alias.value} created!"), duration=2000)
        self.page.snack_bar.open = True
        await self.page.update_async()

        self.reset()
        self.app.showWatchers()

    def loadWitnesses(self):
        return [ft.dropdown.Option(wit['id']) for wit in self.app.watchers]

    def cancel(self, _):
        self.reset()
        self.app.showWatchers()

    def reset(self):
        self.alias.value = ""
        self.oobi.value = ""

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.alias
                ]),
                ft.Column([
                    self.oobi
                ]),
                ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(top=10, bottom=10)),
                ft.Row([
                    ft.TextButton("Create", on_click=self.createWatcher),
                    ft.TextButton("Cancel", on_click=self.cancel)
                ])
            ], spacing=35, scroll=ft.ScrollMode.AUTO),
            expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))


class ViewWatcherPanel(ft.UserControl):

    def __init__(self, app, aid):
        self.app = app
        self.aid = aid

        if "salty" in aid:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Hierarchical Key Chain Identifier", weight=ft.FontWeight.BOLD),
            ])
        elif "randy" in aid:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Random Key Generation Identifier", weight=ft.FontWeight.BOLD),
            ])
        if "group" in aid:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Group Multisig Identifier", weight=ft.FontWeight.BOLD),
            ])

        self.publicKeys = ft.Column()
        for idx, key in enumerate(self.aid["state"]['k']):
            self.publicKeys.controls.append(ft.Row([
                ft.Text(str(idx + 1)),
                ft.Text(key, font_family="SourceCodePro")
            ]))

        oobis = self.app.hby.oobis()
        self.oobiTabs = ft.Column()

        async def copy(e):
            self.app.page.set_clipboard(e.control.data)

            self.page.snack_bar = ft.SnackBar(ft.Text(f"OOBI URL Copied!"), duration=2000)
            self.page.snack_bar.open = True
            await self.page.update_async()

        for role in ('agent', 'mailbox', 'witness'):
            res = oobis.get(self.aid['name'], role=role)
            oobi = res['oobis']

            if len(oobi) == 0:
                continue

            img = qrcode.make(oobi[0])
            f = io.BytesIO()
            img.save(f)
            f.seek(0)

            self.oobiTabs.controls.append(ft.Column([
                ft.Row([
                    ft.Text(role.capitalize(), weight=ft.FontWeight.BOLD),
                ]),
                ft.Row([
                    ft.Image(src_base64=base64.b64encode(f.read()).decode('utf-8'), width=175)
                ]),
                ft.Row([
                    ft.Text(value=oobi[0], tooltip=oobi[0], max_lines=3, size=12, overflow=ft.TextOverflow.ELLIPSIS,
                            weight=ft.FontWeight.BOLD, font_family="SourceCodePro", width=300),

                    ft.IconButton(icon_color=ft.colors.BLUE_400, icon=ft.icons.COPY_SHARP, data=oobi[0],
                                  on_click=copy)
                ]),
                ft.Container(padding=ft.padding.only(top=6)),

            ]))

        super(ViewWatcherPanel, self).__init__()

    def build(self):
        return ft.Container(ft.Column([
            ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(bottom=10)),
            ft.Row([
                ft.Text("Alias:", weight=ft.FontWeight.BOLD, width=175, size=14),
                ft.Text(self.aid["name"], size=14, weight=ft.FontWeight.BOLD)
            ]),
            ft.Row([
                ft.Text("Prefix:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text(self.aid["prefix"], font_family="SourceCodePro")
            ]),
            ft.Row([
                ft.Text("Sequence Number:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text(self.aid["state"]['s'])
            ]),
            self.typePanel,
            ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(top=10, bottom=10)),
            ft.Column([
                ft.Row([
                    ft.Text("Witnesses:", weight=ft.FontWeight.BOLD, width=175),
                ]),
                ft.Row([
                    ft.Text("Count:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(self.aid["state"]['b'])))
                ]),
                ft.Row([
                    ft.Text("Receipt:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(self.aid["windexes"])))
                ]),
                ft.Row([
                    ft.Text("Threshold:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(self.aid["state"]['bt'])
                ]),
            ]),
            ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("Public Keys:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.publicKeys, padding=ft.padding.only(left=40)),
            ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("OOBIs:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.oobiTabs),
            ft.Container(content=ft.Divider(color=ft.colors.BLUE_400), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.TextButton("Close", on_click=self.close)
            ]),
        ]), expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))

    def close(self, _):
        self.app.showIdentifiers()
