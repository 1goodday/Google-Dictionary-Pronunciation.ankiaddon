from bs4 import BeautifulSoup as Soup
import os

f = open(os.path.join(os.path.dirname(__file__), "web",
                          "templ-orig.html"))
    
html = f.read()
soup = Soup(html, "html.parser")

svg_tags = soup.find_all('svg')
print("Length = ", len(svg_tags))


i=0
for svg_tag in svg_tags:
    i += 1
    style = soup.new_tag('style')
    style.string = ".small { font: bold 15px arial; }"
    svg_tag.insert(1,style)

    text = soup.new_tag('text')
    text.string = "AE"
    text['x'] = "50%"
    text['y'] = "50%"
    text['alignment-baseline'] = "middle"
    text['text-anchor'] = "middle"
    text['class'] = "small"
    svg_tag.circle.insert_after(text)
    

print("i = ", i)
print(soup.prettify())