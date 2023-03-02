# This file is still under development

import openai
import requests
import config as c
from io import BytesIO
from PIL import Image
import Downloader

max_limit = 10
default_size = '256x256'
filepath = c.filepath + '/DallE'

size_dict = {'small': '256x256', 'medium': '512x512', 'large': '1024x1024', 'default': default_size}


debug = True
openai_key = c.get_openai_api_key()



# Takes a filename, returns a safely-formatted filename
sanitize_filename = Downloader.sanitize_filename

def image_data_from_url(image_url):
    res = requests.get(image_url)
    image_data = res.content
    return image_data

def url_from_prompt(prompt, image_size):
    openai.api_key = openai_key
    try:
        response = openai.Image.create(
            prompt=prompt,
            size=size_dict[image_size],
            n=1,
            response_format='url'
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return
# Extract the image URL
    image_url = response['data'][0]['url']
    filename = sanitize_filename(prompt) + '.png'
    return image_url, filename

#Takes in a filepath to an image, returns url of a generated variant.
def image_from_image(filepath, image_size):
    openai.api_key = openai_key
    image = Image.open(filepath)
    # Convert the image to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_array = byte_stream.getvalue()
    try:
        response = openai.Image.create_variation(
        image=byte_array,
        n=1,
        size=size_dict[image_size]
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return
    try:
        image_url = response['data'][0]['url']
    except:
        print('Error: No image returned from OpenAI')
    return image_url

def prompts_from_input():
    prompts = []
    limit_qty = -1
    count = 0
    while limit_qty < 0:
        user_input = input('Enter an integer quantity: ')
        try:
            limit_qty = int(user_input)
        except:
            print('Please format correctly. Enter an integer value.')    
        if (limit_qty < 0) or (limit_qty > max_limit):
            print(f'Please enter a value between 0 and {max_limit}.')
        elif limit_qty == 0:
            print('No images saved.')
            return []

    while len(prompts) < limit_qty:
        #Ask for input   
        prompt = input('Enter a prompt: ')
        if prompt == 'quit':
            print(f'Prompts: {prompts}')
            return
        elif prompt == 'del':
            if len(prompts) > 0:
                deleted_prompt = prompts.pop()
                print(f'Prompt has been deleted: {deleted_prompt}')
                count = count - 1
            else:
                print('invalid deletion')
                assert(False)
        else:
            prompts.append(prompt)
            print('Prompt added to list')
            print(f'Prompts: {prompts}')
            assert(prompts[count] == prompt)
            count = count + 1
    print('sending over prompt list promptly!')
    return prompts



def generate_images_from_prompts(filepath, image_size, prompts = None):
    urls = []
    titles = []
    if prompts == None:
        prompts = prompts_from_input()
    if prompts:
        for prompt in prompts:
            try:
                url, tit = url_from_prompt(prompt, image_size)
            except:
                print('Error: No url returned from url_from_prompt')
            print('Fetched url!')
            if url:
                urls.append(url)
            else:
                print('no url?')
            if tit:
                titles.append(tit)
            else:
                print('no title?')
        print('About to save them to the folder!')
    else:
        print('No prompts were given.')
        return
    Downloader.save_images(titles, urls, filepath)
    print('Images saved :)')

def main():
    # Option 1
    generate_images_from_prompts(filepath, 'default')
    # Option 2
    # source_filepath, destination_filepath = None, None
    # generate_variant(source_filepath, destination_filepath)
    

if __name__ == '__main__':
    main()

def generate_variant(source_filepath, destination_filepath):
    image_url = image_from_image(source_filepath)
    save_file_from_url(destination_filepath, image_url)
    
def save_file_from_url(filepath, url):
    res = requests.get(url)
    if res.content:
        print('yay')
        with open(filepath, 'wb') as f:
            f.write(res.content)
    else:
        print('nay')
    