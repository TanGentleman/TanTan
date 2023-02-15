def main():
    import requests
    import sys
    import mysecrets
    import config as c
    from os import mkdir
    mode = 'image_only'
    filepath = 'Documents/Github/Api_Mastery/ScrapeAndSpredd'
    token_needed = False
    max_count = 150 # Will be overridden by config value if no CLI arguments
    args = sys.argv
    arg_count = len(args)

    if arg_count > 1:
        
        user_input = ''
        sort_type = ''
        time_period = ''     
        debug = False 
        limit_qty = 1
        allow_input = not('-s' in args)

        def valid_arg(arg, index):
            if index == 1:
                try:
                    return arg[:2] in ['r/', 'u/']
                except:
                    return False

            elif arg == '-d': #debug
                return True
            elif arg == '-s': #shortcut - no followup input thru terminal
                return True

            elif index == 2:
                try:
                    return (int(arg) > 0) and (int(arg) <= max_count)
                except:
                    return False
            
            elif index == 3:
                sort_types = ['new', 'top']
                return arg in sort_types
            elif index == 4:
                time_periods = ['all', 'year', 'month', 'week', 'day', 'hour']
                return arg in time_periods
            elif index == 5:
                return arg in ['-d', 'debug']


        def check_args(args, arg_count):
            for i in range(arg_count):
                if valid_arg(args[i], i) == False:
                    print(f'Bad formatting on argument {i}: {args[i]}')
                    if i == 1:
                        print('Please format the first arg as u/user or r/subreddit')
                    if i == 2:
                        print(f'Please format the second arg (quantity) as an integer 1 to {max_count}')

                    if allow_input:
                        response = input('Valid examples:\nr/funny 10 top week\nu/WoozleWozzle 3 -d\nPlease try again: ')
                        args = response.split(' ')
                        args = ['UNUSED'] + args
                        return check_args(args, len(args))
                    else:
                        raise(ValueError)
            return args, arg_count

        args, arg_count = check_args(args, arg_count)
        print(args[1:])
        arg_count = len(args)
        for i in range(arg_count):
            if i == 1:
                user_input = args[i]
            elif args[i] == '-d':
                debug = True   
            elif args[i] == '-s':
                # I think this is redundant
                allow_input = False   
            elif i == 2:
                limit_qty = int(args[i])
            elif i == 3:
                sort_type = args[i]
            elif i == 4:
                time_period = args[i]
        

    else:
        import config as c
        token_needed = c.token_needed
        debug = c.debug
        limit_qty = c.limit_qty
        max_count = c.max_count
        user_input = c.user_input
        sort_type = c.sort_type
        time_period = c.time_period

    def user_input_to_search(user_input):
        prefix, suffix = user_input[:2],user_input[2:]
        if prefix == 'u/':
            search = f'user/{suffix}/submitted'
        elif prefix == 'r/':
            search = f'r/{suffix}/top'
        else:
            raise SyntaxError('Format with u/ or r/ from users and subs')
        return search
    try:
        search = user_input_to_search(user_input)
    except:
        print('Syntax error! Format better!')
        return

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
    
    sort_string = get_sort_string(sort_type, time_period)
    headers = mysecrets.getHeaders(token_needed)
    # You're all set!
    

    def link_grab(headers, limit_qty, search, sort):
        # Define a variable to keep track of the 'after' parameter
        after = None
        # Define a variable to keep track of the number of fetched urls
        count = 0
        # Lists to store the URLs and titles of the images
        image_urls = []
        image_titles = []
        output_string = ''


        after_count = 0
        # Loop until all urls are fetched
        while True:
            # Construct the API URL with the 'after' parameter
            url = f'https://oauth.reddit.com/{search}.json?{sort}&limit=500'
            if after:
                if (after_count > 5) and (limit_qty < 200):
                    if debug: print('Too many after calls!', after_count)
                    else: print('no debug on, but too many calls!', after_count)
                    break
                if after_count > 10:
                    if debug: print('Way too many after calls!', after_count)
                    else: print('no debug on, but way too many calls!', after_count)
                    break

                else:
                    #onto the the next batch!
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

                for post in posts:
                    if 'post_hint' in post['data']:
                        post_hint = post['data']['post_hint']
                        if post_hint in counts:
                            counts[post_hint] += 1
                    else:
                        counts['other'] += 1

                print(counts)
                # Loop through each post
                for post in posts:
                    if mode == 'image_only':
                            
                        if ('post_hint' in post['data']) and (post['data']['post_hint'] in ['image', None]):
                            image_url = post['data']['url']
                            if not image_url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                                continue
                            image_urls.append(image_url)
                            image_titles.append(post['data']['title'])
                            count += 1
                        if count >= limit_qty:
                            break
                
                if (count >= limit_qty) or (count >= max_count):
                    if debug: print(f'maxed out at {count}')
                    break
                # Update the 'after' parameter for the next iteration
                after = data['data']['after']
                
                # If there's no more 'after' parameter, we've reached the end of the results
                if not after:
                    break
            elif res.status_code == 401:
                print('Token expired - gimme a sec')
                token_needed = True
                newHeaders = mysecrets.getHeaders(token_needed)
                return link_grab(newHeaders, limit_qty, search, sort)
            else:
                return f'The Reddit API is not connected ({res.status_code})'

        # Print the number of fetched urls
        if debug: print(f'{count} urls fetched')

        seen = set()
        count = 0
        for url, title in zip(image_urls, image_titles):
            if url in seen:
                continue
            seen.add(url)
            line = f'{title}*;;*{url}'
            print(line)
            output_string += line + '\n' 
            count+=1
        if debug: print(f'total count: {count}')
        return output_string

    # Collect output (debugging statements not included)
    output = link_grab(headers, limit_qty, search, sort_string)

    # Write it to contents.txt
    try:
        mkdir(filepath)
    except FileExistsError:
        pass
        # print(f'The folder {filepath} already exists')
    with open(f'{filepath}/contents.txt', 'w') as file:
        if output == None:
            output = 'Faulty output. No links grabbed.'
        else:
            file.write(output)

if __name__ == '__main__':
    main()
