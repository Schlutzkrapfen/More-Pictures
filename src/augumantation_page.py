

from nicegui import ui, run
import asyncio
from downloader import load_setup_conf,fetch_tasks, connect_label_studio,save_tasks, get_local_picutrs, load_picture_conf
from ImageTransformer import ImageTransformer
from image_stats_enum import ImageStat, PictureEntry
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

    pictures_stats = [PictureEntry()]
    

    mirrow = ui.checkbox(text="Mirrored",value=picture_conf['mirrored']) 
    image_row = ui.row()
    if mirrow:
        pictures_stats.append(PictureEntry(mirrored=True))
   
    
    def add_brightness():
        val = brightness_input.value
        if val is None:
            return
        
        pictures_stats.append(PictureEntry(brightness=val))
        refresh_previews()

    def refresh_previews():
        image_row.clear()
        with image_row:
            for img in pictures_stats:
                val = img.brightness
                with ui.grid(columns=5):
                    image =  transformer.adjust_brightness(pictures[0], val)
                    if img.mirrored:
                        image = transformer.mirror(image)
                    ui.image(image)
                    ui.label(f"Brightness: {val}")
                    #ui.button(icon='delete', on_click=lambda v=val: remove_brightness(v)).props('flat round dense')

   # def remove_brightness(val):
   #     brightness_values.remove(val)
   #     refresh_previews()

    brightness_input = ui.number('Brightness value')
    ui.button('Add', icon='add', on_click=add_brightness)


    async def change_pictures(): 
        pass
    ui.button("Use it on all Pictures", on_click=change_pictures)
    pass

