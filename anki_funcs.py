# Functions interacting with Anki and its display.


import os
from . import settings, scrape
from aqt import mw
from anki.cards import Card
import re
import requests
from bs4 import BeautifulSoup
import aqt.utils
from typing import Any, List
from aqt import editor, webview


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
    if settings.add_GB_pronunciation_flag and (not(GB_pronunciation_exists) or settings.keep_duplicates_flag):
        try_adding_GB_pronunciation = True
    if settings.add_US_pronunciation_flag and (not(US_pronunciation_exists) or settings.keep_duplicates_flag):
        try_adding_US_pronunciation = True

    if settings.US_first:
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


def add_pronunciation_button(buttons, editor: editor.Editor):
    '''
    Adds a new button to the editor.
    By clicking this button, _add_pronunciation_mp3s is triggered
    and pronunciations are added to the entry.
    '''
    editor._links['click_button'] = _add_pronunciation_mp3s
    return buttons + [editor._addButton(
        icon=os.path.join(os.path.dirname(__file__), 'images',
                          'sil.svg'),
        cmd='click_button',
        tip='Add Google Pronunciation')]


def new_play_button_css(web_content: webview.WebContent, context: Any) -> None:
    '''
    Appends a css to modify the shape of an existing button
    or define the shape of a new audio play buttons

    In our case, only a text element is added to the
    Anki defined "replay-button svg" by "add_label_to_button.css" file.
    '''

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


def add_button_labels(text: str, card: Card, kind: str) -> BeautifulSoup.prettify:
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
