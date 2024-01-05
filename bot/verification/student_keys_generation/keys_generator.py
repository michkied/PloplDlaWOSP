import random
import string
import json

# Michał Kiedrzyński 01.2024
# Generates keys in the following format:
#       [segment1]-[segment2]-...-[segmentN]
#
# Example key with 4 segments of length 5:
#       1A2B3-C4D5E-6F7G8-H9I0J

SEGMENTS = 4
SEGMENT_LENGTH = 4
SEGMENT_SEPARATOR = '-'


# This function is datasource-specific. Modify it to fit your needs.
# The function should return a list of lists with the following format:
def get_students_data():
    data = [
        ['student_name1', 'class1', 'index_number1'],
        ['student_name2', 'class2', 'index_number2']
    ]
    return data


def generate_key():
    symbols = string.ascii_uppercase + string.digits
    key = ''
    for i in range(1, SEGMENTS + 1):
        key += f"{''.join(random.choices(symbols, k=SEGMENT_LENGTH))}{SEGMENT_SEPARATOR}"
    return key[:-1]


def create_key_lists_by_class(keys_dict):
    classes = {}
    for key in keys_dict:
        if keys_dict[key][1] not in classes:
            classes[keys_dict[key][1]] = [
                [keys_dict[key][2], keys_dict[key][0], key]
            ]
            continue
        classes[keys_dict[key][1]].append([keys_dict[key][2], keys_dict[key][0], key])

    return classes


def format_key_list_into_csv(key_list):
    csv = 'Index;Name;Key\n'
    for key in key_list:
        csv += f"{key[0]};{key[1]};{key[2]}\n"
    return csv


if __name__ == '__main__':
    student_keys_dictionary = {}
    students_data = get_students_data()
    for student in students_data:
        student_keys_dictionary[generate_key()] = student

    with open('../student_keys.json', 'w+', encoding='UTF-8') as f:
        f.write(json.dumps(student_keys_dictionary, indent=4, ensure_ascii=False))

    classes = create_key_lists_by_class(student_keys_dictionary)
    for clss in classes:
        output = format_key_list_into_csv(classes[clss])
        with open(f'keys_by_class/{clss}.csv', 'w+', encoding='UTF-8') as f:
            f.write(output)

    print('Done!')
