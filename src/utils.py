import yaml


def save_setup_conf(
    url: str | None = None,
    api_key: str | None = None,
    project_id: int | None = None,
    dow_output: str | None = None,
    conf: dict | None = None,
    picture_path: str | None = None,
    json_file: str | None = None,
    path: str = "config.yml",
):
    """saves everything to a yml if let empty the part of the yml will not be changed"""
    #  try:
    if conf is not None:
        with open(path, "w") as f:
            yaml.dump(
                conf,
                f,
                default_flow_style=False,
                sort_keys=False,
                default_style=None,
            )

    with open(path, "r") as f:
        config = yaml.safe_load(f)
    if url is not None:
        config["label_studio"]["url"] = url
    if api_key is not None:
        config["label_studio"]["api_key"] = api_key
    if project_id is not None:
        config["label_studio"]["project_id"] = project_id
    if dow_output is not None:
        config["download"]["output_dir"] = dow_output
    if json_file is not None:
        config["local"]["json_path"] = json_file
    if picture_path is not None:
        config["local"]["picture_path"] = picture_path

    print(config)
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    print("Save worked")


# except Exception as e:
#     print(f"Save failed: {e}")


def save_augumatiaion_conf(
    conf: dict | None = None,
    mirror: bool | None = None,
    mirror_combination: list[bool] | None = None,
    brightness: list[int] | None = None,
    guas: list[int] | None = None,
    path: str = "config.yml",
    reset: bool = False,
):
    """saves everything for the picuter fiels to a yml if let empty the part of the yml will not be changed"""
    try:
        if conf is not None:
            with open(path, "w") as f:
                yaml.dump(
                    conf,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    default_style=None,
                )

        with open(path, "r") as f:
            config = yaml.safe_load(f)
        if reset:
            config["mirrored"]["mirrored"] = False
            config["mirrored"]["mirrored_combination"] = []
            config["brightness"]["brigtness_list"] = []
            config["gauss"]["gauss_list"] = []
        if mirror is not None:
            config["mirrored"]["mirrored"] = mirror
        if mirror_combination is not None:
            config["mirrored"]["mirrored_combination"] = mirror_combination
        if brightness is not None:
            config["brightness"]["brigtness_list"] = brightness
            print(brightness)
        if guas is not None:
            config["gauss"]["gauss_list"] = guas

        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print("Save worked")
    except Exception as e:
        print(f"Save failed because of {e}")
