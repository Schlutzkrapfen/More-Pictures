

from nicegui import ui, run
import asyncio
from downloader import load_setup_conf,fetch_tasks, connect_label_studio,save_tasks, get_local_picutrs, load_picture_conf
from ImageTransformer import ImageTransformer
from image_stats import  PictureEntry,ImageEnum
from utils import save_augumatiaion_conf
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
    
    image_row = ui.row()
    def refresh_previews():
        image_row.clear()
        with image_row:
            for i,img in enumerate(pictures_stats):

                val = img.brightness
                with ui.grid(columns=5):
                    image =  transformer.adjust_brightness(pictures[0], val)
                    if img.mirrored:
                        image = transformer.mirror(image)
                    ui.image(image)
                    ui.label(f"Brightness: {val}")
                    ui.button(icon='delete', on_click=lambda v=i: remove_picture(v)).props('flat round dense')

    def update_combination(index:ImageEnum,value:bool):
        '''updtaes the combination of the pictures (works just on mirror and brightness at the moment)'''
        if not value:
            return
        save_pictures= []
        if index.value[0] >= len(picture_conf['mirrored_combination']):
            return

        save_pictures = [
            PictureEntry(mirrored=True, brightness=p.brightness, gaus=p.gaus)
            for p in pictures_stats
            if p.brightness != 1 and not p.mirrored
       ]

        pictures_stats.extend(save_pictures)
        print(pictures_stats)
        save_augumatiaion_conf()
        refresh_previews()

        
    def change_mirror(mirror):
        '''Adds Mirrror images for the pictures'''
        if mirror:
            pictures_stats.append(PictureEntry(mirrored=True))
                    
        else:
            remove_list = []
            for picturers in  pictures_stats:
                if picturers.mirrored == True:
                    remove_list.append(picturers)
            for picture in remove_list:
                pictures_stats.remove(picture)
        update_combination(ImageEnum.Brightness,True)
        refresh_previews()
        save_augumatiaion_conf(mirror=mirror)
        

    ui.checkbox(text="Mirrored",value=picture_conf['mirrored'],on_change=lambda e :change_mirror(e.value)) 
    with ui.dropdown_button('Combine with'):
        ui.checkbox(text="Brightness",value=picture_conf['mirrored_combination'][ImageEnum.Brightness.value[0]],on_change=lambda e :update_combination(ImageEnum.Brightness,e.value))

    def add_brightness():
        '''adds Brigthness for the picuteres with a value '''
        val = brightness_input.value
        if val is None:
            return
        pictures_stats.append(PictureEntry(brightness=val))
        brightness_values = []
        for picture in pictures_stats:
            if picture.brightness != picture.brightness not in brightness_values:
                brightness_values.append(picture.brightness)
        save_augumatiaion_conf(brightness=brightness_values)
        refresh_previews()

   
    def startup():
        '''is called when the Page is loaded an ist used to display all the pictures that are used at the moment'''
        change_mirror(picture_conf['mirrored'])
        change_pictures()

    def remove_picture(index:int):
        '''removes the pictures from the page at a Index'''
        pictures_stats.pop(index)
        refresh_previews()
    async def change_pictures(): 
        image_row.clear()
        with image_row:
            for img in pictures_stats:
                for pic in pictures:
                    val = img.brightness
                    image =  transformer.adjust_brightness(pic, val)
                    if img.mirrored:
                        image = transformer.mirror(image)

    brightness_input = ui.number('Brightness value')
    ui.button('Add', icon='add', on_click=add_brightness)

                   
    ui.timer(0, startup, once=True)
    ui.button("Use it on all Pictures", on_click=change_pictures)
    pass

