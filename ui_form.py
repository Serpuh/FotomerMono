# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
        MainWindow.resize(1254, 859)
        icon = QIcon()
        icon.addFile(u"res/App.ico", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        MainWindow.setWindowIcon(icon)
        self.actionLoadImage = QAction(MainWindow)
        self.actionLoadImage.setObjectName(u"actionLoadImage")
        icon1 = QIcon()
        icon1.addFile(u"res/picture.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLoadImage.setIcon(icon1)
        self.actionLoadImage.setMenuRole(QAction.MenuRole.NoRole)
        self.actionCalc1 = QAction(MainWindow)
        self.actionCalc1.setObjectName(u"actionCalc1")
        self.actionCalc1.setMenuRole(QAction.MenuRole.NoRole)
        self.actionDimension = QAction(MainWindow)
        self.actionDimension.setObjectName(u"actionDimension")
        self.actionDimension.setCheckable(True)
        icon2 = QIcon()
        icon2.addFile(u"res/ruler.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDimension.setIcon(icon2)
        self.actionDimension.setMenuRole(QAction.MenuRole.NoRole)
        self.actionOpen_Folder = QAction(MainWindow)
        self.actionOpen_Folder.setObjectName(u"actionOpen_Folder")
        icon3 = QIcon()
        icon3.addFile(u"res/folder_blue.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpen_Folder.setIcon(icon3)
        self.actionOpen_Folder.setMenuRole(QAction.MenuRole.NoRole)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionHelp.setEnabled(True)
        icon4 = QIcon()
        icon4.addFile(u"res/help3.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionHelp.setIcon(icon4)
        self.actionHelp.setMenuRole(QAction.MenuRole.NoRole)
        self.actionPrint = QAction(MainWindow)
        self.actionPrint.setObjectName(u"actionPrint")
        self.actionPrint.setEnabled(True)
        icon5 = QIcon()
        icon5.addFile(u"res/printer_1.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionPrint.setIcon(icon5)
        self.actionPrint.setMenuRole(QAction.MenuRole.NoRole)
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
        self.menubar.setGeometry(QRect(0, 0, 1254, 22))
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
        self.toolBar.addAction(self.actionDimension)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpen_Folder)
        self.toolBar.addAction(self.actionPrint)
        self.toolBar.addAction(self.actionHelp)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Fotomer Mono", None))
        self.actionLoadImage.setText(QCoreApplication.translate("MainWindow", u"Load image", None))
        self.actionCalc1.setText(QCoreApplication.translate("MainWindow", u"Calculate", None))
        self.actionDimension.setText(QCoreApplication.translate("MainWindow", u"Dimension", None))
        self.actionOpen_Folder.setText(QCoreApplication.translate("MainWindow", u"Open Folder", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionPrint.setText(QCoreApplication.translate("MainWindow", u"Print", None))
#if QT_CONFIG(tooltip)
        self.actionPrint.setToolTip(QCoreApplication.translate("MainWindow", u"Print", None))
#endif // QT_CONFIG(tooltip)
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

