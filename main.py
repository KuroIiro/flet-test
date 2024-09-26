import flet as ft
import json



class json_file():
    def __init__(self):
        self.data = self.load_json()

    def load_json(self):
        with open('data.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d
    
    def get_all_task(self, task_name:str):
        return self.data.get(task_name, {})
    def get_all_work(self, task_name:str, work_name:str):
        return self.data.get(task_name, {}).get(work_name, {})
    

# 再帰的にJSONのキーを階層的に取り出す関数（特定のキーを省略）
def parse_json(data, indent_level=0, exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = {"詳細", "表示", "ID", "作業時間ID"}  # 省略したいキー

    result = []
    for key, value in data.items():
        if key in exclude_keys:
            continue  # キーが除外リストにある場合はスキップ

        # インデントレベルとキーをセットでリストに追加
        result.append((key, indent_level))

        # valueが辞書の場合、さらにネストされているため再帰呼び出し
        if isinstance(value, dict):
            result.extend(parse_json(value, indent_level + 1, exclude_keys))
    return result

json_data:json_file

def flet_content(page: ft.Page):
    json_data = json_file()

    # JSONの内容を階層構造に沿ってインデントを付けたテキストに変換（除外リストを使用）
    parsed_data = parse_json(json_data.data)

    # 新しい要素を格納する変数
    new_elements = []

    # テキストと空のTextFieldを追加
    text_elements = []
    last_indent = 0
    for key, indent_level in parsed_data:
        # 階層が変わるごとにまとめの下にTextFieldを追加
        if indent_level != last_indent:
            text_elements.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.TextField(
                                hint_text=f"新しい要素を追加 (階層: {last_indent})",
                                on_change=lambda e, key=key: add_new_element(e, key, last_indent),
                            ),
                            padding=ft.padding.only(left=last_indent * 20 + 20)
                        )
                    ]
                )
            )
        last_indent = indent_level

        # キーを表示
        text_elements.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(key),
                        padding=ft.padding.only(left=indent_level * 20)
                    )
                ]
            )
        )

    # 最後にまとまりの下にTextFieldを追加
    text_elements.append(
        ft.Row(
            controls=[
                ft.Container(
                    content=ft.TextField(
                        hint_text=f"新しい要素を追加 (階層: {last_indent})",
                        on_change=lambda e, key="new_element": add_new_element(e, "new_element", last_indent),
                    ),
                    padding=ft.padding.only(left=last_indent * 20 + 20)
                )
            ]
        )
    )

    # 新しい要素を追加する関数
    def add_new_element(e, key, indent_level):
        new_value = e.control.value
        if new_value:
            new_elements.append((key, new_value, indent_level))
            print(f"追加された要素: {new_value}, 階層: {indent_level}")

    # 全体のレイアウト
    view = ft.Container(
        content=ft.Column(
            controls=text_elements,
            scroll=ft.ScrollMode.AUTO,  # スクロール可能にする
            height=page.window.height,
            expand=True  # Column全体をスクロール対象に
        ),
    )
    return view

def work_content(process:str, task:str):
    content = []
    for work in json_data.get_all_work(process, task):
        if work in ["詳細", "表示", "ID", "作業時間ID"]:
            continue
        content.append(
            ft.TextField(value=work),
        )
    content.append(ft.TextButton(text="Click"))
    return content

def task_content(process:str):
    content = []
    for task in json_data.get_all_task(process):
        if task in ["詳細", "表示", "ID", "作業時間ID"]:
            continue
        content.append(
            ft.ExpansionTile(
                title=ft.TextField(value=task),
                affinity=ft.TileAffinity.PLATFORM,
                maintain_state=True,
                collapsed_text_color=ft.colors.RED,
                text_color=ft.colors.RED,
                initially_expanded=True,
                controls=work_content(process,task),
            )
        )
    content.append(ft.TextButton(text="Click"))
    return content


def flet_content_sub(page: ft.Page):
    global json_data
    json_data = json_file()

    content = []

    for process in json_data.data:
        if process in ["詳細", "表示", "ID", "作業時間ID"]:
            continue
        content.append(
            ft.ExpansionTile(
                title=ft.TextField(value=process),
                affinity=ft.TileAffinity.PLATFORM,
                maintain_state=True,
                collapsed_text_color=ft.colors.RED,
                text_color=ft.colors.RED,
                initially_expanded=True,
                controls=task_content(process),
            )
        )
    
    content.append(ft.TextButton(text="Click"))


    view = ft.Container(
        content=ft.Column(
            controls=content,
            scroll=ft.ScrollMode.AUTO,  # スクロール可能にする
            height=page.window.height,
            expand=True  # Column全体をスクロール対象に
        ),
    )

    return view


def main(page: ft.Page):
    page.add(flet_content_sub(page=page))

ft.app(main)
