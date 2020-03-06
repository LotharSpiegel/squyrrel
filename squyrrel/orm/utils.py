

def extract_ids(string):
    if string:
        ids = string[1:-1].split(',')
        ids = [int(id.strip()) for id in ids]
        return ids
    else:
        return []