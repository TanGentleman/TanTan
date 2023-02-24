import requests
import config as c
from os import mkdir
TanSaysNoNo = c.TanEx

# Given valid argument strings for sort_type and time_period, returns formatted sort_string
def get_sort_string(sort_type, time_period):
        type_string = ''
        time_string = ''
        if sort_type:
            type_string = f'sort={sort_type}'
        if time_period:
            time_string = f't={time_period}'

        if sort_type and time_period:
            sort_string = type_string + '&' + time_string
        else:
            sort_string = type_string or time_string

        return sort_string

# Formats the subreddit/user argument into a search string
def user_input_to_search(user_input):
        prefix, suffix = user_input[:2], user_input[2:]
        if prefix == 'u/':
            search = f'user/{suffix}/submitted'
        elif prefix == 'r/':
            search = f'r/{suffix}/top'
        else:
            raise SyntaxError('Format with u/ (for users) or r/ (for subs)')
        return search

# Formats the arrays into a string of title+delimiter+url entries, skipping duplicate urls.
def arrays_to_output_string(image_urls, image_titles, output_string, debug, DELIMITER):
        output_string = ''
        seen = set()
        count = 0
        for url, title in zip(image_urls, image_titles):
            if url in seen:
                continue
            seen.add(url)
            line = f'{title}{DELIMITER}{url}'
            print(line)
            output_string += line + '\n' 
            count+=1
        if debug: print(f'total count: {count}')
        return output_string
        
# Given the current count, batch of posts, current url/title list, returns updated lists and count.
def get_urls_and_titles(count, posts, image_only, image_urls, image_titles, limit_qty, max_file_size, debug):
    # Loop through each post
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif')
   
    for post in posts:
        # Check if post_hint is image, video, or None
        if ('post_hint' in post['data']) and (post['data']['post_hint'] in ['image', 'video' if not(image_only) else None, None]):
            image_url = post['data']['url']
            # Allow mp4 if image_only is False
            if image_only == False:
                valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp4')
            # Skips if image url doesn't have a valid extension
            if not image_url.endswith(valid_extensions):
                continue
            # Filter out large gif/mp4 files
            if image_url.endswith(('.gif', 'mp4')):
                res = requests.head(image_url)  # Make a HEAD request to get response headers
                if 'content-length' in res.headers:  # Check if content-length is present in headers
                    file_size = int(res.headers['content-length']) / 1024  # Convert bytes to KB and store as an integer
                    print(f'URL: {image_url}, File Size (in KB): {file_size}')

                    # If the file is a gif or mp4, check if it's too large.  If so, skip it.  Otherwise, save it
                    if file_size < max_file_size:
                        if debug: print('Saving')
                    else:
                        if debug: print('Skipping')
                        continue
                else:
                    if debug: print(f'URL not added!: {image_url}')
                    continue

            # Save the url and title to their respective lists, and increment count by 1
            image_urls.append(image_url)
            image_titles.append(post['data']['title'])
            count += 1
        # If count exceeds limit_qty, breaks out of loop
        if count >= limit_qty:
            break
    return image_urls, image_titles, count

# Displays post_hints for a json batch of posts
def display_hints(counts, posts):
    for post in posts:
        if 'post_hint' in post['data']:
            post_hint = post['data']['post_hint']
            if post_hint in counts:
                counts[post_hint] += 1
        else:
            counts['other'] += 1
    return counts

# Refresh token and return updated headers
def refresh_token(getHeaders):
    print('Token expired - gimme a sec')
    token_needed = True
    newHeaders = getHeaders(token_needed)
    return newHeaders

# Returns 
def link_grab(DELIMITER, debug, getHeaders, headers, image_only, limit_qty, max_count, search, sort_string, max_file_size):
        # Define a variable to keep track of the 'after' parameter
        after = None
        # Define a variable to keep track of the number of fetched urls
        count = 0
        # Lists to store the URLs and titles of the images
        image_urls = []
        image_titles = []
        output_string = ''
        if count > 10:
            json_limit = 100
        else:
            json_limit = 25
        after_count = 0
        # Loop until all urls are fetched
        while ((count < limit_qty) and (count < max_count)):
            # Construct the API URL with the 'after' parameter
            url = f'https://oauth.reddit.com/{search}.json?{sort_string}&limit={json_limit}'
            if after:
                if after_count == 3: # After 3 batches checked
                    if count < 2: # insufficient files found with given parameters
                        print(f'Too many after calls! {after_count} paginations')
                        return(output_string)
                if after_count > 5:
                    if count < 5: # insufficient files found with given parameters
                        print(f'Too many after calls! {after_count} paginations')
                        return(output_string)
                    if count/limit_qty < 0.5: # If less than 50% of request has been completed
                        print(f'Too many after calls! {after_count} paginations')
                        print(f'Aborting early!')
                        return(output_string)
                
                if after < 15:
                    print(f'Too many after calls! {after_count} paginations')
                    print(f'Aborting early!')
                    return(output_string)
                else:
                    # Appends to the url string to move onto the the next batch!
                    url = f'{url}&after={after}'
                    after_count+=1
                    
            # Send a GET request to the API
            res = requests.get(url, headers=headers)

            # Check if the API response was successful
            if res.status_code == 200:
                # Parse the JSON data returned by the API
                data = res.json()
                posts = data['data']['children']
                counts = {'image': 0, 'text': 0, 'video': 0, 'rich:video': 0, 'hosted:video': 0, 'link': 0, 'self': 0, 'other': 0}
                counts = display_hints(counts, posts)

                if debug: print(f'Pagination #{after_count}:\n{counts}')
                image_urls, image_titles, count = get_urls_and_titles(count, posts, image_only, image_urls, image_titles, 
                                                                        limit_qty, max_file_size, debug)
                
                # Update the 'after' parameter for the next iteration
                after = data['data']['after']
                
                # If there's no more 'after' parameter, we've reached the end of the results
                if not after:
                    break
            # If reddit token is expired, refresh and try again
            elif res.status_code == 401:
                newHeaders = refresh_token(getHeaders)
                return link_grab(DELIMITER, debug, getHeaders, newHeaders, image_only, limit_qty, max_count, search, sort_string, max_file_size)
            else:
                return f'The Reddit API is not connected ({res.status_code})'

        # Print the number of fetched urls
        if debug: print(f'{count} urls fetched')
        output_string = arrays_to_output_string(image_urls, image_titles, output_string, debug, DELIMITER)
        return output_string


def main(user_input, limit_qty, sort_type, time_period, max_count, debug):
    image_only = c.image_only
    filepath = f'{c.filepath}/{c.reddit_folder_name}'
    token_needed = c.token_needed
    getHeaders = c.getHeaders
    DELIMITER = c.DELIMITER
    max_file_size = c.max_file_size

    try:
        search = user_input_to_search(user_input)
    except:
        print('Syntax error! Format better!')
        return
    try:
        headers = getHeaders(token_needed)
    except:
        print('Issue with authorization. Please read above and troubleshoot.')
        return

    sort_string = get_sort_string(sort_type, time_period)
    
    # Collect output (debugging statements not included)
    output = link_grab(DELIMITER, debug, getHeaders, headers, image_only, limit_qty, max_count, search, sort_string, max_file_size)
    if output == None:
        print('Faulty output. No links grabbed.')
        return
    # Write it to contents.txt
    try:
        mkdir(filepath)
    except FileExistsError:
        pass
        # print(f'The folder {filepath} already exists')
    try:
        with open(f'{filepath}/contents.txt', 'w') as file:
            file.write(output)
    except:
        print('Error. Could not write to contents.txt')

def valid_arg(arg, index, max_count):
    # user_input
    if index == 1:
        try:
            return arg[:2] in ['r/', 'u/']
        except:
            print('Argument 1 must have a prefix of r/ or u/')
            return False
    # limit_qty
    elif index == 2:
        try:
            return (int(arg) > 0) and (int(arg) <= max_count)
        except:
            print(f'Argument 2 must be a valid quantity from 1 to {max_count}')
            return False
    # sort_type
    elif index == 3:
        sort_types = ['new', 'top']
        return arg in sort_types
    # time_period
    elif index == 4:
        time_periods = ['all', 'year', 'month', 'week', 'day', 'hour']
        return arg in time_periods

def check_args(args, arg_count, max_count, allow_input):
    unused_filename = args[0]
    args[0] = 'UNUSED' # No current use case for args[0] (filename)
    for i in range(arg_count):
        if i == 0: # Unused element
            continue
        if valid_arg(args[i], i, max_count) == False:
            print(f'Bad formatting on argument {i}: {args[i]}')
            if i == 1:
                print('Please format the first arg as u/user or r/subreddit')
            if i == 2:
                print(f'Please format the second arg (quantity) as an integer 1 to {max_count}')
            
            if allow_input:
                response = input('Valid examples:\nr/funny 10 top week\nu/WoozleWozzle 3 -d\nPlease try again: ')
                args = response.split(' ')
                args = [unused_filename] + args
                arg_count = len(args)
                return check_args(args, arg_count, max_count, allow_input)
            else:
                print('Gotta be an expert to use the shortcuts app')
                raise(TanSaysNoNo)
    return args, arg_count

# Takes the arguments from the command line and sets the input variables for main()
def set_vars_from_args(max_count, args, arg_count, allow_input):
    user_input = ''
    sort_type = ''
    time_period = ''     
    debug = False
    limit_qty = 1
    try: # check if arguments are valid.  If not, raise an error.
        args, arg_count = check_args(args, arg_count, max_count, allow_input)
    except: # Error - possibly -s flagged invalid magic string
        print("Error. Likely using a shortcut with error in args.")
        raise(TanSaysNoNo)
   
    print(f'Arguments: {args[1:]}') # prints the list of arguments
    arg_count = len(args) # sets arg_count to the number of arguments in args
    
    for i in range(arg_count):
        if i == 1:
            # Set user_input to the first argument in args. This will be used as input for user_input_to_search.
            user_input = args[i]
        elif i == 2:
            # Set limit_qty to second argument in args (default is 1)
            limit_qty = int(args[i])
        elif i == 3:
            # Set sort_type string to third argument in args (default is None)
            sort_type = args[i]
        elif i == 4:
            # Set time_period string to third argument in args (default is None)
            time_period = args[i]
    return user_input, limit_qty, sort_type, time_period

if __name__ == '__main__':
    import sys
    args = sys.argv
    arg_count = len(args)
    max_count = c.max_count
    debug = c.debug
    
    # If arguments are found
    if arg_count > 1:
        # Check for flags
        # If -s flag is used, disallow input retrying (since that's terminal-only)
        if '-s' == args[1]:
            args.remove('-s')
            arg_count -= 1
            allow_input = False
        else:
            allow_input = True
        # If -d flag is used, set debug to True
        if '-d' in args:
            args.remove('-d')
            arg_count -= 1
            debug = True

    # If a magic string is used
    if arg_count > 1:
        user_input, limit_qty, sort_type, time_period = set_vars_from_args(max_count, args, arg_count, allow_input)
    else:
        user_input = c.user_input
        limit_qty = c.limit_qty
        sort_type = c.sort_type
        time_period = c.time_period

    main(user_input, limit_qty, sort_type, time_period, max_count, debug)
