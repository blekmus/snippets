def firstletter(name):
    if any(char == ' ' for char in name):
        # if sentence
        first, last = name.split(' ')
        first = first.capitalize()
        last = last.capitalize()
        return first + ' ' + last
    else:
        # if word
        return name.capitalize()