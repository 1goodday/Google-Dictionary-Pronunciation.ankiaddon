from aqt import *
from PyQt5 import QtWidgets

def t1():
    print('hi')
    return

app = QtWidgets.QApplication(sys.argv)

a = QWidget()
a.resize(600,300)
# b = QWidget()
# b.resize(60,30)

hbox = QHBoxLayout()
btn = QPushButton("Click me")
# btn.setEnabled(True)
btn.clicked.connect(t1)
hbox.addWidget(btn)
hbox.addStretch(3)
a.setLayout(hbox)
a.move(200, 200)
a.setWindowTitle("God")
print(hbox.parentWidget() == a)
# mw.mya = a
a.show()
# btn.show()

sys.exit(app.exec_())