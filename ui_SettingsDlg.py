# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsDlg.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QPushButton,
    QSizePolicy, QWidget)

class Ui_SettingsDlg(object):
    def setupUi(self, SettingsDlg):
        if not SettingsDlg.objectName():
            SettingsDlg.setObjectName(u"SettingsDlg")
        SettingsDlg.resize(400, 300)
        self.calcButton = QPushButton(SettingsDlg)
        self.calcButton.setObjectName(u"calcButton")
        self.calcButton.setGeometry(QRect(150, 180, 75, 24))
        self.gpuComboBox = QComboBox(SettingsDlg)
        self.gpuComboBox.setObjectName(u"gpuComboBox")
        self.gpuComboBox.setGeometry(QRect(50, 30, 62, 22))

        self.retranslateUi(SettingsDlg)

        QMetaObject.connectSlotsByName(SettingsDlg)
    # setupUi

    def retranslateUi(self, SettingsDlg):
        SettingsDlg.setWindowTitle(QCoreApplication.translate("SettingsDlg", u"Calculate depth map", None))
        self.calcButton.setText(QCoreApplication.translate("SettingsDlg", u"Calculate", None))
    # retranslateUi

