# Functions interacting with Anki and its display.


from . import settings, scrape
from aqt import mw
from anki.cards import Card
import re
import requests
from bs4 import BeautifulSoup
import aqt.utils
from typing import Any, List
from aqt import editor, webview
import sys
import os

# Add external_libs directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
external_libs_dir = os.path.join(parent_dir, 'external_libs')
sys.path.append(external_libs_dir)
from googletrans import Translator


def _get_word_from_editor(editor: editor.Editor) -> str:
    '''Extracts and cleans the word (the question) from editor.'''
    _field0 = str(editor.note.fields[0]).replace('&nbsp;', ' ')
    _word_and_av_filenames = re.split('[\[\]]|sound:', _field0)

    # Removing blank list items
    _word_and_av_filenames = list(filter(None, _word_and_av_filenames))

    word = _word_and_av_filenames[0].strip().lower()

    # Replacing multi-space with single-space in multi-word terms
    word = re.sub('\s+', ' ', word)

    # For debugging
    # aqt.utils.showText("editor.note.fields[0]:\n" + editor.note.fields[0] + "\n\n_field0:\n" +
    #                    _field0 + "\n\n_word_and_av_filenames:\n" + str(_word_and_av_filenames) + "\n\nword:\n" + word)

    return word


def _get_av_filenames_from_editor(editor: editor.Editor) -> List[str]:
    '''Extracts and cleans the audio/video filenames from editor.'''
    _field0 = str(editor.note.fields[0]).replace('&nbsp;', ' ')
    _word_and_av_filenames = re.split('[\[\]]|sound:', _field0)

    # Removing blank list items
    _word_and_av_filenames = list(filter(None, _word_and_av_filenames))

    av_filenames = _word_and_av_filenames[1:]

    # For debugging
    # aqt.utils.showText("editor.note.fields[0]:\n" + editor.note.fields[0] + "\n\n_field0:\n" +
    #                    _field0 + "\n\n_word_and_av_filenames:\n" + str(_word_and_av_filenames) + "\n\nav_filenames:\n" + str(av_filenames))

    return av_filenames


def _add_pronunciation_mp3s(editor: editor.Editor) -> None:
    '''
    Finds and adds US and/or GB pronunciations after clicking the add-on
    button.

    Arguments:
        editor: Passed to the function by Anki.

    Returns:
        None. If successful, adds the [sound:filename.mp3] tags to the entries
        and the related audio files in the collection.media folder (in a typical
        Windows installation in:
        C:\_Users\_your_name\AppData\Roaming\Anki2\_your_name\collection.media').
        If unsuccessful, quits without any change.
    '''

    # Main function of the add-on, works in sequence as:
    # 1- Gets the word from the editor.
    #
    # 2- Searches Google for pronunciation
    #
    # 3- If one pronunciation is found (usually the US is found first), it makes
    #    the other (usually GB) url by replacing "us" with "gb" in the url
    #    filename part (or vice versa if GB is found first).
    #
    # 4- Checks the existing audio/video filenames in the editor to find whether
    #    pronunciation files are already there.
    #
    # 5- Tries to add the US and/or GB pronunciations based on config file flag
    #    values.

    # 1
    word = _get_word_from_editor(editor)

    # 2
    if len(scrape.search_google(word)) == 0:
        return

    # Only the first url is used.
    # The rest (if any) are reserved for possible future use.
    (mp3_url, mp3_filename) = scrape.search_google(word)[0]

    # Some "hyphenated compound words" like "add-on" appear with underscore
    # in the mp3 filename and mp3 url, but should be searched with hyphen.
    # This change is to address this special case.
    _word_hyphen_to_underscore = re.sub('-', '_', word)

    # 3
    if re.match(settings.patterns(_word_hyphen_to_underscore).GB_mp3_filename_pattern, mp3_filename):
        mp3_url_gb = mp3_url
        us_or_gb_sub_string = re.search('[_-]gb[_-]', mp3_filename).group(0)
        mp3_url_us = re.sub(
            '[_-]gb[_-]', us_or_gb_sub_string.replace('gb', 'us'), mp3_url)
    elif re.match(settings.patterns(_word_hyphen_to_underscore).US_mp3_filename_pattern, mp3_filename):
        mp3_url_us = mp3_url
        us_or_gb_sub_string = re.search('[_-]us[_-]', mp3_filename).group(0)
        mp3_url_gb = re.sub(
            '[_-]us[_-]', us_or_gb_sub_string.replace('us', 'gb'), mp3_url)

    # 4
    GB_pronunciation_exists = US_pronunciation_exists = False
    av_filenames = _get_av_filenames_from_editor(editor)
    for av_filename in av_filenames:
        if re.match(settings.patterns(_word_hyphen_to_underscore).GB_mp3_filename_pattern, av_filename):
            GB_pronunciation_exists = True
        if re.match(settings.patterns(_word_hyphen_to_underscore).US_mp3_filename_pattern, av_filename):
            US_pronunciation_exists = True

    # 5
    try_adding_GB_pronunciation = try_adding_US_pronunciation = False
    if settings.config_values().add_GB_pronunciation and (not(GB_pronunciation_exists) or settings.config_values().keep_pronunciation_duplicates):
        try_adding_GB_pronunciation = True
    if settings.config_values().add_US_pronunciation and (not(US_pronunciation_exists) or settings.config_values().keep_pronunciation_duplicates):
        try_adding_US_pronunciation = True

    if settings.config_values().US_pronunciation_first:
        if (requests.get(mp3_url_us).status_code == 200) and try_adding_US_pronunciation:
            file_path_us = editor.urlToFile(mp3_url_us)
            editor.addMedia(file_path_us)

        if (requests.get(mp3_url_gb).status_code == 200) and try_adding_GB_pronunciation:
            file_path_gb = editor.urlToFile(mp3_url_gb)
            editor.addMedia(file_path_gb)

    else:
        if (requests.get(mp3_url_gb).status_code == 200) and try_adding_GB_pronunciation:
            file_path_gb = editor.urlToFile(mp3_url_gb)
            editor.addMedia(file_path_gb)

        if (requests.get(mp3_url_us).status_code == 200) and try_adding_US_pronunciation:
            file_path_us = editor.urlToFile(mp3_url_us)
            editor.addMedia(file_path_us)


def _add_1st_meaning(editor: editor.Editor) -> None:
    '''Adds only the first meaning given by api.dictionaryapi.dev to the
    editor "Back" box.'''
    # Same as _add_all_meanings, just breaking the loop after the first definition.

    word = _get_word_from_editor(editor)

    # Gets the word from api.dictionaryapi.dev (than returns a list of length 1).
    try:
        api_json = requests.get(
            "https://api.dictionaryapi.dev/api/v2/entries/en/" + word).json()[0]
    except:
        return

    # _answer will be constructed and used to fill the "Back" box.
    _answer: str = ''

    try:
        if settings.config_values().add_phonetics_with_1st_meaning:
            _answer += (api_json["phonetic"] + '<br><br>')
    except:
        pass

    # Loop to add all the meanings, plus formatting.
    for meaning in api_json['meanings']:
        try:
            _answer += ('<b>' + meaning['partOfSpeech'] + '</b>' + '<br>')
        except:
            pass

        for definition in meaning['definitions']:
            try:
                _answer += (definition['definition'] + '<br>')
            except:
                pass

            try:
                if definition['example']:
                    _answer += ('<font color="grey">' + '"' +
                                definition['example'] + '"' + '</font>' + '<br>')
            except:
                pass

            try:
                if definition['synonyms']:
                    _answer += ('Similar: ' + '<font color="grey">' +
                                ", ".join(definition['synonyms']) + '</font>' + '<br>')
            except:
                pass

            try:
                if definition['antonyms']:
                    _answer += ('Opposite: ' + '<font color="grey">' +
                                ", ".join(definition['antonyms']) + '</font>' + '<br>')
            except:
                pass

            break
        break

    # Removes any of the line breaks added in the above loop at the beginning
    # or end of _answer.
    # Can be replaced by removesuffix and removeprefix in the later Anki versions
    # for better readability.
    while _answer[:4] == '<br>':
        _answer = _answer[4:]

    while _answer[-4:] == '<br>':
        _answer = _answer[:-4]

    # If overwrite is disabled, separates the new and old contents with a dashed line.
    if settings.config_values().overwrite_meaning or not(editor.note.fields[1]):
        editor.note.fields[1] = _answer
    else:
        editor.note.fields[1] += (
            '<br><br>' + '-------------------------------------------' + '<br><br>' + _answer)

    # For debugging
    # aqt.utils.showText(str(editor.note.fields[1]))

    # Applies the new content.
    editor.loadNote()

    return


def _add_all_meanings(editor: editor.Editor) -> None:
    '''Adds all meanings given by api.dictionaryapi.dev to the editor "Back" box.'''

    word = _get_word_from_editor(editor)

    # Gets the word from api.dictionaryapi.dev (than returns a list of length 1).
    try:
        api_json = requests.get(
            "https://api.dictionaryapi.dev/api/v2/entries/en/" + word).json()[0]
    except:
        return

    # _answer will be constructed and used to fill the "Back" box.
    _answer: str = ''

    try:
        if settings.config_values().add_phonetics_with_1st_meaning:
            _answer += (api_json["phonetic"] + '<br><br>')
    except:
        pass

    # Loop to add all the meanings, plus formatting.
    for meaning in api_json['meanings']:
        try:
            _answer += ('<b>' + meaning['partOfSpeech'] + '</b>' + '<br>')
        except:
            pass

        for definition in meaning['definitions']:
            try:
                _answer += (definition['definition'] + '<br>')
            except:
                pass

            try:
                if definition['example']:
                    _answer += ('<font color="grey">' + '"' +
                                definition['example'] + '"' + '</font>' + '<br>')
            except:
                pass

            try:
                if definition['synonyms']:
                    _answer += ('Similar: ' + '<font color="grey">' +
                                ", ".join(definition['synonyms']) + '</font>' + '<br>')
            except:
                pass

            try:
                if definition['antonyms']:
                    _answer += ('Opposite: ' + '<font color="grey">' +
                                ", ".join(definition['antonyms']) + '</font>' + '<br>')
            except:
                pass

            _answer += '<br>'
        _answer += '<br>'

    # Removes any of the line breaks added in the above loop at the beginning
    # or end of _answer.
    # Can be replaced by removesuffix and removeprefix in the later Anki versions
    # for better readability.
    while _answer[:4] == '<br>':
        _answer = _answer[4:]

    while _answer[-4:] == '<br>':
        _answer = _answer[:-4]

    # If overwrite is disabled, separates the new and old contents with a dashed line.
    if settings.config_values().overwrite_meaning or not(editor.note.fields[1]):
        editor.note.fields[1] = _answer
    else:
        editor.note.fields[1] += (
            '<br><br>' + '-------------------------------------------' + '<br><br>' + _answer)

    # For debugging
    # aqt.utils.showText(str(editor.note.fields[1]))

    # Applies the new content.
    editor.loadNote()

    return


def _add_translation(editor: editor.Editor) -> None:
    '''Adds translation given by googletrans (https://pypi.org/project/googletrans/)
    to the editor "Back" box.'''

    word = _get_word_from_editor(editor)
    # Initiating Translator
    _translator = Translator(
        user_agent=settings.config_values().mybrowser_headers['User-Agent'])

    # Gets the translation
    try:
        _translated = _translator.translate(
            word, src='en', dest=settings.config_values().translation_target_language)
    except:
        return

    # _answer will be constructed and used to fill the "Back" box.
    _answer: str = ''

    try:
        _answer += (settings.iso_639_1_codes_dict[settings.config_values().translation_target_language] +
                    ' translation: ' + _translated.text)
    except:
        pass

    try:
        if settings.config_values().add_transliteration:
            _answer += ('<font color="grey" >' + ' (' +
                        _translated.pronunciation + ')' + '</font>')
    except:
        pass

    # If overwrite is disabled, separates the new and old contents with a dashed line.
    if settings.config_values().overwrite_translation or not(editor.note.fields[1]):
        editor.note.fields[1] = _answer
    else:
        editor.note.fields[1] += (
            '<br><br>' + '-------------------------------------------' + '<br><br>' + _answer)

    # For debugging
    # aqt.utils.showText(str(editor.note.fields[1]))

    # Applies the new content.
    editor.loadNote()

    return


def add_buttons(buttons, editor: editor.Editor) -> List[str]:
    '''
    Adds three new buttons to the editor.
    By clicking the respective button one of below happens:
    1- _add_pronunciation_mp3s is triggered and pronunciations will be added to the entry.
    2- _add_1st_meaning is triggered and only the first meaning will be added to the entry.
    3- _add_all_meanings is triggered and all meanings will be added to the entry.
    4- _add_translation is triggered and translation in the specified target language
       will be added to the entry.
    '''
    editor._links['click_pronunciation_button'] = _add_pronunciation_mp3s
    editor._links['click_1st_meaning_button'] = _add_1st_meaning
    editor._links['click_all_meanings_button'] = _add_all_meanings
    editor._links['click_translation_button'] = _add_translation
    _buttons = buttons

    if settings.config_values().display_add_pronunciation_button:
        _buttons += [editor._addButton(icon=os.path.join(os.path.dirname(__file__), 'images',
                                       'sil.svg'), cmd='click_pronunciation_button', tip='Add Pronunciation')]
    if settings.config_values().display_add_1st_meaning_button:
        _buttons += [editor._addButton(icon=os.path.join(os.path.dirname(
            __file__), 'images', '1st.svg'), cmd='click_1st_meaning_button', tip='Add 1st Meaning')]
    if settings.config_values().display_add_all_meanings_button:
        _buttons += [editor._addButton(icon=os.path.join(os.path.dirname(
            __file__), 'images', 'All.svg'), cmd='click_all_meanings_button', tip='Add All Meanings')]
    if settings.config_values().display_add_translation_button:
        _buttons += [editor._addButton(icon=os.path.join(os.path.dirname(
            __file__), 'images', 'T.svg'), cmd='click_translation_button', tip='Add Translation')]

    return _buttons


def new_play_button_css(web_content: webview.WebContent, context: Any) -> None:
    '''
    Appends a css to modify the shape of an existing button
    or define the shape of a new audio play button

    In our case, only a text element is added to the
    Anki defined "replay-button svg" by "add_label_to_button.css" file.
    '''

    if not(settings.config_values().add_play_button_labels):
        return

    # Below codes/explanations belong to Anki "webview_will_set_content" hook in genhooks_gui.py
    # that are kept for possible future use.

    # if not isinstance(context, aqt.reviewer.Reviewer):
    #     # not reviewer, do not modify content
    #     return

    # reviewer, perform changes to content

    # context: aqt.reviewer.Reviewer
    # mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.css.append(
        f'/_addons/{addon_package}/web/add_label_to_button.css')

    # web_content.js.append(
    # f"/_addons/{addon_package}/web/my-addon.js")

    # web_content.head += "<script>console.log('my-addon')</script>"
    # web_content.body += "<div id='my-addon'></div>"


def add_play_button_labels(text: str, card: Card, kind: str) -> BeautifulSoup.prettify:
    '''
    Adds US/GB labels to the respective pronunciation play buttons.
    This function is used by the card_will_show hook in the __init__.py
    to modify the card appearance before display.

    Arguments:
    text: The window html, passed to the function by Anki.
    card: The card, passed to the function by Anki.
    kind: The window kind, passed to the function by Anki.
    Values 'reviewQuestion', 'reviewAnswer', 'previewQuestion',
    'previewAnswer' are considered to be processed by this function.

    Returns:
    The original or modified text (html input), decided based on kind value
    and audio/video filenames in the card.
    '''

    if not(settings.config_values().add_play_button_labels):
        return

    # Function works in below steps:
    # 1- Checks the kind, it should be in either reviewer or previewer
    #    question or answer.
    #
    # 2- Extracts the word and audio/video filenames from the card.
    #
    # 3- Considers "US", "GB" or "none" labels to each audio/video file.
    #    Purpose of this step is to distinguish between the audio/video
    #    files added by this add-on (labeled "US" or "GB") and other
    #    possible existing ones (labeled "none").
    #
    # 4- Adds the label text and format of the new buttons.

    # For debugging
    # aqt.utils.showText("text\n" + text + "\n\ncard\n" +
    #                    str(card) + "\n\nkind\n" + kind)

    # 1
    if kind not in ('reviewQuestion', 'reviewAnswer', 'previewQuestion', 'previewAnswer'):
        return text

    # 2
    q_text = (card.render_output().question_text).replace('&nbsp;', ' ')
    word = (re.split('[\[\]]', q_text))[0].strip().lower()
    word = re.sub('\s+', ' ', word)

    # Some "hyphenated compound words" like "add-on" appear with underscore
    # in the mp3 filename and mp3 url, but should be searched with hyphen.
    # This change is to address this special case.
    word = re.sub('-', '_', word)

    av_filenames = [av_tags.filename for av_tags in card.question_av_tags()]

    # For debugging
    # aqt.utils.showText("word\n" + word +
    #                    "\n\nav_filenames\n" + str(av_filenames))

    # 3
    labels = []
    for av_filename in av_filenames:
        if re.match(settings.patterns(word).US_mp3_filename_pattern, av_filename):
            labels.append('US')
        elif re.match(settings.patterns(word).mp3_filename_pattern, av_filename):
            labels.append('GB')
        else:
            labels.append('none')

    # For debugging
    # aqt.utils.showText("av_filenames\n" +
    #                    str(av_filenames) + "\n\nlabels\n" + str(labels))

    # 4
    text_soup = BeautifulSoup(text, 'html.parser')
    svg_tags = text_soup.find_all('svg')

    for (svg_tag, label) in zip(svg_tags, labels):
        if label != 'none':
            # The next line of code is needed only if a new button is going to
            # be defined from scratch by a css.
            #
            # "replay-button-new" should be defined similar to "replay-button"
            # in the original Anki reviewer.css file.
            #
            # In this add-on the css (add_label_to_button.css) only adds the
            # text color (white) to the Anki default button ("replay-button").

            # svg_tag.parent['class'] = 'replay-button-new soundLink'

            style = text_soup.new_tag('style')
            style.string = '.button_font { font: 75% arial; }'
            svg_tag.insert(1, style)

            text_tag = text_soup.new_tag('text')
            text_tag.string = label
            text_tag['x'] = '50%'
            text_tag['y'] = '50%'
            text_tag['alignment-baseline'] = 'middle'
            text_tag['text-anchor'] = 'middle'
            text_tag['class'] = 'button_font'
            svg_tag.path.insert_after(text_tag)

    # For debugging
    # aqt.utils.showText("original text:\n" + BeautifulSoup(text, 'html.parser').prettify() +
    #                    "\n\n\nmodified text:\n" + text_soup.prettify() + "\n\nkind is:\n" + kind)

    return text_soup.prettify()
