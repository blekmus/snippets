import csv


def read_csv(filename):
    items = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            items.append({'First': row['first'], 'Second': row['second']})
    return items