import csv


def extract_nums(file_path, column_name):
    numlist = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            num = "".join(row[column_name].split())

            unwanted_chars = ['+', '-']
            for char in unwanted_chars:
                num = num.replace(char, '')

            if num.startswith('94'):
                num = num.replace(num[:2], '', 1)

            if num.startswith('0'):
                num = num.replace(num[:1], '', 1)

            if not num.startswith('7'):
                print(f"Omitted {num}")
                continue

            numlist.append(num)

    return list(set(numlist))


num_list = extract_nums('numlist.csv', 'Number')
