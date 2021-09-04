import os
import sys

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)

# Now you can import any library located in the "vendor" folder!
from googletrans import Translator

translator = Translator(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
t = translator.translate('green', src='en', dest='ar')
print(str(t))
print(t.text)
print(t.pronunciation)