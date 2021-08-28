# Reads the user config file (config.json), generates patterns for
# text search and defines the constants used in other modules.

from aqt import mw

# Redaing the user settings in config.json
config = mw.addonManager.getConfig(__name__)
mybrowser_headers = {
    'User-Agent': config['01-User-Agent']}
add_US_pronunciation = (
    config['05-Add US pronunciation?'][0].lower() == 'y')
add_GB_pronunciation = (
    config['06-Add GB pronunciation?'][0].lower() == 'y')
US_pronunciation_first = (
    config['07-US or GB pronunciation first?'][0].lower() == 'u')
keep_pronunciation_duplicates = (
    config['08-Keep pronunciation duplicates?'][0].lower() == 'y')
add_play_button_labels = (
    config['09-Add labels to play buttons?'][0].lower() == 'y')
display_add_pronunciation_button = (
    config['02-Display \'Add Pronunciation\' button?'][0].lower() == 'y')
display_add_1st_meaning_button = (
    config['03-Display \'Add 1st Meaning\' button?'][0].lower() == 'y')
display_add_all_meanings_button = (
    config['04-Display \'Add All Meanings\' button?'][0].lower() == 'y')
add_phonetics_with_1st_meaning = (
    config['10-Add phonetics with the 1st meaning?'][0].lower() == 'y')
add_phonetics_with_all_meanings = (
    config['11-Add phonetics with all meanings?'][0].lower() == 'y')
overwrite_meaning = (
    config['12-Overwrite meaning?'][0].lower() == 'y')


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
