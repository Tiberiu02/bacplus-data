import requests
import favicon
import sqlite3
import os
from dotenv import load_dotenv
from tqdm import tqdm
from tqdm import tqdm
import re
from PIL import Image

load_dotenv()

input_path = "data/icons-curated"
output_path = "data/output-icons"

icons = os.listdir(input_path)


def process_and_save_image(input_path, output_path):
    # Open the image
    with Image.open(input_path) as img:
        width, height = img.size

        # Make the image square by expanding with transparency
        if width != height:
            new_size = max(width, height)
            new_img = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
            new_img.paste(img, ((new_size - width) // 2, (new_size - height) // 2))
            img = new_img

        # Resize if larger than 32x32
        if img.size[0] > 32 or img.size[1] > 32:
            img = img.resize((32, 32))

        # Save the image
        img.save(output_path, format="PNG")


conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

licee = cur.execute(
    "SELECT id_liceu, website, rank FROM licee WHERE website is not null ORDER BY id_liceu ASC"
).fetchall()

duplicates_found = False

for i, (id_liceu, website, rank) in list(enumerate(licee)):
    icons_liceu = [
        icon
        for icon in icons
        if re.match(r"{}(_\d+)?\.(png|ico|jpg|jpeg|gif)".format(id_liceu), icon)
    ]

    if len(icons_liceu) > 1:
        if not duplicates_found:
            duplicates_found = True
            print("Please remove duplicates:")
        print(id_liceu)

if duplicates_found:
    exit(1)

for i, (id_liceu, website, rank) in tqdm(list(enumerate(licee))):
    icons_liceu = [
        icon
        for icon in icons
        if re.match(r"{}(_\d+)?\.(png|ico|jpg|jpeg|gif)".format(id_liceu), icon)
    ]

    if len(icons_liceu) == 0:
        continue

    icon = icons_liceu[0]

    process_and_save_image(
        os.path.join(input_path, icon),
        os.path.join(output_path, "{}.png".format(id_liceu)),
    )
