import flet as ft


class Splash(ft.Column):
    def __init__(self):
        super(Splash, self).__init__()

    def build(self):
        return ft.Column(
            [
                ft.Row([
                    ft.Container(
                        ft.Image(
                            src="gleif-logo-new.svg",
                            height=200),
                        expand=True)
                ], expand=True)
            ],
            expand=True,
        )
