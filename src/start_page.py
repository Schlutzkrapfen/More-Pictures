
import yaml
from nicegui import ui
from downloader import load_setup_conf, connect_label_studio
from utils import save_setup_conf

json_path_glob= ""
def try_connection(url,api_key,project_id = 1):
    try:
        client =  connect_label_studio(url,api_key,int(project_id))
        if client == None:

            ui.notify(f"Error one of the Input fields is wrong", type="negative")
        else:
            
            save_setup_conf(url=url,api_key=api_key,project_id=int(project_id))
            ui.navigate.to('/download')
        return True
    except Exception as e:
        ui.notify(f"Could not connect to Label Studio: {e}", type="negative")
        return False

@ui.page('/')
def set_up_connection():
    '''Tests if the connection can be set up'''
    setup_conf = load_setup_conf()
    with ui.tabs().classes('w-full') as tabs:
        one = ui.tab('Label Studio')
        two = ui.tab('Locally')
    with ui.tab_panels(tabs, value=one).classes('w-full'):
        with ui.tab_panel(one):
            ui.label("The base URL where your Label Studio instance is running")
            i = ui.input(value=setup_conf['url']).props('clearable')
            ui.label("Your API key — either a Personal Access Token (PAT) or legacy access token")
            d = ui.input(value=setup_conf['api_key'],password=True).props('clearable')
           
            ui.label("The numeric ID of the project you want to download images from")
            project_id_number =ui.number(value=setup_conf['project_id'])
            ui.button("Start", on_click=lambda: try_connection(
                i.value,
                d.value,
                int(project_id_number.value)
            ))
        with ui.tab_panel(two):
            ui.label('Local is under construction')
    
def dump_yml(data):
    yaml_string = yaml.dump(data, default_flow_style=False, indent=4, width=80)
    print(yaml_string)
    with open('data.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False, indent=4)

    

    