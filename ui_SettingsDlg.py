# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsDlg.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QWidget)

class Ui_SettingsDlg(object):
    def setupUi(self, SettingsDlg):
        if not SettingsDlg.objectName():
            SettingsDlg.setObjectName(u"SettingsDlg")
        SettingsDlg.resize(491, 362)
        font = QFont()
        font.setPointSize(13)
        SettingsDlg.setFont(font)
        self.text1 = QPlainTextEdit(SettingsDlg)
        self.text1.setObjectName(u"text1")
        self.text1.setGeometry(QRect(275, 15, 211, 336))
        self.text1.setFont(font)
        self.layoutWidget = QWidget(SettingsDlg)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 310, 256, 42))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.calcButton = QPushButton(self.layoutWidget)
        self.calcButton.setObjectName(u"calcButton")
        self.calcButton.setFont(font)

        self.horizontalLayout.addWidget(self.calcButton)

        self.openFolderButton = QPushButton(self.layoutWidget)
        self.openFolderButton.setObjectName(u"openFolderButton")
        self.openFolderButton.setMaximumSize(QSize(50, 16777215))
        self.openFolderButton.setFont(font)
        icon = QIcon()
        icon.addFile(u"res/folder_blue.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.openFolderButton.setIcon(icon)
        self.openFolderButton.setIconSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.openFolderButton)

        self.bPlyMake = QCheckBox(SettingsDlg)
        self.bPlyMake.setObjectName(u"bPlyMake")
        self.bPlyMake.setGeometry(QRect(12, 273, 231, 26))
        self.bPlyMake.setChecked(True)
        self.label_6 = QLabel(SettingsDlg)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(12, 186, 136, 22))
        self.fov_x = QLineEdit(SettingsDlg)
        self.fov_x.setObjectName(u"fov_x")
        self.fov_x.setGeometry(QRect(183, 84, 88, 28))
        self.fov_x.setFont(font)
        self.label = QLabel(SettingsDlg)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(12, 16, 50, 22))
        self.label.setFont(font)
        self.metric_scale_mnoj = QLineEdit(SettingsDlg)
        self.metric_scale_mnoj.setObjectName(u"metric_scale_mnoj")
        self.metric_scale_mnoj.setGeometry(QRect(183, 152, 88, 28))
        self.mesh_dense = QLineEdit(SettingsDlg)
        self.mesh_dense.setObjectName(u"mesh_dense")
        self.mesh_dense.setGeometry(QRect(183, 186, 88, 28))
        self.max_depth_m = QLineEdit(SettingsDlg)
        self.max_depth_m.setObjectName(u"max_depth_m")
        self.max_depth_m.setGeometry(QRect(183, 118, 88, 28))
        self.max_depth_m.setFont(font)
        self.label_2 = QLabel(SettingsDlg)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(12, 84, 104, 22))
        self.label_2.setFont(font)
        self.label_2.setTextFormat(Qt.TextFormat.PlainText)
        self.qualityComboBox = QComboBox(SettingsDlg)
        self.qualityComboBox.setObjectName(u"qualityComboBox")
        self.qualityComboBox.setGeometry(QRect(183, 50, 83, 28))
        self.qualityComboBox.setFont(font)
        self.label_5 = QLabel(SettingsDlg)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(12, 152, 39, 22))
        self.label_4 = QLabel(SettingsDlg)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(12, 50, 54, 22))
        self.label_4.setFont(font)
        self.label_3 = QLabel(SettingsDlg)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(12, 118, 108, 22))
        self.label_3.setFont(font)
        self.gpuComboBox = QComboBox(SettingsDlg)
        self.gpuComboBox.setObjectName(u"gpuComboBox")
        self.gpuComboBox.setGeometry(QRect(183, 16, 83, 28))
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(False)
        self.gpuComboBox.setFont(font1)
        self.label_dimension = QLabel(SettingsDlg)
        self.label_dimension.setObjectName(u"label_dimension")
        self.label_dimension.setGeometry(QRect(13, 221, 104, 45))
        self.label_dimension.setMaximumSize(QSize(16777215, 45))
        self.dimenScale = QLineEdit(SettingsDlg)
        self.dimenScale.setObjectName(u"dimenScale")
        self.dimenScale.setGeometry(QRect(123, 229, 147, 28))

        self.retranslateUi(SettingsDlg)

        QMetaObject.connectSlotsByName(SettingsDlg)
    # setupUi

    def retranslateUi(self, SettingsDlg):
        SettingsDlg.setWindowTitle(QCoreApplication.translate("SettingsDlg", u"Calculate depth map", None))
        self.calcButton.setText(QCoreApplication.translate("SettingsDlg", u"Calculate", None))
        self.openFolderButton.setText("")
        self.bPlyMake.setText(QCoreApplication.translate("SettingsDlg", u"make 3D ply (more time)", None))
        self.label_6.setText(QCoreApplication.translate("SettingsDlg", u"Mesh filter (0-1)", None))
        self.fov_x.setText(QCoreApplication.translate("SettingsDlg", u"None", None))
        self.label.setText(QCoreApplication.translate("SettingsDlg", u"Device", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDlg", u"Focus_X, grad", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDlg", u"Scale", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDlg", u"Quality", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDlg", u"Depth max, m", None))
        self.label_dimension.setText(QCoreApplication.translate("SettingsDlg", u"Adjast \n"
"dimension     ", None))
    # retranslateUi

