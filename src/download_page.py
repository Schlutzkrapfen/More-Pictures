
import asyncio
from nicegui import ui, run
from downloader import load_setup_conf,fetch_tasks, connect_label_studio,save_tasks,donwload_image
from utils import save_setup_conf
@ui.page('/download')
def download_pictures():
    with ui.card().classes('mt-20').style('width:75%'):
    
        setup_conf = load_setup_conf()
        ui.label(f"Connected to: {setup_conf['url']}")
    with ui.card().style('width:75%'):
        ui.label("The numeric ID of the project you want to download images from")
        project_id_number =ui.number(value=setup_conf['project_id']).props('outlined')
        ui.label("Folder where downloaded images will be saved")
        output = ui.input(value=setup_conf['output_dir']).props('clearable').classes(' w-full').props('outlined')
        ui.label("Set to true to only download tasks that have been fully annotated/completed. \n \
              Set to false to download all tasks regardless of annotation status")
        only_completed = ui.checkbox(text="Only annotated",value=setup_conf['only_completed'])
      

        async def handle_download(): 
                print("handle_download called!") 
                project_id = int(project_id_number.value)
                ui.notify(f"Starting download from Project {project_id}", type="positive",position="bottom-right")
                try:
                    client = await run.io_bound(connect_label_studio, 
                        setup_conf['url'],
                        setup_conf['api_key'],
                        project_id
                    )
                    if client is None:
                        ui.notify("Connection failed", type="negative",position='bottom-right')
                        return
                    tasks = await run.io_bound(fetch_tasks, client,project_id , only_completed.value)
                    if not tasks:
                        ui.notify("No tasks found", type="negative",position="bottom-right")
                        return
                    await run.io_bound(save_tasks, tasks, output.value, project_id )
                    save_setup_conf(project_id=int(project_id),dow_output=output)

                    for task in tasks:
                        try:
                            await run.io_bound(donwload_image, task, setup_conf['api_key'], setup_conf['url'], output.value)
                            ui.notify(f"Downloaded Picture {task.id}", type="positive",position="bottom-right")
                        except Exception as e:
                            ui.notify(f"Download from Picture {task.id} failed: {e}", type="negative",position="bottom-right")
                    ui.notify("Download complete!", type="positive",position="bottom-right")
                    await asyncio.sleep(0.5) 
                    ui.navigate.to('/ImageAgumantation')
                except Exception as e:
                    ui.notify(f"Download failed: {e}", type="negative")
        with ui.row().classes('w-full justify-between'):
            ui.button("Download", on_click=handle_download)
            ui.button("Back", on_click=lambda: ui.navigate.to('/'))