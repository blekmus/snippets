import csv

def save_to_csv(filename, item_list):
    file = open(filename, 'w')

    # init sheet rows
    fieldnames = [
        'Column 1',
        'Column 2',
    ]

    # init csv writer
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # loop through list and add them as rows
    for item in item_list:
        writer.writerow({
            'Column 1': item['first'],
            'Column 2': item['second'],
        })

    file.close()
