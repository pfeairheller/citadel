import base64
import io
from urllib.parse import urlparse, urljoin

import flet as ft
import qrcode
from flet_core import padding, FontWeight
from keri import kering
from keri.app import habbing
from keri.app.keeping import Algos
from keri.core import coring
from keri.db import dbing

from citadel.app.colours import Brand


class Identifiers(ft.Column):

    def __init__(self, app):
        self.app = app

        self.title = ft.Text("Identifiers", size=32)
        self.list = ft.Column([], spacing=0, expand=True)
        self.card = ft.Container(
            content=self.list,
            padding=padding.only(top=15), expand=True,
            alignment=ft.alignment.top_left
        )

        super(Identifiers, self).__init__([
            ft.Row([ft.Icon(ft.icons.PEOPLE_ALT_SHARP, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True, scroll=ft.ScrollMode.ALWAYS)

    async def add_identifier(self, _):
        self.title.value = "Create Identifier"
        self.app.page.floating_action_button = None

        identifierPanel = CreateIdentifierPanel(self.app)
        self.card.content = identifierPanel
        await self.card.update_async()
        await self.app.page.update_async()

        await identifierPanel.update_async()

    async def setIdentifiers(self, habs):
        self.title.value = "Identifiers"
        self.card.content = self.list
        self.list.controls.clear()
        icon = ft.icons.PERSON_SHARP
        tip = "Identifier"
        for hab in habs:
            if isinstance(hab, habbing.GroupHab):
                icon = ft.icons.PEOPLE_ALT_OUTLINED
                tip = "Group Multisig"
            if hab.algo == Algos.salty:
                icon = ft.icons.LINK_OUTLINED
                tip = "Key Chain"
            elif hab.algo == Algos.randy:
                icon = ft.icons.SHUFFLE_OUTLINED
                tip = "Random Key"

            tile = ft.ListTile(
                leading=ft.Icon(icon, tooltip=tip),
                title=ft.Text(hab.name),
                subtitle=ft.Text(hab.pre, font_family="SourceCodePro"),
                trailing=ft.PopupMenuButton(
                    tooltip=None,
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, on_click=self.viewIdentifier,
                                         data=hab),
                        ft.PopupMenuItem(
                            text="Delete", icon=ft.icons.DELETE_FOREVER),
                    ],
                ),
                on_click=self.viewIdentifier,
                data=hab,
            )
            bg = Brand.GRAY_LIGHTER if len(
                self.list.controls) % 2 == 0 else ft.colors.WHITE
            self.list.controls.append(ft.Container(content=tile, bgcolor=bg))

        await self.update_async()

    async def viewIdentifier(self, e):
        hab = e.control.data

        viewPanel = ViewIdentifierPanel(self.app, hab)
        self.card.content = viewPanel
        await self.card.update_async()
        await self.app.page.update_async()

        await viewPanel.update_async()

    def build(self):
        return ft.Column([
            ft.Row([ft.Icon(ft.icons.PEOPLE_ALT_SHARP, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True)


class ViewIdentifierPanel(ft.UserControl):

    def __init__(self, app, hab):
        self.app = app
        self.hab = hab

        if isinstance(hab, habbing.GroupHab):
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Group Multisig Identifier",
                        weight=ft.FontWeight.BOLD),
            ])
        elif hab.algo == Algos.salty:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Hierarchical Key Chain Identifier",
                        weight=ft.FontWeight.BOLD),
            ])
        elif hab.algo == Algos.randy:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Random Key Generation Identifier",
                        weight=ft.FontWeight.BOLD),
            ])

        self.publicKeys = ft.Column()
        for idx, verfer in enumerate(self.hab.kever.verfers):
            self.publicKeys.controls.append(ft.Row([
                ft.Text(str(idx + 1)),
                ft.Text(verfer.qb64, font_family="SourceCodePro")
            ]))

        self.oobiTabs = ft.Column()

        async def copy(e):
            await self.app.page.set_clipboard_async(e.control.data)

            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"OOBI URL Copied!"), duration=2000)
            self.page.snack_bar.open = True
            await self.page.update_async()

        for role in ('agent', 'mailbox', 'witness'):
            oobi = self.loadOOBIs(role)

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
                    ft.Image(src_base64=base64.b64encode(
                        f.read()).decode('utf-8'), width=175)
                ]),
                ft.Row([
                    ft.Text(value=oobi[0], tooltip=oobi[0], max_lines=3, size=12, overflow=ft.TextOverflow.ELLIPSIS,
                            weight=ft.FontWeight.BOLD, font_family="SourceCodePro", width=300),

                    ft.IconButton(icon_color=ft.colors.BLUE_400, icon=ft.icons.COPY_SHARP, data=oobi[0],
                                  on_click=copy)
                ]),
                ft.Container(padding=ft.padding.only(top=6)),

            ]))

        super(ViewIdentifierPanel, self).__init__()

    def build(self):
        kever = self.hab.kever
        ser = kever.serder
        dgkey = dbing.dgKey(ser.preb, ser.saidb)
        wigs = self.hab.db.getWigs(dgkey)
        return ft.Container(ft.Column([
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(bottom=10)),
            ft.Row([
                ft.Text("Alias:", weight=ft.FontWeight.BOLD,
                        width=175, size=14),
                ft.Text(self.hab.name, size=14, weight=ft.FontWeight.BOLD)
            ]),
            ft.Row([
                ft.Text("Prefix:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text(self.hab.pre, font_family="SourceCodePro")
            ]),
            ft.Row([
                ft.Text("Sequence Number:",
                        weight=ft.FontWeight.BOLD, width=175),
                ft.Text(kever.sner.num)
            ]),
            self.typePanel,
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(top=10, bottom=10)),
            ft.Column([
                ft.Row([
                    ft.Text("Establishment Only",
                        weight=ft.FontWeight.BOLD, width=168, size=14),
                    ft.Checkbox(value=True, fill_color=Brand.SECONDARY,
                            disabled=True)], 
                visible=kever.estOnly),
                ft.Row([
                    ft.Text("Do Not Delegate",
                        weight=ft.FontWeight.BOLD, width=168, size=14),
                    ft.Checkbox(value=True, fill_color=Brand.SECONDARY,
                            disabled=True)], 
                visible=kever.estOnly),
            ]),
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(top=10, bottom=10)),
            ft.Column([
                ft.Row([
                    ft.Text("Witnesses:", weight=ft.FontWeight.BOLD, width=175),
                ]),
                ft.Row([
                    ft.Text("Count:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(self.hab.kever.wits)))
                ]),
                ft.Row([
                    ft.Text("Receipt:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(wigs)))
                ]),
                ft.Row([
                    ft.Text("Threshold:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(kever.toader.num)
                ]),
            ]),
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("Public Keys:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.publicKeys,
                         padding=ft.padding.only(left=40)),
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("OOBIs:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.oobiTabs),
            ft.Container(content=ft.Divider(color=Brand.SECONDARY),
                         padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.TextButton("Close", on_click=self.close)
            ]),
        ]), expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))

    def loadOOBIs(self, role):
        if role in (kering.Roles.witness,):  # Fetch URL OOBIs for all witnesses
            oobis = []
            for wit in self.hab.kever.wits:
                urls = self.hab.fetchUrls(eid=wit, scheme=kering.Schemes.http) or self.hab.fetchUrls(
                    eid=wit, scheme=kering.Schemes.https)
                if not urls:
                    return []

                url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
                up = urlparse(url)
                oobis.append(
                    urljoin(up.geturl(), f"/oobi/{self.hab.pre}/witness/{wit}"))
            return oobis

        elif role in (kering.Roles.controller,):  # Fetch any controller URL OOBIs
            oobis = []
            urls = self.hab.fetchUrls(eid=self.hab.pre, scheme=kering.Schemes.http) or self.hab.fetchUrls(
                eid=self.hab.pre, scheme=kering.Schemes.https)
            if not urls:
                return []

            url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
            up = urlparse(url)
            oobis.append(
                urljoin(up.geturl(), f"/oobi/{self.hab.pre}/controller"))
            return oobis

        elif role in (kering.Roles.agent,):
            oobis = []
            roleUrls = (self.hab.fetchRoleUrls(self.hab.pre, scheme=kering.Schemes.http, role=kering.Roles.agent)
                        or self.hab.fetchRoleUrls(self.hab.pre, scheme=kering.Schemes.https, role=kering.Roles.agent))
            if not roleUrls:
                return []

            for eid, urls in roleUrls['agent'].items():
                url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
                up = urlparse(url)
                oobis.append(
                    urljoin(up.geturl(), f"/oobi/{self.hab.pre}/agent/{eid}"))

            return oobis

        return []

    async def close(self, _):
        await self.app.showIdentifiers()


class CreateIdentifierPanel(ft.UserControl):
    def __init__(self, app):
        self.app = app
        super(CreateIdentifierPanel, self).__init__()

        self.alias = ft.TextField(
            hint_text="a-memorable-description", border_color=Brand.SECONDARY)
        self.eo = ft.Checkbox(label="Establishment Only", value=False,
                              fill_color=ft.colors.WHITE, check_color=Brand.SECONDARY)
        self.dnd = ft.Checkbox(label="Do Not Delegate", value=False,
                               fill_color=ft.colors.WHITE, check_color=Brand.SECONDARY)

        salt = coring.randomNonce()[2:23]
        self.salt = ft.TextField(label="Key Salt", value=salt, password=True, can_reveal_password=True, width=300,
                                 border_color=Brand.SECONDARY)
        self.keyCount = ft.TextField(
            label="Signing", width=100, value="1", border_color=Brand.SECONDARY)
        self.nkeyCount = ft.TextField(
            label="Rotation", width=100, value="1", border_color=Brand.SECONDARY)
        self.keySith = ft.TextField(
            label="Signing Threshold", width=200, value="1", border_color=Brand.SECONDARY)
        self.nkeySith = ft.TextField(
            label="Rotation Threshold", width=200, value="1", border_color=Brand.SECONDARY)
        self.toad = ft.TextField(value="0", border_color=Brand.SECONDARY)

        self.signingList = ft.Column(width=550)
        self.signingDropdown = ft.Dropdown(options=[], width=420, text_size=12, height=50,
                                           border_color=Brand.SECONDARY,
                                           text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.rotationList = ft.Column(width=550)
        self.rotationDropdown = ft.Dropdown(options=[], width=420, text_size=12, height=50,
                                            border_color=ft.colors.with_opacity(0.25, ft.colors.GREY), disabled=True,
                                            text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.rotationAddButton = ft.IconButton(icon=ft.icons.ADD, tooltip="Add Member", on_click=self.addRotation,
                                               disabled=True)
        self.rotSith = ft.TextField(label="Rotation Threshold", width=200, value="1", border_color=Brand.SECONDARY,
                                    disabled=True)

        async def resalt(_):
            self.salt.value = coring.randomNonce()[2:23]
            await self.salt.update_async()

        self.salty = ft.Column([
            ft.Row([
                self.salt,
                ft.IconButton(icon=ft.icons.CHANGE_CIRCLE_OUTLINED,
                              on_click=resalt, icon_color=Brand.SECONDARY)
            ]),
            ft.Text("Number of Keys / Threshold", weight=FontWeight.BOLD),
            ft.Row([
                self.keyCount,
                self.keySith
            ]),
            ft.Row([
                self.nkeyCount,
                self.nkeySith
            ])

        ], spacing=20)

        self.randy = ft.Column([
            ft.Text("Number of Keys / Threshold", weight=FontWeight.BOLD),
            ft.Row([
                self.keyCount,
                self.keySith
            ]),
            ft.Row([
                self.nkeyCount,
                self.nkeySith
            ])
        ], spacing=20)

        self.group = ft.Column([
            ft.Text("Signing members"),
            self.signingList,
            ft.Row([
                self.signingDropdown,
                ft.IconButton(icon=ft.icons.ADD,
                              tooltip="Add Member", on_click=self.addMember)
            ]),
            ft.Row([
                self.keySith
            ]),
            ft.Container(padding=ft.padding.only(top=20)),
            ft.Checkbox(label="Rotation Members (if different from signing)", value=False,
                        on_change=self.enableRotationMembers),
            self.rotationList,
            ft.Row([
                self.rotationDropdown,
                self.rotationAddButton
            ]),
            ft.Row([
                self.rotSith
            ])

        ], spacing=15)

        self.witnesses = self.loadWitnesses()

        self.keyTypePanel = ft.Container(
            content=self.salty, padding=padding.only(left=50))
        self.keyType = "salty"

        self.witnessDropdown = ft.Dropdown(options=self.witnesses, width=420, text_size=14,
                                           border_color=Brand.SECONDARY,
                                           text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.witnessList = ft.Column(width=550)

        self.members = self.loadMembers()
        self.signingDropdown.options = self.members
        self.rotationDropdown.options = list(self.members)

    async def keyTypeChanged(self, e):
        self.keyType = e.control.value
        match e.control.value:
            case "salty":
                self.keyTypePanel.content = self.salty
            case "randy":
                self.keyTypePanel.content = self.randy
            case "group":
                self.keyTypePanel.content = self.group
        await self.update_async()

    async def addWitness(self, _):
        if not self.witnessDropdown.value:
            return

        self.witnessList.controls.append(
            ft.ListTile(title=ft.Text(self.witnessDropdown.value, font_family="SourceCodePro"),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteWitness, data=self.witnessDropdown.value),
                        data=self.witnessDropdown.value),
        )

        for option in self.witnessDropdown.options:
            if option.key == self.witnessDropdown.value:
                self.witnessDropdown.options.remove(option)

        self.toad.value = str(self.recommendedThold(
            len(self.witnessList.controls)))
        await self.toad.update_async()

        self.witnessDropdown.value = None
        await self.witnessDropdown.update_async()
        await self.witnessList.update_async()

    async def deleteWitness(self, e):
        aid = e.control.data
        for tile in self.witnessList.controls:
            if tile.data == aid:
                self.witnessList.controls.remove(tile)
                self.witnessDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(
            len(self.witnessList.controls)))
        await self.toad.update_async()
        await self.witnessDropdown.update_async()
        await self.witnessList.update_async()

    async def addMember(self, _):
        if self.signingDropdown.value is None:
            return

        idx = int(self.signingDropdown.value)
        m = self.app.members[idx]
        self.signingList.controls.append(
            ft.ListTile(title=ft.Text(f"{m['alias']}\n({m['id']})", font_family="SourceCodePro", size=14),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteMember, data=self.signingDropdown.value),
                        data=self.signingDropdown.value),
        )

        for option in self.signingDropdown.options:
            if option.key == self.signingDropdown.value:
                self.signingDropdown.options.remove(option)

        self.signingDropdown.value = None
        await self.signingDropdown.update_async()
        await self.signingList.update_async()

    async def enableRotationMembers(self, e):
        self.rotationDropdown.disabled = not e.control.value
        self.rotSith.disabled = not e.control.value
        self.rotationAddButton.disabled = not e.control.value
        self.rotationList.controls.clear()

        self.rotationDropdown.border_color = Brand.SECONDARY if e.control.value \
            else ft.colors.with_opacity(0.25, ft.colors.GREY)

        await self.rotationList.update_async()
        await self.rotationDropdown.update_async()
        await self.rotSith.update_async()
        await self.rotationAddButton.update_async()

    async def addRotation(self, _):
        if self.rotationDropdown.value is None:
            return

        idx = int(self.rotationDropdown.value)
        m = self.app.members[idx]
        self.rotationList.controls.append(
            ft.ListTile(title=ft.Text(self.rotationDropdown.value, font_family="SourceCodePro", size=14),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteRotation, data=self.rotationDropdown.value),
                        data=self.rotationDropdown.value),
        )

        for option in self.rotationDropdown.options:
            if option.key == self.rotationDropdown.value:
                self.rotationDropdown.options.remove(option)

        self.rotationDropdown.value = None
        await self.rotationDropdown.update_async()
        await self.rotationList.update_async()

    async def deleteMember(self, e):
        aid = e.control.data
        for tile in self.signingList.controls:
            if tile.data == aid:
                self.signingList.controls.remove(tile)
                self.signingDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(
            len(self.signingList.controls)))
        await self.toad.update_async()
        await self.signingDropdown.update_async()
        await self.signingList.update_async()

    async def deleteRotation(self, e):
        aid = e.control.data
        for tile in self.rotationList.controls:
            if tile.data == aid:
                self.rotationList.controls.remove(tile)
                self.rotationDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(
            len(self.rotationList.controls)))
        await self.toad.update_async()
        await self.rotationDropdown.update_async()
        await self.rotationList.update_async()

    async def createAid(self, _):

        if self.alias.value == "":
            return

        if self.salt.value == "" or len(self.salt.value) != 21:
            return

        kwargs = dict(algo=self.keyType)
        if self.keyType == "salty":
            kwargs['salt'] = coring.Salter(
                raw=self.salt.value.encode("utf-8")).qb64
            kwargs['icount'] = int(self.keyCount.value)
            kwargs['isith'] = int(self.keySith.value)
            kwargs['ncount'] = int(self.nkeyCount.value)
            kwargs['nsith'] = int(self.nkeySith.value)

        elif self.keyType == "randy":
            kwargs['salt'] = None
            kwargs['icount'] = int(self.keyCount.value)
            kwargs['isith'] = int(self.keySith.value)
            kwargs['ncount'] = int(self.nkeyCount.value)
            kwargs['nsith'] = int(self.nkeySith.value)

        elif self.keyType == "group":
            kwargs['isith'] = int(self.keySith.value)
            kwargs['nsith'] = int(self.nkeySith.value)

            smids = []
            for tile in self.signingList.controls:
                m = self.app.members[int(tile.data)]
                smids.append(m['id'])

            if not self.rotSith.disabled:
                rmids = []
                for tile in self.rotationList.controls:
                    m = self.app.members[int(tile.data)]
                    rmids.append(m['id'])
            else:
                rmids = smids

            kwargs["smids"] = smids
            kwargs["rmids"] = rmids

        # TODO - Add delegator support here
        # delpre
        delegator = False

        kwargs['wits'] = [c.data for c in self.witnessList.controls]
        kwargs['toad'] = self.toad.value
        kwargs['estOnly'] = self.eo.value
        kwargs['DnD'] = self.dnd.value

        if self.keyType == "group":
            hab = self.app.hby.makeGroupHab(name=self.alias.value, **kwargs)
            serder, _, _ = hab.getOwnEvent(allowPartiallySigned=True)

            self.app.agent.groups.push(dict(serder=serder))
            await self.app.snack(f"Creating {hab.pre}, waiting for multisig collaboration...")
        else:
            hab = self.app.hby.makeHab(name=self.alias.value, **kwargs)
            serder, _, _ = hab.getOwnEvent(sn=0)

            if delegator:
                self.app.agent.anchors.push(dict(sn=0))
                await self.app.snack(f"Creating {hab.pre}, waiting for delegation approval...")

            elif len(kwargs['wits']) > 0:
                self.app.agent.witners.push(dict(serder=serder))
                await self.app.snack(f"Creating {hab.pre}, waiting for witness receipts...")

            else:
                await self.app.snack(f"Creatd AID {hab.pre}.")

        self.reset()
        await self.app.showIdentifiers()

    def loadWitnesses(self):
        return [ft.dropdown.Option(wit['id']) for wit in self.app.witnesses]

    def loadMembers(self):
        return [ft.dropdown.Option(key=idx, text=f"{m['alias']}\n({m['id']})") for idx, m in enumerate(self.app.members)]

    async def cancel(self, _):
        self.reset()
        await self.app.showIdentifiers()

    def reset(self):
        self.alias.value = ""
        self.eo.value = False
        self.dnd.value = False
        self.keyTypePanel = ft.Container(
            content=self.salty, padding=padding.only(left=50))
        self.keyType = "salty"
        self.nkeySith.value = "1"
        self.keySith.value = "1"
        self.nkeyCount.value = "1"
        self.keyCount.value = "1"
        self.salt.value = coring.randomNonce()[2:23]

    @staticmethod
    def recommendedThold(numWits):
        match numWits:
            case 0:
                return 0
            case 1:
                return 1
            case 2 | 3:
                return 2
            case 4:
                return 3
            case 5 | 6:
                return 4
            case 7:
                return 5
            case 8 | 9:
                return 7
            case 10:
                return 8

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text("Alias", weight=FontWeight.BOLD,),
                        ]),
                        ft.Row([
                            self.alias,
                        ]),
                    ]),
                ]),
                ft.Container(content=ft.Divider(color=Brand.SECONDARY),),
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text("Configuration options",
                                    weight=FontWeight.BOLD,),
                        ]),
                        ft.Row([
                            ft.Column([
                                self.eo
                            ]),
                            ft.Column([
                                self.dnd
                            ]),
                        ]),
                    ]),
                ]),
                ft.Container(content=ft.Divider(color=Brand.SECONDARY),),
                ft.Column([
                    ft.Text("Select Key Type", weight=FontWeight.BOLD,),
                    ft.RadioGroup(content=ft.Row([
                        ft.Radio(value="salty", label="Key Chain",
                                 fill_color=Brand.SECONDARY,),
                        ft.Radio(value="randy", label="Random Key",
                                 fill_color=Brand.SECONDARY,),
                        ft.Radio(value="group", label="Group Multisig", fill_color=Brand.SECONDARY,)]), value="salty", on_change=self.keyTypeChanged)
                ]),
                self.keyTypePanel,
                ft.Container(content=ft.Divider(color=Brand.SECONDARY),),
                ft.Column([
                    ft.Text("Witnesses", weight=FontWeight.BOLD,),
                    self.witnessList,
                    ft.Row([
                        self.witnessDropdown,
                        ft.IconButton(
                            icon=ft.icons.ADD, tooltip="Add Witness", on_click=self.addWitness)
                    ]),
                    ft.Container(padding=ft.padding.only(top=3)),
                    ft.Row([
                        ft.Text("Threshold of Acceptable Duplicity",
                                weight=FontWeight.BOLD),
                    ]),
                    ft.Row([
                        self.toad,
                    ]),
                ]),
                ft.Container(content=ft.Divider(color=Brand.SECONDARY),),
                ft.Column([
                    ft.Text("Delegator", weight=FontWeight.BOLD,),
                    self.witnessList,
                    ft.Row([
                        self.witnessDropdown,
                        ft.IconButton(
                            icon=ft.icons.ADD, tooltip="Add Delegator", on_click=self.addWitness)
                    ]),
                ]),
                ft.Container(content=ft.Divider(color=Brand.SECONDARY),),
                ft.Row([
                    ft.ElevatedButton(
                        "Create", on_click=self.createAid, color=ft.colors.WHITE, bgcolor=Brand.SECONDARY,),
                    ft.ElevatedButton(
                        "Cancel", on_click=self.cancel, color=Brand.BATTLESHIP_GRAY,),
                ]),
            ], spacing=35, scroll=ft.ScrollMode.AUTO),
            expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))
