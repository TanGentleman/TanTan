# This file is still under development

import openai
import requests
from tansecrets import openai_key
from io import BytesIO
from PIL import Image

filepath = 'Documents/GitHub/Api_Magic/'
debug = True
generation = False
variant = False

def save_file(filepath, content):
    with open(filepath, "wb") as f:
        f.write(content)


def image_from_prompt(prompt):
    openai.api_key = openai_key

    try:
        response = openai.Image.create(
            prompt=prompt,
            size="256x256",
            n=1,
            response_format="url"
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return
# Extract the image URL
    image_url = response["data"][0]["url"]

# Fetch the image data
    if debug:
        print(image_url)
    res = requests.get(image_url)
    image_data = res.content

    filename = prompt.replace(" ", "_") + ".png"
    return filename, image_data

""" Enter filename and url to get image_data """
def manual():
    user_input = input("Enter a title for the image: ")
    filename = user_input
    user_input = input("Enter a link for the image: ")
    url = user_input
    res = requests.get(url)
    image_data = res.content
    return filename, image_data

#Takes in a filepath to an image, returns url of a generated variant.
def image_from_image(filepath):
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
        size="256x256"
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return

    image_url = response["data"][0]["url"]
    print(image_url, "This one should've been different")
    # filename = prompt.replace(" ", "_") + ".png"
    res = requests.get(image_url)
    image_data = res.content
    return image_data


def save_images(prompts, urls):
    # Need prompts array and urls array of equal length
    file_extension = ".png"
    size = len(prompts)
    assert(len(urls) == size)


    for i in range(size):
        res = requests.get(urls[i])
        with open(f"{filepath}/{prompts[i][:20]}{file_extension}", "wb") as f:
                f.write(res.content)
                if debug: print("image saved")



def interactive_chat():
    prompts = []
    limit_qty = -1
    count = 0
    while limit_qty < 0:
        user_input = input("Enter an integer quantity: ")
        try:
            limit_qty = int(user_input)
            if (limit_qty < 0) or (limit_qty > 10):
                assert(False)
            elif limit_qty == 0:
                print("No images saved.")
                return []
        except:
            print("Please format correctly. Enter an integer value.")


    while len(prompts) < limit_qty:
        #Ask for input
        
        prompt = input("Enter a prompt: ")
        if prompt == "quit":
            print(f"Prompts: {prompts}")
            return
        elif prompt == "del":
            if len(prompts) > 0:
                deleted_prompt = prompts.pop()
                print(f"Prompt has been deleted: {deleted_prompt}")
                count = count - 1
            else:
                print("invalid deletion")
                assert(False)
        else:
            prompts.append(prompt)
            print("Prompt added to list")
            print(f"Prompts: {prompts}")
            assert(prompts[count] == prompt)
            count = count + 1
    print("sending over prompt list promptly!")
    return prompts

def generate_variant(source_filepath, destination_filepath):
    image_data = image_from_image(source_filepath)
    save_file(destination_filepath, image_data)

def main():
    prompt = ""
    prompts = []
    urls = []
    debug = False
    if generation:
        prompts = interactive_chat()
        if prompts:
            for prompt in prompts:
                image_url = image_from_prompt(prompt)
                if debug: print("Fetched url!")
                urls.append(image_url)
            print("About to save 'em to the folder!")
        save_images(prompts, urls)
    
    elif variant:
        source_filepath, destination_filepath = None, None
        generate_variant(source_filepath, destination_filepath)
    

if __name__ == "__main__":
    main()
