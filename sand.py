input_vars = "debug, image_only, max_count, newHeaders, limit_qty, search, sort_string, DELIMITER, getHeaders"
output_vars = input_vars
a = []
for i in input_vars.split(', '):
    a.append(i)

input_vars_array = sorted(a)

for i in input_vars_array:
    print(i, end = ", ")

to_pop = []
for i in to_pop:
    input_vars_array.remove(i)

print()
output_vars_array = input_vars_array

for i in output_vars_array:
    print(i, end = ", ")
