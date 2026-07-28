import os
import socket
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from nicegui import ui

from downloader import (
    connect_label_studio,
    download_images,
    fetch_tasks,
    get_local_json,
    get_local_picutrs,
    load_picture_conf,
    load_setup_conf,
    save_tasks,
)
from ImageTransformer import ImageTransformer


def run_without_gui():
    """
    CLI mode — runs the augmentation pipeline without the GUI.

    Usage:
        python main.py --no-gui

    Useful for automated pipelines, servers, or scripting.
    Reads all settings from config.yml instead of the interactive UI.
    """
    conf = load_setup_conf()
    if conf is None:
        print("Critical Error")
        sys.exit(1)

    if not conf["local"]:
        client = connect_label_studio(conf["url"], conf["api_key"], conf["project_id"])
        tasks = fetch_tasks(client, conf["project_id"], conf["only_completed"])

        if not tasks:
            print("No tasks to save. Exiting.")
            sys.exit(0)
        json_path = save_tasks(tasks, conf["output_dir"], conf["project_id"])
        images_paths = download_images(
            tasks, conf["api_key"], conf["url"], conf["output_dir"]
        )
        print("\nDownload complete.")
    else:
        json_path = get_local_json(conf["json_path"])
        images_paths = get_local_picutrs(conf["picture_path"])
    conf = load_picture_conf()

    brightness_list = conf["picture_brightness"]
    brightness_combination = conf["brightness_combination"]
    changed_list = []
    transformer = ImageTransformer(images_paths, json_path, conf["json_output_path"])
    for brightness in brightness_list:
        changed_list += transformer.adjust_brightness(float(brightness))
    if conf["mirrored"]:
        transformer.mirror()
    for strength in conf["gauss_strength"]:
        transformer.add_gaussian_filter(strength)
    if brightness_combination and conf["gauss_combination"]:
        for strength in conf["gauss_strength"]:
            transformer.add_gaussian_filter(strength)


def find_free_port()->int:
    """
        Find an available port on the local machine.

        Binds a temporary socket to port 0, which asks the OS to assign
        an unused ephemeral port, then closes the socket and returns
        that port number for reuse.

        Returns:
            int: An available port number.
        """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main():
    """Main Programm"""
    if "--no-gui" in sys.argv:
        run_without_gui()
        return
    ui.add_css(
        "body { background: #B1D3EF; }.q-card { border-radius: 16px; padding: 2rem; max-width: 560px; width: 100%; }",
        shared=True,
    )
    ui.run(port=find_free_port())


if __name__ in {"__main__", "__mp_main__"}:
    main()
