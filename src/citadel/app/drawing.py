import flet as ft

from citadel.app import agenting


class AgentDrawer(ft.UserControl):
    def __init__(self, app, page: ft.Page):
        super(AgentDrawer, self).__init__()

        self.page = page
        self.app = app
        self.agent_init = agenting.AgentInitialization(self.app, self.page).build()

    def build(self):
        agents = []
        for agent in self.app.environments():
            agents.append(ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.IRON),
                label=agent,
            ))

        return ft.NavigationDrawer(
            controls=[
                ft.Container(height=12),
                ft.Container(content=ft.Row(controls=[
                    ft.Container(width=16),
                    ft.Icon(ft.icons.WALLET_OUTLINED),
                    ft.Text("Agents")
                ]), height=64,
                ),
                ft.Divider(thickness=2),
                *agents,
                ft.NavigationDrawerDestination(
                    icon_content=ft.Icon(ft.icons.ADD_ROUNDED),
                    label="Initialize new agent",
                ),
            ],
            on_change=self.agent_change
        )

    async def agent_change(self, e):
        await self.page.close_end_drawer_async()
        selected = e.control.controls[e.control.selected_index+3]

        if selected.label == "Initialize new agent":
            self.page.dialog = self.agent_init
            self.agent_init.open = True
            await self.page.update_async()

        else:
            self.page.dialog = agenting.AgentConnection(self.app, self.page, selected.label).build()
            self.page.dialog.open = True
            await self.page.update_async()

