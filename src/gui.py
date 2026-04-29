import yaml
from nicegui import ui
from downloader import load_setup_conf,load_picture_conf,load_config, connect_label_studio
def try_connection(url,api_key,project_id):
    try:
        connect_label_studio(url,api_key,project_id)
        return True
    except Exception as e:
        ui.notify(f"Could not connect to Label Studio: {e}", type="negative")
        return False

def set_up_connection(on_start=None):
    setup_conf = load_setup_conf()
    with ui.tabs().classes('w-full') as tabs:
        one = ui.tab('Label Studio')
        two = ui.tab('Locally')
    with ui.tab_panels(tabs, value=two).classes('w-full'):
        with ui.tab_panel(one):
            ui.label("The base URL where your Label Studio instance is running")
            i = ui.input(value=setup_conf['url']).props('clearable')
            ui.label("Your API key — either a Personal Access Token (PAT) or legacy access token")
            d = ui.input(value=setup_conf['api_key'],password=True).props('clearable')
            ui.label("The numeric ID of the project you want to download images from")
            project_id = ui.number(value=setup_conf['project_id'])
            ui.button("Start",on_click=try_connection( i, 
                d, 
                project_id) )
        with ui.tab_panel(two):
            ui.label('Second tab')

    #ui.label("Folder where downloaded images will be saved")
    #output = ui.input(value=setup_conf['output_dir'])
    def handle_start():
        conf = load_config()
        setup_conf['url'] = i.value
        setup_conf['api_key'] = d.value
        #setup_conf['output_dir'] = output.value
        save_setup_conf(conf)
        if on_start:
            on_start()

def save_setup_conf(conf: dict, path: str = "config.yml"):
    try:
        with open(path, 'w') as f:
            yaml.dump(conf, f, default_flow_style=False, sort_keys=False, default_style=None)
        print("Save worked")
    except Exception as e:
        print(f"Save failed: {e}")