import re
Field0 = ' baby&nbsp;&nbsp;&nbsp; [sound:baby_en_us_1.mp3]&nbsp; [sound:baby_en_gb_1.mp3]&nbsp; &nbsp;'
print("Fileds0 is: " + Field0)
separator_pattern = re.compile('[\[\]\s]|&nbsp;|sound:')
word_and_av_filenames = re.split(separator_pattern, Field0)
print("word_and_av_filenames after split is: " + str(word_and_av_filenames))
word_and_av_filenames = list(filter(None, word_and_av_filenames))
print("word_and_av_filenames after space removal: " + str(word_and_av_filenames))

word = word_and_av_filenames[0].lower()
print("word after cleanup is: " + word)

av_filenames = word_and_av_filenames[1:]
print("av_filenames is: " + str(av_filenames))