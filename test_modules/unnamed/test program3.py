import re
class re_patterns:
    def __init__(self, word):
        self.word = word
        self.US_mp3_filename_pattern = f"{word}([a-zA-Z0-9._-]*)[_-]us[_-]([a-zA-Z0-9._-]*)\.mp3"
        self.GB_mp3_filename_pattern = f"{word}([a-zA-Z0-9._-]*)[_-]gb[_-]([a-zA-Z0-9._-]*)\.mp3"
        self.mp3_filename_pattern = f"{word}([a-zA-Z0-9._-]*)[_-](us|gb)[_-]([a-zA-Z0-9._-]*)\.mp3"

url = "//ssl.gstatic.com/dictionary/static/sounds/20200429/inside--_us_2.mp3"

word = 'inside'
mp3_url_gb = re.sub(re_patterns(word).mp3_filename_pattern, re_patterns(word).GB_mp3_filename_pattern, url)
# s = re_patterns('ali').global_US_mp3_filename_pattern
print(mp3_url_gb)