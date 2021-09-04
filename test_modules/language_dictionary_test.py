import csv

_iso_639_1_codes_file = open("files/ISO-639-1_Codes.csv", mode='r')
_iso_639_1_codes_dictreader = csv.DictReader(_iso_639_1_codes_file)

_iso_639_1_codes_dict: dict = {}
for _row in _iso_639_1_codes_dictreader:
    _iso_639_1_codes_dict[_row['ISO-639-1 Code']] = _row['Language']

print(str(_iso_639_1_codes_dict))