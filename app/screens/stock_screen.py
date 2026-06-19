import flet as ft
from app.database import (get_products, add_product, update_product, delete_product,
                          add_stock_movement, get_stock_movements, get_product)
from app.translations import get_translation as t
from app.theme import AppTheme


class StockScreen(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.bgcolor = page.theme.bgcolor if hasattr(page.theme, "bgcolor") else None
        self._build()

    def _build(self):
        lang = self.page.session.get("lang") or "ar"
        self.products = get_products(self.page.session.get("user_id")) if self.page.session.get("user_id") else []
        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(t(lang, "products"), size=24, weight=ft.FontWeight.BOLD),
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD,
                            text=t(lang, "add_product"),
                            on_click=self._show_add_dialog,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=10),
                self._build_product_list(lang),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_product_list(self, lang):
        if not self.products:
            return ft.Text(t(lang, "no_data"), opacity=0.5, italic=True)
        cards = []
        for p in self.products:
            is_low = p["quantity"] <= p["low_stock_qty"]
            cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(p["name"], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, pid=p["id"]: self._show_edit_dialog(pid)),
                                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, pid=p["id"]: self._confirm_delete(pid)),
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"{t(lang, 'quantity')}: {p['quantity']}"),
                                        ft.Text(f"{t(lang, 'price')}: {p['price']:.2f} DA"),
                                        ft.Text(f"{t(lang, 'category')}: {p.get('category', '')}"),
                                    ],
                                    spacing=20,
                                ),
                                ft.Row(
                                    [
                                        ft.FilledTonalButton(
                                            t(lang, "stock_in"),
                                            icon=ft.icons.ADD_CIRCLE,
                                            on_click=lambda e, pid=p["id"]: self._show_movement_dialog(pid, "in"),
                                        ),
                                        ft.FilledTonalButton(
                                            t(lang, "stock_out"),
                                            icon=ft.icons.REMOVE_CIRCLE,
                                            on_click=lambda e, pid=p["id"]: self._show_movement_dialog(pid, "out"),
                                        ),
                                        ft.FilledTonalButton(
                                            t(lang, "movement_history"),
                                            icon=ft.icons.HISTORY,
                                            on_click=lambda e, pid=p["id"]: self._show_movement_history(pid),
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                ft.Row(
                                    [ft.Icon(ft.icons.WARNING, color=AppTheme.LOW_STOCK, size=16),
                                     ft.Text(t(lang, "low_stock_alerts"), size=12, color=AppTheme.LOW_STOCK)]
                                ) if is_low else ft.Container(),
                            ],
                            spacing=5,
                        ),
                        padding=15,
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                )
            )
        return ft.Column(cards, scroll=ft.ScrollMode.AUTO)

    def _show_add_dialog(self, e):
        self._show_product_dialog()

    def _show_edit_dialog(self, product_id):
        p = get_product(product_id)
        if p:
            self._show_product_dialog(product=p)

    def _confirm_delete(self, product_id):
        lang = self.page.session.get("lang") or "ar"
        dlg = ft.AlertDialog(
            title=ft.Text(t(lang, "confirm_delete")),
            content=ft.Text(t(lang, "confirm_delete_msg")),
            actions=[
                ft.TextButton(t(lang, "cancel"), on_click=lambda e: self._close_dialog(dlg)),
                ft.FilledButton(t(lang, "delete"), on_click=lambda e: self._do_delete(product_id, dlg)),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _do_delete(self, product_id, dlg):
        delete_product(product_id)
        dlg.open = False
        self.page.update()
        self._refresh()

    def _show_product_dialog(self, product=None):
        lang = self.page.session.get("lang") or "ar"
        is_edit = product is not None
        name_inp = ft.TextField(label=t(lang, "product_name"), value=product["name"] if is_edit else "",
                                text_align=ft.TextAlign.RIGHT)
        qty_inp = ft.TextField(label=t(lang, "quantity"), value=str(product["quantity"]) if is_edit else "0",
                                keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.RIGHT)
        price_inp = ft.TextField(label=t(lang, "price"), value=str(product["price"]) if is_edit else "0",
                                 keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.RIGHT)
        cat_inp = ft.TextField(label=t(lang, "category"), value=product.get("category", "") if is_edit else "",
                               text_align=ft.TextAlign.RIGHT)
        pkg_inp = ft.TextField(label=t(lang, "packaging"), value=product.get("packaging", "") if is_edit else "",
                               text_align=ft.TextAlign.RIGHT)
        desc_inp = ft.TextField(label=t(lang, "description"), value=product.get("description", "") if is_edit else "",
                                multiline=True, text_align=ft.TextAlign.RIGHT)
        low_inp = ft.TextField(label=t(lang, "low_stock_qty"),
                               value=str(product["low_stock_qty"]) if is_edit else "5",
                               keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.RIGHT)

        def save_action(e):
            try:
                if is_edit:
                    update_product(product["id"], name_inp.value.strip(), float(qty_inp.value or 0),
                                   float(price_inp.value or 0), cat_inp.value.strip(), pkg_inp.value.strip(),
                                   desc_inp.value.strip(), float(low_inp.value or 5))
                else:
                    add_product(self.page.session.get("user_id"), name_inp.value.strip(),
                                float(qty_inp.value or 0), float(price_inp.value or 0),
                                cat_inp.value.strip(), pkg_inp.value.strip(), desc_inp.value.strip(),
                                float(low_inp.value or 5))
                dlg.open = False
                self.page.update()
                self._refresh()
            except ValueError:
                pass

        dlg = ft.AlertDialog(
            title=ft.Text(t(lang, "edit_product" if is_edit else "add_product")),
            content=ft.Column([name_inp, qty_inp, price_inp, cat_inp, pkg_inp, desc_inp, low_inp],
                              width=320, height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton(t(lang, "cancel"), on_click=lambda e: self._close_dialog(dlg)),
                ft.FilledButton(t(lang, "save"), on_click=save_action),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _show_movement_dialog(self, product_id, mtype):
        lang = self.page.session.get("lang") or "ar"
        qty_inp = ft.TextField(label=t(lang, "quantity"), value="0",
                               keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.RIGHT)
        note_inp = ft.TextField(label=t(lang, "note"), text_align=ft.TextAlign.RIGHT)

        def save_movement(e):
            try:
                qty = float(qty_inp.value or 0)
                if qty <= 0:
                    return
                if mtype == "out":
                    p = get_product(product_id)
                    if p and qty > p["quantity"]:
                        self.page.show_snack_bar(ft.SnackBar(ft.Text(t(lang, "quantity_more_than_stock"))))
                        return
                add_stock_movement(product_id, self.page.session.get("user_id"), mtype, qty, note_inp.value.strip())
                dlg.open = False
                self.page.update()
                self._refresh()
            except ValueError:
                pass

        dlg = ft.AlertDialog(
            title=ft.Text(t(lang, "stock_in" if mtype == "in" else "stock_out")),
            content=ft.Column([qty_inp, note_inp], width=320),
            actions=[
                ft.TextButton(t(lang, "cancel"), on_click=lambda e: self._close_dialog(dlg)),
                ft.FilledButton(t(lang, "save"), on_click=save_movement),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _show_movement_history(self, product_id):
        lang = self.page.session.get("lang") or "ar"
        user_id = self.page.session.get("user_id")
        all_movements = get_stock_movements(user_id, 200)
        p_movements = [m for m in all_movements if m["product_id"] == product_id]

        if not p_movements:
            content = ft.Text(t(lang, "no_movements"), opacity=0.5, italic=True)
        else:
            rows = []
            for m in p_movements:
                color = AppTheme.SUCCESS if m["type"] == "in" else AppTheme.ERROR
                label = t(lang, "stock_in" if m["type"] == "in" else "stock_out")
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(label, color=color)),
                            ft.DataCell(ft.Text(str(m["quantity"]))),
                            ft.DataCell(ft.Text(m["date"][:16] if m["date"] else "")),
                            ft.DataCell(ft.Text(m.get("note", ""))),
                        ]
                    )
                )
            content = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(t(lang, "movement_type"))),
                    ft.DataColumn(ft.Text(t(lang, "quantity"))),
                    ft.DataColumn(ft.Text(t(lang, "date"))),
                    ft.DataColumn(ft.Text(t(lang, "note"))),
                ],
                rows=rows,
            )

        dlg = ft.AlertDialog(
            title=ft.Text(t(lang, "movement_history")),
            content=ft.Container(content=content, width=400),
            actions=[ft.TextButton(t(lang, "cancel"), on_click=lambda e: self._close_dialog(dlg))],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dlg):
        dlg.open = False
        self.page.update()

    def _refresh(self):
        self.products = get_products(self.page.session.get("user_id")) if self.page.session.get("user_id") else []
        self._build()
        self.update()
