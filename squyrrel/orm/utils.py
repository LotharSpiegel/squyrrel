

def extract_ids(string):
    if string and string[0] == '[':
        string = string[1:-1]
        if not string:
            return []
        ids = string.split(',')
        return [int(id.strip()) for id in ids]
    else:
        return []