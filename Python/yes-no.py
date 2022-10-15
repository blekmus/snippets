# recursive y/n input with default
def yesno(question, default=None):
    ans = input(question).strip().lower()

    if default is not None:
        if ans == '':
            if default == 'y':
                return True
            return False
        elif ans not in ['y', 'n']:
            print(f'{ans} is invalid, please try again...')
            return yesno(question)
        if ans == 'y':
            return True
    else:
        if ans not in ['y', 'n']:
            print(f'{ans} is invalid, please try again...')
            return yesno(question)
        if ans == 'y':
            return True

    return False
