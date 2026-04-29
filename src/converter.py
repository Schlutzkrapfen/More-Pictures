import os 
import json
from PIL import Image, ImageEnhance,ImageFilter,ImageOps

def change_mirror_labels(path_to_labels,id,file_name):
    copied_result = get_picture_label(path_to_labels,id)
    changed_result =change_path_label(copied_result,file_name)
    changed_result = change_mirror_path(changed_result)
    with open(path_to_labels, 'r') as f:
        data = json.load(f)
        data.append(changed_result)
    with open(path_to_labels, 'w') as f:
        json.dump(data, f, indent=4)
        print("   added the task to the json")
    
def add_labels(path_to_labels,id,file_name):
    copied_result = get_picture_label(path_to_labels,id)
    changed_result =change_path_label(copied_result,file_name)
    with open(path_to_labels, 'r') as f:
        data = json.load(f)
        data.append(changed_result)
    with open(path_to_labels, 'w') as f:
        json.dump(data, f, indent=4)
        print("   added the task to the json")

def get_picture_label(path_to_labels,id):
    with open(path_to_labels, "r") as f:
        data = json.load(f)
    return data[id]

def change_mirror_path(data):
    '''mirrors the labels'''
    for annations in data['annotations']:
        for items in annations['result']:
            if items['type'] != 'rectanglelabels':
                    continue  
            x = items['value']['x']
            width = items['value']['width']
            items['value']['x'] = 100 - x - width
     

    return data

def change_path_label(data,filepath):
    old_path =  data["data"]["image"]
    old_dir = os.path.dirname(old_path)
    file    = os.path.join(old_dir, os.path.basename(filepath))
    data["data"]["image"] =file
    return data

def _apply_transform(image_paths, path_to_label, suffix, transform_fn,label_fn=add_labels):
    """Base helper: open each image, apply transform_fn, save, and label."""
    saved_paths = []
    for i, filepath in enumerate(image_paths):
        #try:
            name, ext = os.path.splitext(filepath)
            new_filepath = f"{name}-{suffix}{ext}"
            with Image.open(filepath) as img:
                result = transform_fn(img)
                result.save(new_filepath)
            saved_paths.append(new_filepath)
            print(f"  Saved: {os.path.basename(new_filepath)}")
            label_fn(path_to_label, i, new_filepath)
        #except Exception as e:
         #   print(f"  Skipping {os.path.basename(filepath)}: {e}")
    return saved_paths


def adjust_brightness(image_paths, path_to_label, factor=1.5):
    '''adjust the brightness of the Image'''
    return _apply_transform(
        image_paths, path_to_label,
        suffix=f"brit-{factor}",
        transform_fn=lambda img: ImageEnhance.Brightness(img).enhance(factor)
    )

def add_gaussian_filter(image_paths, path_to_label, strength=1):
    '''adds an guassian filter to the image'''
    return _apply_transform(
        image_paths, path_to_label,
        suffix=f"gaus-{strength}",
        transform_fn=lambda img: img.filter(ImageFilter.GaussianBlur(radius=strength))
    )

def mirror(image_paths, path_to_label):
    '''mirrors the image'''
    return _apply_transform(
        image_paths, path_to_label,
        suffix="mirrored",
        transform_fn=ImageOps.mirror,
        label_fn=change_mirror_labels
    )
