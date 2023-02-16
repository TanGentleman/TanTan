input_vars = "prompt, response, debug, start_time, cached_history, history, full_log, prompt_token_count, response_token_count, response_count, correlation_log"
output_vars = input_vars
a = []
for i in input_vars.split(', '):
    a.append(i)

input_vars_array = sorted(a)

for i in input_vars_array:
    print(i, end = ", ")

for i in ["debug", "prompt", "response", "start_time"]:
    input_vars_array.remove(i)


print()
output_vars_array = input_vars_array



for i in output_vars_array:
    print(i, end = ", ")