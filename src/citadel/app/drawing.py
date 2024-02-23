import flet as ft

from citadel.app import agenting


class AgentDrawer(ft.UserControl):
    def __init__(self, page: ft.Page):
        super(AgentDrawer, self).__init__()

        self.page = page
        self.agent_init = agenting.AgentInitialization(self, self.page).build()

    def build(self):
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
                ft.NavigationDrawerDestination(
                    icon_content=ft.Icon(ft.icons.ADD_ROUNDED),
                    label="Initialize new agent",
                ),
            ],
            on_change=self.agent_change,
        )

    async def agent_change(self, e):
        print("drawing change", self, self.page)
        await self.page.close_end_drawer_async()
        if e.control.selected_index == 0:
            self.page.dialog = self.agent_init
            self.agent_init.open = True
            await self.page.update_async()

