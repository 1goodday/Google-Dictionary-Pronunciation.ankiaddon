# Reads the user config file (config.json), generates patterns for
# text search and defines the constants used in other modules.

from aqt import mw

# Redaing the user settings in config.json
config = mw.addonManager.getConfig(__name__)
mybrowser_headers = {
    'User-Agent': config['User-Agent']}
add_US_pronunciation_flag = (
    config['Add US pronunciation?'][0].lower() == 'y')
add_GB_pronunciation_flag = (
    config['Add GB pronunciation?'][0].lower() == 'y')
US_first = (
    config['US or GB first?'][0].lower() == 'u')
keep_duplicates_flag = (
    config['Keep duplicates?'][0].lower() == 'y')
add_play_button_labels = (
    config['Add labels to play buttons?'][0].lower() == 'y')


class patterns:
    '''Generates regex or search patterns, accepting "word" as class argument.'''

    def __init__(self, word: str):
        self.word = word
        self.US_mp3_filename_pattern = f'{word}([a-zA-Z0-9._-]*)[_-]us[_-]([a-zA-Z0-9._-]*)\.mp3'
        self.GB_mp3_filename_pattern = f'{word}([a-zA-Z0-9._-]*)[_-]gb[_-]([a-zA-Z0-9._-]*)\.mp3'
        self.mp3_filename_pattern = f'{word}([a-zA-Z0-9._-]*)[_-](us|gb)[_-]([a-zA-Z0-9._-]*)\.mp3'
        self.google_pronounce_search_url = f'https://www.google.com/search?q=how+to+pronounce+{word}'
        self.google_define_search_url = f'https://www.google.com/search?q=define:{word}'


# Constant definitions
MP3_URL_BEGIN_STR = '//ssl.gstatic.com/dictionary/static/'
MP3_URL_END_STR = '.mp3'
