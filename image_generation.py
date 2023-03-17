# This file is still under development

import openai
import requests
import config as c
import os 
from io import BytesIO
from PIL import Image
import Downloader

filepath = os.path.join(c.filepath, 'DallE')
if not os.path.exists(filepath):
    os.mkdir(filepath)

size_dict = {'small': '256x256', 'medium': '512x512', 'large': '1024x1024', 'default': '256x256'}

openai_key = c.get_openai_api_key()
# Takes a filename, returns a safely-formatted filename
sanitize_filename = Downloader.sanitize_filename

MAX_LIMIT = 10
DEFAULT_SIZE = size_dict['small']

class QuitAndSaveError(Exception): pass
def check_quit(text: str) -> None:
    '''
    Raises a QuitAndSaveError if the user types -q or quit
    '''
    if text in ['-q','quit']:
        raise QuitAndSaveError

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

# Takes in a filepath to an image, returns url of a generated variant.
def image_url_from_image(filepath, image_size, masked = False, var_prompt = None):
    openai.api_key = openai_key
    image = Image.open(filepath)
    # Convert the image to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_array = byte_stream.getvalue()
    if not masked:
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

    else:
        image2 = Image.open(f'{c.filepath}/DallE/mask.png')
        byte_stream2 = BytesIO()
        image2.save(byte_stream2, format='PNG')
        byte_array2 = byte_stream2.getvalue()

        try:
            response = openai.Image.create_edit(
                image=byte_array,
                mask=byte_array2,
                prompt=var_prompt,
                n=1,
                size="1024x1024"
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
        user_input = input('How many images would you like? (Type 0 to exit): ')
        check_quit(user_input)
        try:
            limit_qty = int(user_input)
        except:
            print('Please format correctly. Enter an integer value.')    
        if (limit_qty < 0) or (limit_qty > MAX_LIMIT):
            print(f'Please enter a value between 0 and {MAX_LIMIT}.')
        elif limit_qty == 0:
            print('No images saved.')
            return []

    while len(prompts) < limit_qty:
        #Ask for input   
        prompt = input('Enter a prompt: ')
        check_quit(prompt)
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
        try:
            prompts = prompts_from_input()
        except:
            raise QuitAndSaveError
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
    # needs a better helper function to clarify filename/filepath
    #source_filepath, destination_filepath = (f'{filepath}/something' + '/example_image.png'), filepath + '/new_image_name.png'
    # generate_variant(source_filepath, destination_filepath, 'medium')
    



def generate_variant(source_filepath, destination_filepath, image_size, masked = False, var_prompt = None):
    image_url = image_url_from_image(source_filepath, image_size, masked, var_prompt)
    save_file_from_url(destination_filepath, image_url)
    
def save_file_from_url(filepath, url):
    res = requests.get(url)
    if res.content:
        print('yay')
        with open(filepath, 'wb') as f:
            f.write(res.content)
    else:
        print('nay')

if __name__ == '__main__':
    main()

    if False:
        # This is just testing, make sure to have file existence checks
        FILENAME = 'an_oil_painting_of_an_indian_grandmother_sitting_with_her_grandson,_a_cavalier_king_charles_spaniel_(blenheim),_and_a_tortoiseshell_cat_colored_black_and_ginger.png'
        NEW_FILENAME = 'TanAddition.png'
        generate_variant(f'{filepath}/{FILENAME}', f'{filepath}/{NEW_FILENAME}', 'large', masked = True, var_prompt = 'An oil painting with a grandma, a dog, a cat, and Abraham Lincoln wearing a hot pink hat')
