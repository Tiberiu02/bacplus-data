import requests
import favicon
import sqlite3
import os
from dotenv import load_dotenv
from tqdm import tqdm
from tqdm import tqdm
import re
from PIL import Image
import shutil

load_dotenv()

input_path = "data/icons"
output_path_xs = "../bacplus/public/icons-xs"
output_path_lg = "../bacplus/public/icons-lg"

icon_files = os.listdir(input_path)


def process_and_save_image(input_path, output_path, max_size, min_size=None):
    # Open the image
    with Image.open(input_path) as img:
        width, height = img.size

        # Skip if smaller than min_size
        if min_size is not None and (width < min_size and height < min_size):
            return

        # Make the image square by expanding with transparency
        if width != height:
            new_size = max(width, height)
            if img.has_transparency_data:
                new_img = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
            else:
                new_img = Image.new("RGB", (new_size, new_size), (255, 255, 255))
            new_img.paste(
                img,
                ((new_size - width) // 2, (new_size - height) // 2),
                img.convert("RGBA"),
            )
            img = new_img

        # Resize if larger than 32x32
        if img.size[0] > max_size or img.size[1] > max_size:
            img = img.resize((max_size, max_size))

        # Save the image
        img.save(output_path, format="WEBP")


conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

institutii = cur.execute("SELECT id FROM institutii").fetchall()

# print(institutii)

duplicates_found = False

for (id,) in institutii:
    icons = [
        icon
        for icon in icon_files
        if re.match(r"{}(_\d+)?\.(png|ico|jpg|jpeg|gif|webp|svg)".format(id), icon)
    ]

    if len(icons) > 1:
        if not duplicates_found:
            duplicates_found = True
            print("Please remove duplicates:")
        print(id)

    if len(icons) == 1 and icons[0].endswith(".svg"):
        print("SVG not supported:", id)
        print("Please convert to PNG and remove the SVG file")
        exit(1)

if duplicates_found:
    exit(1)

# Remove and recreate output directory
if os.path.exists(output_path_xs):
    shutil.rmtree(output_path_xs)
os.mkdir(output_path_xs)

if os.path.exists(output_path_lg):
    shutil.rmtree(output_path_lg)
os.mkdir(output_path_lg)

for (id,) in institutii:

    # print("Processing icon for", id)
    icons = [
        icon
        for icon in icon_files
        if re.match(r"{}(_\d+)?\.(png|ico|jpg|jpeg|gif|webp|svg)".format(id), icon)
    ]

    if len(icons) == 0:
        continue

    icon = icons[0]

    process_and_save_image(
        os.path.join(input_path, icon),
        os.path.join(output_path_xs, "{}.webp".format(id)),
        max_size=32,
    )

    process_and_save_image(
        os.path.join(input_path, icon),
        os.path.join(output_path_lg, "{}.webp".format(id)),
        max_size=320,
        min_size=96,
    )
