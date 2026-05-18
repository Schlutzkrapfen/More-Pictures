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

@ui.page('/download')
def download_pictures():
      setup_conf = load_setup_conf()
      ui.label(f"Connected to: {setup_conf['url']}, project id: {setup_conf['project_id']}")
      ui.label("Folder where downloaded images will be saved")
      output = ui.input(value=setup_conf['output_dir']).props('clearable')
      ui.label("Set to true to only download tasks that have been fully annotated/completed. \n \
            Set to false to download all tasks regardless of annotation status")
      only_completed = ui.checkbox(text="Only annotated",value=setup_conf['only_completed'])
      async def handle_download(): 
            print("handle_download called!") 
            ui.notify("Starting download...", type="positive")
            try:
                client = await run.io_bound(connect_label_studio, 
                    setup_conf['url'],
                    setup_conf['api_key'],
                    setup_conf['project_id']
                )
                if client is None:
                    ui.notify("Connection failed", type="negative")
                    return
                tasks = await run.io_bound(fetch_tasks, client, setup_conf['project_id'], only_completed.value)
                if not tasks:
                    ui.notify("No tasks found", type="negative")
                    return
                await run.io_bound(save_tasks, tasks, output.value, setup_conf['project_id'])
                for task in tasks:
                    try:
                        await run.io_bound(donwload_image, task, setup_conf['api_key'], setup_conf['url'], output.value)
                        ui.notify(f"Downloaded Picture {task.id}", type="positive")
                    except Exception as e:
                        ui.notify(f"Download from Picture {task.id} failed: {e}", type="negative")
                ui.notify("Download complete!", type="positive")
                await asyncio.sleep(0.5) 
                ui.navigate.to('/ImageAgumantation')
            except Exception as e:
                ui.notify(f"Download failed: {e}", type="negative")

      ui.button("Download", on_click=handle_download)
      ui.button("Back", on_click=lambda: ui.navigate.to('/'))
    
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
    ui.image(pictures[0])
    img = ui.image(pictures[0])
    #brit = ui.image(pictures[0])
    if picture_conf['mirrored']:
        img.set_source(transformer.mirror(pictures[0]))
        img.set_visibility(True)
    else:
        img.set_visibility(False)
    async def show_output(e):
        if e.value:
            mirrored = transformer.mirror(pictures[0])
            img.set_source(mirrored)
            img.set_visibility(True)
        else:
            img.set_visibility(False)

    brightness_values = []
    image_row = ui.row()

    def add_brightness():
        val = brightness_input.value
        if val is None:
            return
        brightness_values.append(val)
        refresh_previews()

    def refresh_previews():
        image_row.clear()
        with image_row:
            for val in brightness_values:
                with ui.column():
                    ui.image(transformer.adjust_brightness(pictures[0], val))
                    ui.label(f"Brightness: {val}")
                    ui.button(icon='delete', on_click=lambda v=val: remove_brightness(v)).props('flat round dense')

    def remove_brightness(val):
        brightness_values.remove(val)
        refresh_previews()

    brightness_input = ui.number('Brightness value')
    ui.button('Add', icon='add', on_click=add_brightness)
    image_row = ui.row()


    ui.label("What do you want to change: ")
    ui.checkbox(text="Mirrored",value=picture_conf['mirrored'], on_change=show_output) 
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
    