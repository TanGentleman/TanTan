input_vars = "var4, var1, var2, var3"
output_vars = input_vars
a = []
for i in input_vars.split(', '):
    a.append(i)

input_vars_array = sorted(a)

for i in input_vars_array:
    print(i, end = ", ")

to_pop = ["var2"]
for i in to_pop:
    input_vars_array.remove(i)

print()
output_vars_array = input_vars_array

for i in output_vars_array:
    print(i, end = ", ")
