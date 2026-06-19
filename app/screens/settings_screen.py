import flet as ft
from app.version import VERSION, BUILD_DATE
from app.translations import get_translation as t
from app.theme import AppTheme


class SettingsScreen(ft.Container):
    def __init__(self, page: ft.Page, on_logout, on_theme_change, on_lang_change):
        super().__init__()
        self.page = page
        self.on_logout = on_logout
        self.on_theme_change = on_theme_change
        self.on_lang_change = on_lang_change
        self.expand = True
        self.bgcolor = page.theme.bgcolor if hasattr(page.theme, "bgcolor") else None
        self._build()

    def _build(self):
        lang = self.page.session.store.get("lang") or "ar"
        is_dark = self.page.theme_mode == "dark" if hasattr(self.page, "theme_mode") else False
        surface = AppTheme.SURFACE_DARK if is_dark else AppTheme.SURFACE_LIGHT

        self.content = ft.Column(
            [
                ft.Text(t(lang, "settings"), size=24, weight=ft.FontWeight.BOLD),
                ft.Text(t(lang, "settings_subtitle"), size=14, opacity=0.7),
                ft.Container(height=20),

                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(t(lang, "theme"), size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.SegmentedButton(
                                segments=[
                                    ft.Segment("light", label=ft.Text(t(lang, "light_mode")),
                                               icon=ft.icons.LIGHT_MODE),
                                    ft.Segment("dark", label=ft.Text(t(lang, "dark_mode")),
                                               icon=ft.icons.DARK_MODE),
                                ],
                                selected={"dark" if is_dark else "light"},
                                on_change=self._on_theme_change,
                            ),
                        ]
                    ),
                    bgcolor=surface,
                    border_radius=12,
                    padding=15,
                    margin=ft.margin.symmetric(vertical=5),
                ),

                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(t(lang, "language"), size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.SegmentedButton(
                                segments=[
                                    ft.Segment("ar", label=ft.Text(t(lang, "arabic")),
                                               icon=ft.icons.TRANSLATE),
                                    ft.Segment("fr", label=ft.Text(t(lang, "french")),
                                               icon=ft.icons.TRANSLATE),
                                    ft.Segment("en", label=ft.Text(t(lang, "english")),
                                               icon=ft.icons.TRANSLATE),
                                ],
                                selected={lang},
                                on_change=self._on_lang_change,
                            ),
                        ]
                    ),
                    bgcolor=surface,
                    border_radius=12,
                    padding=15,
                    margin=ft.margin.symmetric(vertical=5),
                ),

                ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.INFO),
                                title=ft.Text(f"{t(lang, 'version')}: {VERSION}"),
                                subtitle=ft.Text(f"{t(lang, 'build_date')}: {BUILD_DATE}"),
                            ),
                        ]
                    ),
                    bgcolor=surface,
                    border_radius=12,
                    padding=5,
                    margin=ft.margin.symmetric(vertical=5),
                ),

                ft.Container(height=20),
                ft.FilledButton(
                    t(lang, "logout"),
                    icon=ft.icons.LOGOUT,
                    width=320,
                    height=48,
                    on_click=lambda e: self.on_logout(),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def _on_theme_change(self, e):
        selected = e.data
        new_mode = "dark" if "dark" in selected else "light"
        self.page.theme_mode = new_mode
        self.page.session.store.set("theme_mode", new_mode)
        self.page.update()
        if self.on_theme_change:
            self.on_theme_change(new_mode)
        self._rebuild()

    def _on_lang_change(self, e):
        selected = e.data
        lang = "ar"
        if "fr" in selected:
            lang = "fr"
        elif "en" in selected:
            lang = "en"
        self.page.session.store.set("lang", lang)
        if self.on_lang_change:
            self.on_lang_change(lang)
        self._rebuild()

    def _rebuild(self):
        self._build()
        self.update()
