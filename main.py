import flet as ft
from app.database import init_db
from app.translations import get_translation as t
from app.screens.login_screen import LoginScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.stock_screen import StockScreen
from app.screens.cash_screen import CashScreen
from app.screens.settings_screen import SettingsScreen


def main(page: ft.Page):
    init_db()

    page.title = "7Hanouti"
    page.theme_mode = page.session.store.get("theme_mode") or "dark"
    page.rtl = True
    page.window.width = 400
    page.window.height = 750
    page.padding = 20

    if not page.session.store.get("lang"):
        page.session.store.set("lang", "ar")
    if not page.session.store.get("theme_mode"):
        page.session.store.set("theme_mode", "dark")

    def navigate_to(screen_index):
        nav_bar.selected_index = screen_index
        _update_screen(screen_index)

    def _update_screen(index):
        lang = page.session.store.get("lang") or "ar"
        page.views.clear()
        user_id = page.session.store.get("user_id")

        if not user_id:
            view = ft.View("/", [LoginScreen(page, on_login_success=lambda: navigate_to(0))])
            page.views.append(view)
            page.update()
            return

        screens = [
            DashboardScreen(page),
            StockScreen(page),
            CashScreen(page),
            SettingsScreen(page, on_logout=_logout, on_theme_change=_on_theme_change,
                            on_lang_change=_on_lang_change),
        ]

        titles = [t(lang, "dashboard"), t(lang, "stock"), t(lang, "cash"), t(lang, "settings")]
        icons = [ft.Icons.DASHBOARD, ft.Icons.INVENTORY, ft.Icons.ACCOUNT_BALANCE, ft.Icons.SETTINGS]

        content = screens[index] if index < len(screens) else screens[0]
        view = ft.View(
            "/",
            [
                ft.Container(content=content, expand=True),
                ft.Container(height=60),
            ],
            bottom_appbar=ft.BottomAppBar(
                content=ft.Container(
                    content=nav_bar,
                    padding=ft.padding.symmetric(horizontal=10),
                ),
                height=70,
            ),
            padding=10,
        )
        page.views.append(view)
        page.update()

    def _logout():
        page.session.store.set("user_id", None)
        page.session.store.set("user_name", None)
        page.views.clear()
        page.views.append(ft.View("/", [LoginScreen(page, on_login_success=lambda: navigate_to(0))]))
        page.update()

    def _on_theme_change(mode):
        page.theme_mode = mode
        _update_screen(nav_bar.selected_index)

    def _on_lang_change(lang):
        _update_screen(nav_bar.selected_index)

    def _nav_change(e):
        _update_screen(e.control.selected_index)

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label=t(page.session.store.get("lang") or "ar", "dashboard")),
            ft.NavigationBarDestination(icon=ft.Icons.INVENTORY, label=t(page.session.store.get("lang") or "ar", "stock")),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE, label=t(page.session.store.get("lang") or "ar", "cash")),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label=t(page.session.store.get("lang") or "ar", "settings")),
        ],
        selected_index=0,
        on_change=_nav_change,
    )

    _update_screen(0)


if __name__ == "__main__":
    ft.run(main)
