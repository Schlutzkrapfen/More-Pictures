import base64
from io import BytesIO

from nicegui import run, ui
from PIL import Image

from downloader import (
    connect_label_studio,
    fetch_tasks,
    get_local_picutrs,
    load_picture_conf,
    load_setup_conf,
    save_tasks,
)
from image_stats import DEFAULT_VALUES, ImageEnum, PictureEntry
from ImageTransformer import ImageTransformer
from utils import save_augumatiaion_conf


@ui.page("/ImageAgumantation")
async def change_picturs():
    setup_conf = load_setup_conf()
    picture_conf = load_picture_conf()
    pictures = get_local_picutrs(setup_conf["output_dir"])
    client = await run.io_bound(
        connect_label_studio,
        setup_conf["url"],
        setup_conf["api_key"],
        setup_conf["project_id"],
    )
    tasks = await run.io_bound(
        fetch_tasks, client, setup_conf["project_id"], setup_conf["only_completed"]
    )
    json_path = await run.io_bound(
        save_tasks, tasks, setup_conf["output_dir"], setup_conf["project_id"]
    )
    transformer = ImageTransformer(pictures, json_path, setup_conf["output_dir"])

    ui.label("What do you want to change: ")

    pictures_stats = [PictureEntry()]
    image_row = ui.grid(columns=2)

    def pil_to_base64(img):
        if isinstance(img, str):
            img = Image.open(img)

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    def refresh_previews():
        """displays every image in image_row"""
        image_row.clear()
        with image_row:
            for i, img in enumerate(pictures_stats):
                brit_val = img.brightness
                gaus_val = img.gaus
                with ui.grid(columns=3):
                    image = transformer.adjust_brightness_to_single(
                        pictures[0], brit_val, tmp_folder=True
                    )
                    image = transformer.add_gaussian_filter_to_single(
                        image, int(gaus_val), tmp_folder=True
                    )
                    if img.mirrored:
                        image = transformer.mirror_single(image, tmp_folder=True)
                    image_src = pil_to_base64(image)

                    ui.image(image_src).style("min-width: 300px; height: auto;")
                    with ui.dropdown_button(auto_close=True).style(
                        "height: 50%,max-width:50px"
                    ):
                        ui.label(f"Brightness: {brit_val}")
                        ui.label(f"Blur Effekt: {gaus_val}")
                        ui.label(f"mirrored:{img.mirrored}")
                    ui.button(
                        icon="delete", on_click=lambda v=i: remove_picture(v)
                    ).props("flat round dense")

    def reset():
        """Reset all the values in the pictures config"""
        save_augumatiaion_conf(reset=True)
        pictures_stats.clear()
        pictures_stats.append(PictureEntry())
        refresh_previews()

    def get_attr(pic, index):
        """Helper to get the relevant attribute based on index."""
        match index:
            case ImageEnum.Brightness:
                return pic.brightness
            case ImageEnum.Gaus:
                return pic.gaus

    def update_combination(index: ImageEnum, value: bool):
        """updtaes the combination of the pictures (works just with mirror at the moment)"""
        if not value:
            remove_items = [
                i
                for i, pic in enumerate(pictures_stats)
                if pic.mirrored and get_attr(pic, index) != DEFAULT_VALUES[index]
            ]

            for i in reversed(remove_items):
                pictures_stats.pop(i)
            refresh_previews()
            return
        save_pictures = []
        if index.value[0] >= len(picture_conf["mirrored_combination"]):
            return

        values = []
        for pic in pictures_stats:
            if pic.mirrored:
                values.append(get_attr(pic, index))
                save_pictures = [
                    PictureEntry(mirrored=True, brightness=p.brightness, gaus=p.gaus)
                    for p in pictures_stats
                    if get_attr(p, index) not in values
                    and get_attr(p, index) != DEFAULT_VALUES[index]
                ]

        pictures_stats.extend(save_pictures)
        refresh_previews()

    def change_mirror(mirror):
        """Adds Mirrror images for the pictures"""
        if mirror:
            combine_dropdown.set_visibility(True)
            pictures_stats.append(PictureEntry(mirrored=True))
            update_combination(ImageEnum.Brightness, True)

        else:
            combine_dropdown.set_visibility(False)
            remove_items = [i for i, pic in enumerate(pictures_stats) if pic.mirrored]

            for i in reversed(remove_items):
                pictures_stats.pop(i)
        save_augumatiaion_conf(mirror=mirror)
        refresh_previews()

    ui.checkbox(
        text="Mirrored",
        value=picture_conf["mirrored"],
        on_change=lambda e: change_mirror(e.value),
    )
    with ui.dropdown_button("Combine with") as combine_dropdown:
        ui.checkbox(
            text="Brightness",
            value=picture_conf["mirrored_combination"][ImageEnum.Brightness.value[0]],
            on_change=lambda e: update_combination(ImageEnum.Brightness, e.value),
        )
        ui.checkbox(
            text="Gaus",
            value=picture_conf["gauss_combination"][ImageEnum.Brightness.value[0]],
            on_change=lambda e: update_combination(ImageEnum.Gaus, e.value),
        )

    def add_brightness(val=None):
        """adds Brigthness for the picuteres with a value"""
        if val is None:
            val = brightness_input.value
        if val is None or val == DEFAULT_VALUES[ImageEnum.Brightness]:
            ui.notify("The Value is Nothing or default value ", type="negative")
            return
        pictures_stats.append(PictureEntry(brightness=val))
        brightness_values = []
        for picture in pictures_stats:
            if (
                picture.brightness not in brightness_values
                and picture.brightness != DEFAULT_VALUES[ImageEnum.Brightness]
            ):
                brightness_values.append(picture.brightness)
        print(brightness_values)
        save_augumatiaion_conf(brightness=brightness_values)
        refresh_previews()

    def add_gaus(val=None):
        """adds a gaus filter to a picture"""
        if val is None:
            val = gaus_input.value
        if val is None or val == DEFAULT_VALUES[ImageEnum.Gaus]:
            ui.notify("The Value is Nothing or default value ", type="negative")
            return
        pictures_stats.append(PictureEntry(gaus=val))
        gaus_values = []
        for picture in pictures_stats:
            if (
                picture.gaus not in gaus_values
                and picture.gaus != DEFAULT_VALUES[ImageEnum.Gaus]
            ):
                gaus_values.append(picture.gaus)
        save_augumatiaion_conf(guas=gaus_values)
        refresh_previews()

    def startup():
        """is called when the Page is loaded an ist used to display all the pictures that are used at the moment"""
        change_mirror(picture_conf["mirrored"])
        for val in picture_conf["picture_brightness"] or []:
            add_brightness(val)
        for val in picture_conf["gauss_strength"] or []:
            add_gaus(val)
        refresh_previews()

    def remove_picture(index: int):
        """removes the pictures from the page at a Index"""
        pictures_stats.pop(index)
        refresh_previews()

    async def change_pictures():
        """!!!NOT WORKING AT THE MOMENT!!!!\n
        Saves the Pictures when after you press the finisch the work"""
        image_row.clear()
        with image_row:
            for img in pictures_stats:
                for pic in pictures:
                    val = img.brightness
                    image = await run.io_bound(
                        transformer.adjust_brightness_to_single, pic, val
                    )
                    if img.mirrored:
                        image = await run.io_bound(transformer.mirror_single, image)
                ui.notify(f"Changed everything image with stats {img}", type="positive")
        ui.notify("This doesen't work at moment", type="negative")

    brightness_input = ui.number(
        "Brightness value", step=0.1, value=DEFAULT_VALUES[ImageEnum.Brightness]
    )
    ui.button(
        "Add",
        icon="add",
        on_click=add_brightness,
    )
    gaus_input = ui.number(
        "Blur value (gauss)", step=0.1, value=DEFAULT_VALUES[ImageEnum.Gaus]
    )
    ui.button(
        "Add",
        icon="add",
        on_click=add_gaus,
    )
    ui.timer(0, startup, once=True)
    ui.button("Use it on all Pictures", on_click=change_pictures)
    ui.button("reset", on_click=reset)
