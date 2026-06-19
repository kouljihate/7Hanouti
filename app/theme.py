import flet as ft


class AppTheme:
    PRIMARY = "#00897B"
    PRIMARY_DARK = "#00695C"
    PRIMARY_LIGHT = "#4DB6AC"
    ACCENT = "#FF5722"
    ACCENT_DARK = "#D84315"
    ACCENT_LIGHT = "#FF8A65"
    BG_LIGHT = "#F5F5F5"
    BG_DARK = "#121212"
    SURFACE_LIGHT = "#FFFFFF"
    SURFACE_DARK = "#1E1E1E"
    TEXT_LIGHT = "#212121"
    TEXT_DARK = "#E0E0E0"
    ERROR = "#D32F2F"
    SUCCESS = "#388E3C"
    WARNING = "#F57C00"
    LOW_STOCK = "#FF6F00"

    @staticmethod
    def get_theme(theme_mode: str) -> ft.Theme:
        is_dark = theme_mode == "dark"
        return ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            brightness=ft.Brightness.DARK if is_dark else ft.Brightness.LIGHT,
            primary_color=AppTheme.PRIMARY,
            primary_color_dark=AppTheme.PRIMARY_DARK,
            primary_color_light=AppTheme.PRIMARY_LIGHT,
            secondary_color=AppTheme.ACCENT,
            bgcolor=AppTheme.BG_DARK if is_dark else AppTheme.BG_LIGHT,
            surface_tint_color=AppTheme.SURFACE_DARK if is_dark else AppTheme.SURFACE_LIGHT,
            error_color=AppTheme.ERROR,
            text_theme=ft.TextTheme(
                body_large=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                body_medium=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                body_small=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                headline_large=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                headline_medium=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                headline_small=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                title_large=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                title_medium=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
                title_small=ft.TextStyle(color=AppTheme.TEXT_DARK if is_dark else AppTheme.TEXT_LIGHT),
            ),
        )
