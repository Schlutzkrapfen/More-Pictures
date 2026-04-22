import os 

from PIL import Image, ImageEnhance

def adjust_brightness(image_paths, brightness_factor=1.5):
    '''Adjust the brightness of the picutre and saves it as {picutrename}-btightness.png'''
    for filepath in image_paths:
        try:
            with Image.open(filepath) as img:
                enhancer = ImageEnhance.Brightness(img)
                brightened = enhancer.enhance(brightness_factor)
                name, ext = os.path.splitext(filepath)
                filepath = f"{name}-brightness{ext}"
                brightened.save(filepath)
                print(f"  Brightness adjusted: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"  Skipping {os.path.basename(filepath)}: {e}")





