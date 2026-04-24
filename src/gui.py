from nicegui import ui
def set_up_gui(on_start=None):
    i = ui.input(value='some text').props('clearable')
    ui.label().bind_text_from(i, 'value')
    def handle_start():
        # optionally validate inputs first
        if on_start:
            on_start()
    ui.button("Start", on_click=handle_start)
