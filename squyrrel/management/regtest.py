import re

regex = r'".+?"|[\w-]+'

s = 'teste diesen String uh "blabla" juhu urgs="arg" aha'
a = re.findall(regex, s)
#user_inputs = re.split(regex, user_input)#user_input.split()

print(a)

b = re.split(regex, s)
print(b)
print(type(b))