import os
import requests
from re import sub
from hashlib import sha256
import sys
import config as c

TanSaysNoNo = c.TanEx

# Given a filepath:s to a contents.txt file, returns the internal text as a string.
def read_content(contents_path):
        try:
            with open(f'{contents_path}/contents.txt', 'r') as file:
                file_contents = file.read()
                return file_contents
        except FileNotFoundError:
            print('No contents.txt in this directory found')
            raise(TanSaysNoNo)

# Takes a filename, returns a safely-formatted filename
def sanitize_filename(filename):
        # Remove invalid characters
        filename = sub(r"[\/:*?'<>|]", '', filename)
        # Replace whitespace characters with an underscore
        filename = filename.replace(' ', '_')
        # Truncate the filename if it is too long
        max_length = 247
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename

# Given content as a string, plus the delimiter to parse it, return arrays of titles and links
def content_to_arrays(content, DELIMITER):
    titles = []
    links = []
    for line in content.splitlines():
        if DELIMITER not in line:
            continue
        try: # Extracting the title and url from each line
            tit, url = line.split(DELIMITER)
        except:
            print('wow, you broke my delimiter!')
            raise(ValueError)
        titles.append(tit)
        links.append(url)
    try: # Double checking formatting (list lengths)
        assert(len(titles) == len(links))
    except:
        print(f'Format must be TITLE + {DELIMITER} + URL')
        raise(TanSaysNoNo)
    return titles, links

# Takes image content, returns its hashed value as a string.
def get_image_hash(image_content):
    hasher = sha256()
    hasher.update(image_content)
    return hasher.hexdigest()        

# Saves images in the form of titles, links to a given folder_path
def save_images(titles, links, folder_path):
    if len(titles) == 0:
        print('List invalid.')
        raise(TanSaysNoNo)
    duplicates = ''
    count = 0
    total_count = 0
    seen = set()
    image_hashes = set()
    
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
            duplicates += (f'Skipping duplicate image: {title}{file_extension}\n')
            print(f'Skipping duplicate image: {title}{file_extension}')
            continue

        # Add the image hash to the set of image hashes
        image_hashes.add(image_hash)
        filename = sanitize_filename(title)

        if filename in seen:
            count+=1
            filename = filename + f'_{count}'
        seen.add(filename)

        # Save the image
        try:
            with open(f'{folder_path}/{filename}{file_extension}', 'wb') as f:
                f.write(res.content)
                total_count+=1
        except:
            print('Welp, unable to save the image')
            raise(TanSaysNoNo)
    return total_count, duplicates

# runs content_to_arrays with error handling
def try_content_to_arrays(content, DELIMITER):
    if content:
        try:
            titles, links = content_to_arrays(content, DELIMITER)
            return titles, links
        except:
            print('Error! Traces back to: content_to_arrays')
            raise(TanSaysNoNo)
    else:
        print('Error? Content empty.')
        return [], []

def make_folder(folder_path):
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        print(f'No worries: The folder {folder_name} already exists')
    except:
        print('Filepath not found!')
        raise(TanSaysNoNo)
    
# runs save_images with error handling, then prints output results
def try_saving_images(titles, links, folder_path):
    if all([titles, links]) == False:
        print('No title/url pairs found')
        return 0, None
    try:
        total_count, duplicates = save_images(titles, links, folder_path)
    except:
        print('Error. Output of save_images is faulty.')
        raise(TanSaysNoNo)

    print(f'There are {len(links)} title*;;*url formatted images')
    print(f'Total unique images: {total_count}')
    return total_count, duplicates


def try_saving_results(filepath, total_count, folder_name, duplicates = None):
    try:
        with open(f'{filepath}/results.txt', 'w') as file:
            file.write(f'Total unique images saved to {folder_name}: {total_count}\nDupe Log:\n{duplicates or "None detected"}')
    except:
        print('Welp, unable to save results.txt')
        raise(TanSaysNoNo)

# Given the filepath of the main reddit folder, the new folder to download to, and the delimiter, runs the downloader
def run_downloader(DELIMITER, filepath, download_folder_path):
    # Read content
    try:
        content = read_content(filepath)
    except:
        print('Add a contents.txt file! I recommend running the link_grabber :D')
        print('Exiting.')
        return
    # Set arrays and make folder
    titles, links = try_content_to_arrays(content, DELIMITER)
    make_folder(download_folder_path)

    #Save images and results
    total_count, duplicates = try_saving_images(titles, links, download_folder_path)
    try_saving_results(filepath, total_count, folder_name, duplicates)

def main(folder_name):
    DELIMITER = c.DELIMITER
    reddit_folder_name = c.reddit_folder_name
    filepath = f'{c.filepath}/{reddit_folder_name}'
    download_folder_path = f'{filepath}/{folder_name}'
    run_downloader(DELIMITER, filepath, download_folder_path)   

if __name__ == '__main__':
    arg_count = len(sys.argv)
    if arg_count > 1:
        arg = sys.argv[1]
        folder_name = arg
    else:
        print('When running from command line, please add an argument after path/to/downloader.py <RENAME_ME>')
        folder_name = 'RENAME_ME'
    main(folder_name)
