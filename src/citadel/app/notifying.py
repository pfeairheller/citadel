from time import sleep

import flet as ft
from keri.core import eventing, coring


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
        super(Notifications, self).__init__(
            expand=True, alignment=ft.alignment.top_left)

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
                                ft.PopupMenuItem(
                                    text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.view),
                                ft.PopupMenuItem(
                                    text="Delete", icon=ft.icons.DELETE_FOREVER),
                            ],
                        ),
                    )
                    self.list.controls.append(tile)
                case "/multisig/vcp":
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.icons.BADGE_ROUNDED),
                        title=ft.Text(
                            "Group Credential Registry Inception Request"),
                        trailing=ft.PopupMenuButton(
                            tooltip=None,
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.view),
                                ft.PopupMenuItem(
                                    text="Delete", icon=ft.icons.DELETE_FOREVER),
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
                                ft.PopupMenuItem(
                                    text="View", icon=ft.icons.PAGEVIEW, data=note, on_click=self.viewIss),
                                ft.PopupMenuItem(
                                    text="Delete", icon=ft.icons.DELETE_FOREVER),
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
                    ft.TextButton(
                        "Approve", on_click=self.approveVcp, data=req),
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
                    ft.TextButton(
                        "Approve", on_click=self.approveVcp, data=req),
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

        op = registries.create_from_events(
            ghab, "vLEI", vcp=vcp.ked, ixn=iserder.ked, sigs=sigs)

        embeds = dict(
            vcp=vcp.raw,
            anc=eventing.messagize(serder=iserder, sigers=[
                coring.Siger(qb64=sig) for sig in sigs])
        )

        recp = ["EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4",
                "EJccSRTfXYF6wrUVuenAIHzwcx3hJugeiJsEKmndi5q1"]
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
