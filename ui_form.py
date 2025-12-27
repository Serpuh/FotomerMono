# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QHBoxLayout, QMainWindow,
    QMenuBar, QSizePolicy, QStatusBar, QToolBar,
    QWidget)

from camview import CamView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1022, 647)
        self.actionLoadImage = QAction(MainWindow)
        self.actionLoadImage.setObjectName(u"actionLoadImage")
        icon = QIcon()
        icon.addFile(u"res/picture.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLoadImage.setIcon(icon)
        self.actionLoadImage.setMenuRole(QAction.MenuRole.NoRole)
        self.actionCalc1 = QAction(MainWindow)
        self.actionCalc1.setObjectName(u"actionCalc1")
        self.actionCalc1.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gView1 = CamView(self.centralwidget)
        self.gView1.setObjectName(u"gView1")
        self.gView1.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.gView1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.gView1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.gView1.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.horizontalLayout.addWidget(self.gView1)

        self.gView2 = CamView(self.centralwidget)
        self.gView2.setObjectName(u"gView2")
        self.gView2.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.gView2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.gView2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.gView2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.horizontalLayout.addWidget(self.gView2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1022, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setMinimumSize(QSize(0, 20))
        font = QFont()
        font.setPointSize(13)
        self.statusbar.setFont(font)
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionLoadImage)
        self.toolBar.addAction(self.actionCalc1)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Fotomer Mono", None))
        self.actionLoadImage.setText(QCoreApplication.translate("MainWindow", u"Load image", None))
        self.actionCalc1.setText(QCoreApplication.translate("MainWindow", u"Calculate", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

