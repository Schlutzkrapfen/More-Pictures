import yaml
def save_setup_conf(url = None,api_key= None,project_id:int = None,dow_output =None , conf: dict =None,picture_path = None, json_file = None, path: str = "config.yml"):
    '''saves everything to a yml if let empty the part of the yml will not be changed'''
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
        if json_file != None:
            config['local']['json_path'] = json_file
        if picture_path != None:
            config['local']['picture_path'] = picture_path

        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print("Save worked")
    except Exception as e:
        print(f"Save failed: {e}")

def save_augumatiaion_conf(conf: dict =None,mirror:bool = None,mirror_combination = None,brightness = None,  path: str = "config.yml"):
    '''saves everything for the picuter fiels to a yml if let empty the part of the yml will not be changed'''
    try:
        if conf != None:
            with open(path, 'w') as f:
                yaml.dump(conf, f, default_flow_style=False, sort_keys=False, default_style=None)
        

        with open(path, "r") as f:
            config = yaml.safe_load(f)
        if mirror != None:
            config['mirrored']['mirrored'] = mirror
        if brightness != None:
            config['brigtness']['brigtness_list'] = brightness
        if mirror_combination != None:
            config['mirrored']['mirrored_combination'] = mirror_combination
        
        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print("Save worked")
    except Exception as e:
        print(f"Save failed: {e}")
