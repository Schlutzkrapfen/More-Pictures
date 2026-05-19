import yaml
from nicegui import ui, run
import asyncio
from downloader import load_setup_conf,fetch_tasks, connect_label_studio,save_tasks,donwload_image, get_local_picutrs, load_picture_conf
from ImageTransformer import ImageTransformer

json_path_glob= ""
def try_connection(url,api_key,project_id = 1):
    try:
        client =  connect_label_studio(url,api_key,project_id)
        if client == None:

            ui.notify(f"Error one of the Input fields is wrong", type="negative")
        else:
            
            save_setup_conf(url=url,api_key=api_key,project_id=project_id)
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
            project_id = ui.number(value=setup_conf['project_id'])
            ui.button("Start", on_click=lambda: try_connection(
                i.value,
                d.value,
                project_id.value
            ))
        with ui.tab_panel(two):
            ui.label('Local is under construction')
    
def dump_yml(data):
    yaml_string = yaml.dump(data, default_flow_style=False, indent=4, width=80)
    print(yaml_string)
    with open('data.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False, indent=4)

    
@ui.page('/ImageAgumantation')
def change_picturs():
    setup_conf = load_setup_conf()
    picture_conf = load_picture_conf()
    pictures = get_local_picutrs(setup_conf['output_dir'])
    client =  run.io_bound(connect_label_studio, 
                    setup_conf['url'],
                    setup_conf['api_key'],
                    setup_conf['project_id']
                )
    tasks =  run.io_bound(fetch_tasks, client, setup_conf['project_id'],setup_conf['only_completed'])
    json_path =  run.io_bound(save_tasks, tasks, setup_conf['output_dir'], setup_conf['project_id'])
    transformer = ImageTransformer(pictures,json_path,setup_conf['output_dir'])
   
    ui.label("What do you want to change: ")

    brightness_values = []
    image_row = ui.row()

    main_imag = ui.image(pictures[0])
    main_imag.set_visibility(True)
    mirrow = ui.checkbox(text="Mirrored",value=picture_conf['mirrored']) 
    if mirrow:
        with ui.column() as image_row:
            img = ui.image(pictures[0])
            img.set_source(transformer.mirror(pictures[0]))
    else:
        image_row = None
    
    def add_brightness():
        val = brightness_input.value
        if val is None:
            return
        brightness_values.append(val)
        refresh_previews()

    def refresh_previews():
        with image_row:
            for val in brightness_values:
                with ui.grid(columns=5):
                    ui.image(transformer.adjust_brightness(pictures[0], val))
                    ui.label(f"Brightness: {val}")
                    ui.button(icon='delete', on_click=lambda v=val: remove_brightness(v)).props('flat round dense')

    def remove_brightness(val):
        brightness_values.remove(val)
        refresh_previews()

    brightness_input = ui.number('Brightness value')
    ui.button('Add', icon='add', on_click=add_brightness)


    async def change_pictures(): 
        pass
    ui.button("Use it on all Pictures", on_click=change_pictures)
    pass

def save_setup_conf(url = None,api_key= None,project_id = None,dow_output =None , conf: dict =None,  path: str = "config.yml"):
    try:
        if conf != None:
            with open(path, 'w') as f:
                yaml.dump(conf, f, default_flow_style=False, sort_keys=False, default_style=None)
        

        with open(path, "r") as f:
            config = yaml.safe_load(f)
        if url != None:
            config['label_studio']['url'] = url
        if api_key != None:
            config['label_studio']['api_key'] = api_key
        if project_id != None:
            config['label_studio']['project_id'] = project_id
        if dow_output != None:
            config['donwload']['output_dir'] = dow_output

        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print("Save worked")
    except Exception as e:
        print(f"Save failed: {e}")
    