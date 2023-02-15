import os
import requests
import re
from hashlib import sha256
import sys
filepath = "Documents/Github/Api_Mastery/ScrapeAndSpredd"
assert(os.path.isdir(filepath))

def read_content():
        try:
            contents_path = f"{filepath}/contents.txt"
            with open(contents_path, "r") as file:
                file_contents = file.read()
                return file_contents
        except FileNotFoundError:
            print("No contents.txt in this directory found")

def sanitize_filename(filename):
        # Remove invalid characters
        filename = re.sub(r'[\/:*?"<>|]', '', filename)
        
        # Replace whitespace characters with an underscore
        filename = filename.replace(' ', '_')
        
        # Truncate the filename if it is too long
        max_length = 247
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename

def arrays_from_content(content):
        links = []
        titles = []
        for line in content.splitlines():
            if "*;;*" not in line:
                continue
            else:
                try:
                    tit, url = line.split("*;;*")
                except:
                    print("wow, you broke my delimiter!")
                    raise(ValueError)
                links.append(url)
                titles.append(tit)
        return links, titles

def get_image_hash(image_content):
        hasher = sha256()
        hasher.update(image_content)
        return hasher.hexdigest()        

def save_images(titles, links, folder_path):
        duplicates = ""
        count = 0
        tot_count = 0
        seen = set()
        image_hashes = set()
        ######
        assert(len(links)) > 0
        # Loop over each line in the file
        for i in range(len(links)):
            url = links[i]
            title = titles[i]
            
            # Download the file
            res = requests.get(url)
            
            # Extract the file extension from the URL
            _, file_extension = os.path.splitext(url)
            
            # Compute the hash of the image data
            image_hash = get_image_hash(res.content)

            # Check if the image has already been downloaded
            if image_hash in image_hashes:
                # Skip this image
                duplicates += (f"Skipping duplicate image: {title}{file_extension}\n")
                print(f"Skipping duplicate image: {title}{file_extension}")
                continue

            # Add the image hash to the set of image hashes
            image_hashes.add(image_hash)
            filename = sanitize_filename(title)

            if filename in seen:
                count+=1
                filename = filename + f"_{count}"
            seen.add(filename)

            # Save the image
            with open(f"{folder_path}/{filename}{file_extension}", "wb") as f:
                f.write(res.content)
                tot_count+=1
        return tot_count, duplicates

def main():
    content = read_content()
    if content:
        links, titles = arrays_from_content(content)
    else:
        print("Error? Content empty.")
        return

    folder_name = "RENAME_ME"
    tot_count = 0

    arg_count = len(sys.argv)
    if arg_count > 1:
        arg = sys.argv[1]
        folder_name = arg

    folder_path = f"{filepath}/{folder_name}"   

    try:
        os.mkdir(folder_path)
    except FileExistsError:
        print(f"The folder {folder_path} already exists")

    try:
        tot_count, duplicates = save_images(titles, links, folder_path)
    except:
        print("Error. Output of save_images is faulty.")
        raise(ValueError)
    
    print(f"There are {len(links)} title*;;*url formatted images")
    assert(len(links) == len(titles))
    print(f"Total unique images: {tot_count}")

    with open(f"{filepath}/results.txt", "w") as file:
        file.write(f"Total unique images saved to {folder_name}: {tot_count}\n{duplicates}")

if __name__ == "__main__":
    main()
