import json
import requests

api_json = requests.get(
    "https://api.dictionaryapi.dev/api/v2/entries/en/bright").json()[0]

# print(json.dumps(txt, indent=4))

print(api_json["phonetic"])
print()

for meaning in api_json['meanings']:
    print(meaning['partOfSpeech'])
    for definition in meaning['definitions']:
        print(definition['definition'])
        if definition['example']:
            print('"'+ definition['example'] + '"')
        if definition['synonyms']:
            print('Similar: ', "    ".join(definition['synonyms']))
        if definition['antonyms']:
            print('Opposite: ', "    ".join(definition['antonyms']))
        print()
    print()

print(api_json["origin"])
print()