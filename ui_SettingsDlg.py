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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_SettingsDlg(object):
    def setupUi(self, SettingsDlg):
        if not SettingsDlg.objectName():
            SettingsDlg.setObjectName(u"SettingsDlg")
        SettingsDlg.resize(245, 173)
        self.calcButton = QPushButton(SettingsDlg)
        self.calcButton.setObjectName(u"calcButton")
        self.calcButton.setGeometry(QRect(65, 110, 75, 24))
        self.widget = QWidget(SettingsDlg)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(15, 10, 216, 64))
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(13)
        self.label.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.gpuComboBox = QComboBox(self.widget)
        self.gpuComboBox.setObjectName(u"gpuComboBox")
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(False)
        self.gpuComboBox.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.gpuComboBox)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setTextFormat(Qt.TextFormat.PlainText)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.fov_x = QLineEdit(self.widget)
        self.fov_x.setObjectName(u"fov_x")
        self.fov_x.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.fov_x)


        self.retranslateUi(SettingsDlg)

        QMetaObject.connectSlotsByName(SettingsDlg)
    # setupUi

    def retranslateUi(self, SettingsDlg):
        SettingsDlg.setWindowTitle(QCoreApplication.translate("SettingsDlg", u"Calculate depth map", None))
        self.calcButton.setText(QCoreApplication.translate("SettingsDlg", u"Calculate", None))
        self.label.setText(QCoreApplication.translate("SettingsDlg", u"Device", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDlg", u"Focus_X, grad", None))
        self.fov_x.setText(QCoreApplication.translate("SettingsDlg", u"None", None))
    # retranslateUi

