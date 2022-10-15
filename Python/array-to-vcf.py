def format_nums(numlist, num_code):
    num_base = len(str(len(numlist)))

    formatted = {}
    for x, num in enumerate(numlist):
        formatted[f'{num_code}{str(x).rjust(int(num_base), "0")}'] = num

    return formatted


def save_vcf(numlist, file_path):
    with open(file_path, mode='w') as file:
        for name, num in numlist.items():
            # print(name)
            file.write("BEGIN:VCARD\n")
            file.write("VERSION:3.0\n")
            file.write(f"FN:{name}\n")
            file.write(f"N:;{name};;;\n")
            file.write(f'item1.TEL:{num}\n')
            file.write('END:VCARD\n\n')

    print(f"Wrote {len(numlist)} numbers to {file_path}")


num_list = [...]
save_vcf(format_nums(num_list, 'CODE'), './output.vcf')
