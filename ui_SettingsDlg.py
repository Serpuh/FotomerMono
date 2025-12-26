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
    QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_SettingsDlg(object):
    def setupUi(self, SettingsDlg):
        if not SettingsDlg.objectName():
            SettingsDlg.setObjectName(u"SettingsDlg")
        SettingsDlg.resize(403, 243)
        font = QFont()
        font.setPointSize(13)
        SettingsDlg.setFont(font)
        self.text1 = QPlainTextEdit(SettingsDlg)
        self.text1.setObjectName(u"text1")
        self.text1.setGeometry(QRect(225, 15, 171, 216))
        self.text1.setFont(font)
        self.widget = QWidget(SettingsDlg)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(12, 13, 206, 166))
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.gpuComboBox = QComboBox(self.widget)
        self.gpuComboBox.setObjectName(u"gpuComboBox")
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(False)
        self.gpuComboBox.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.gpuComboBox)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.qualityComboBox = QComboBox(self.widget)
        self.qualityComboBox.setObjectName(u"qualityComboBox")
        self.qualityComboBox.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.qualityComboBox)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setTextFormat(Qt.TextFormat.PlainText)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.fov_x = QLineEdit(self.widget)
        self.fov_x.setObjectName(u"fov_x")
        self.fov_x.setFont(font)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.fov_x)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.max_depth_m = QLineEdit(self.widget)
        self.max_depth_m.setObjectName(u"max_depth_m")
        self.max_depth_m.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.max_depth_m)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.metric_scale_mnoj = QLineEdit(self.widget)
        self.metric_scale_mnoj.setObjectName(u"metric_scale_mnoj")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.metric_scale_mnoj)

        self.widget1 = QWidget(SettingsDlg)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(10, 190, 211, 42))
        self.horizontalLayout = QHBoxLayout(self.widget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.calcButton = QPushButton(self.widget1)
        self.calcButton.setObjectName(u"calcButton")
        self.calcButton.setFont(font)

        self.horizontalLayout.addWidget(self.calcButton)

        self.openFolderButton = QPushButton(self.widget1)
        self.openFolderButton.setObjectName(u"openFolderButton")
        self.openFolderButton.setMaximumSize(QSize(50, 16777215))
        self.openFolderButton.setFont(font)
        icon = QIcon()
        icon.addFile(u"res/folder_blue.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.openFolderButton.setIcon(icon)
        self.openFolderButton.setIconSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.openFolderButton)


        self.retranslateUi(SettingsDlg)

        QMetaObject.connectSlotsByName(SettingsDlg)
    # setupUi

    def retranslateUi(self, SettingsDlg):
        SettingsDlg.setWindowTitle(QCoreApplication.translate("SettingsDlg", u"Calculate depth map", None))
        self.label.setText(QCoreApplication.translate("SettingsDlg", u"Device", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDlg", u"Quality", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDlg", u"Focus_X, grad", None))
        self.fov_x.setText(QCoreApplication.translate("SettingsDlg", u"None", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDlg", u"Depth max, m", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDlg", u"Scale", None))
        self.calcButton.setText(QCoreApplication.translate("SettingsDlg", u"Calculate", None))
        self.openFolderButton.setText("")
    # retranslateUi

