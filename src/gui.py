import yaml
from nicegui import ui, run
import asyncio
from downloader import load_setup_conf,fetch_tasks, connect_label_studio,save_tasks,donwload_image
def try_connection(url,api_key,project_id = 1):
    try:
        client =  connect_label_studio(url,api_key,project_id)
        if client == None:
            ui.notify(f"Error one of the Input fields is wrong")
        else:
            ui.navigate.to('/download')
        return True
    except Exception as e:
        ui.notify(f"Could not connect to Label Studio: {e}", type="negative")
        return False

@ui.page('/')
def set_up_connection(on_start=None):
    '''Tests if the connection can be set up'''
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
            ui.button("Start", on_click=lambda: try_connection(
                i.value,
                d.value,
                project_id.value
            ))
        with ui.tab_panel(two):
            ui.label('Local is under construction')
    

   
@ui.page('/download')
def download_pictures():
        
      setup_conf = load_setup_conf()

      ui.label(f"Connected to: {setup_conf['url']}, project id: {setup_conf['project_id']}")
      #project_id = ui.number(value=setup_conf['project_id'])
      ui.label("Folder where downloaded images will be saved")
      output = ui.input(value=setup_conf['output_dir']).props('clearable')
      ui.label("Set to true to only download tasks that have been fully annotated/completed. \n \
            Set to false to download all tasks regardless of annotation status")
      only_completed = ui.checkbox(text="Only annotated",value=setup_conf['only_completed'])
      async def handle_download(): # 1. Added 'async' keyword
            print("handle_download called!") 
            ui.notify("Starting download...", type="positive")
            
            try:
                # Note: If connect_label_studio or fetch_tasks take a long time, 
                # you should also wrap them in run.io_bound
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
                
                await asyncio.sleep(0.1) 
                ui.navigate.to('/ImageAgumantation')
            except Exception as e:
                ui.notify(f"Download failed: {e}", type="negative")

      ui.button("Download", on_click=handle_download)
      ui.button("Back", on_click=lambda: ui.navigate.to('/'))
    
@ui.page('/download')
def change_picturs():
    pass

def save_setup_conf(conf: dict, path: str = "config.yml"):
    try:
        with open(path, 'w') as f:
            yaml.dump(conf, f, default_flow_style=False, sort_keys=False, default_style=None)
        print("Save worked")
    except Exception as e:
        print(f"Save failed: {e}")