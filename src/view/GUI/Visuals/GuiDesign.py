from PyQt5.QtCore import QSize, Qt, QMetaObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpacerItem,
                             QSplitter, QCheckBox)

from src.view.GUI.UserInteraction.TableWidget import TableWidget
import qtawesome as qta


def setupUI(mainWindow, active_mode_queue):
    mainWindow.resize(800, 615)
    sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
    mainWindow.setSizePolicy(sizePolicy)
    mainWindow.centralwidget = QWidget(mainWindow)
    mainWindow.horizontalLayout_4 = QHBoxLayout(mainWindow.centralwidget)
    mainWindow.horizontalLayout_4.setSpacing(5)
    mainWindow.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)

    mainWindow.verticalLayout_4 = QVBoxLayout()
    mainWindow.verticalLayout_4.setSpacing(0)
    mainWindow.verticalLayout_4.setContentsMargins(3, 3, 3, 3)
    mainWindow.horizontalLayout_2 = QHBoxLayout()
    mainWindow.horizontalLayout_2.setSpacing(0)
    mainWindow.verticalLayout_2 = QVBoxLayout()
    mainWindow.verticalLayout_2.setSpacing(10)


    icon_label = QLabel()
    icon_label.setAlignment(Qt.AlignHCenter)

    icon_label.setPixmap(QIcon('src/view/GUI/Images/CTIEngineLogo.png').pixmap(24, 24))
    mainWindow.verticalLayout_2.addWidget(icon_label)



    mainWindow.horizontalLayout_2.addLayout(mainWindow.verticalLayout_2)

    mainWindow.verticalLayout_4.addLayout(mainWindow.horizontalLayout_2)

    mainWindow.verticalSpacer_2 = QSpacerItem(20, 495, QSizePolicy.Minimum, QSizePolicy.Expanding)
    mainWindow.horizontalSpacer_3 = QSpacerItem(300, 20, QSizePolicy.Minimum)

    mainWindow.verticalLayout_4.addItem(mainWindow.verticalSpacer_2)


    mainWindow.sidebar = QWidget(mainWindow.centralwidget)
    mainWindow.sidebar.setMinimumSize(QSize(140, 0))
    mainWindow.sidebar.setMaximumSize(QSize(400, 16777215))
    mainWindow.sidebar.setStyleSheet(u"background-color: rgb(61, 61, 61);")
    mainWindow.verticalLayout_3 = QVBoxLayout(mainWindow.sidebar)
    mainWindow.verticalLayout_3.setSpacing(0)
    mainWindow.verticalLayout_3.setContentsMargins(3, 3, 3, 3)
    mainWindow.horizontalLayout = QHBoxLayout()
    mainWindow.horizontalLayout.setSpacing(0)
    mainWindow.verticalLayout = QVBoxLayout()
    mainWindow.verticalLayout.setSpacing(10)
    mainWindow.label = QLabel(mainWindow.sidebar)

    mainWindow.verticalLayout.addWidget(mainWindow.label)
    icon_label2 = QLabel()
    icon_label2.setAlignment(Qt.AlignHCenter)
    icon_label2.setPixmap(QIcon('src/view/GUI/Images/CTIEngineLogo.png').pixmap(40, 40))
    mainWindow.verticalLayout.addWidget(icon_label2)


    mainWindow.load_button = mainWindow.menu_bar.load_file_button

    mainWindow.verticalLayout.addWidget(mainWindow.load_button)

    mainWindow.cancel_button = mainWindow.menu_bar.cancel_button

    mainWindow.verticalLayout.addWidget(mainWindow.cancel_button)

    mainWindow.pause_button = mainWindow.menu_bar.pause_resume_button

    mainWindow.verticalLayout.addWidget(mainWindow.pause_button)

    mainWindow.project_scroll_button = mainWindow.menu_bar.scroll_button
    mainWindow.scroll_bar = mainWindow.menu_bar.scroll_bar
    mainWindow.verticalLayout.addWidget(mainWindow.project_scroll_button)
    mainWindow.verticalLayout.addWidget(mainWindow.scroll_bar)

    mainWindow.horizontalLayout.addLayout(mainWindow.verticalLayout)

    mainWindow.verticalLayout_3.addLayout(mainWindow.horizontalLayout)

    mainWindow.verticalSpacer = QSpacerItem(20, 700, QSizePolicy.Maximum, QSizePolicy.Expanding)

    mainWindow.verticalLayout_3.addItem(mainWindow.verticalSpacer)

    mainWindow.horizontalLayout_4.addWidget(mainWindow.sidebar, 0, Qt.AlignLeft)

    mainWindow.widget_3 = QWidget(mainWindow.centralwidget)
    mainWindow.verticalLayout_6 = QVBoxLayout(mainWindow.widget_3)
    mainWindow.verticalLayout_6.setSpacing(0)
    mainWindow.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
    mainWindow.upper_bar = QWidget(mainWindow.widget_3)
    mainWindow.upper_bar.setMaximumSize(QSize(1500, 50))
    mainWindow.verticalLayout_5 = QVBoxLayout(mainWindow.upper_bar)
    mainWindow.verticalLayout_5.setSpacing(0)
    mainWindow.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
    mainWindow.horizontalLayout_3 = QHBoxLayout()
    mainWindow.horizontalLayout_3.setSpacing(10)

    mainWindow.menu_button = QPushButton(mainWindow.upper_bar)
    mainWindow.menu_button.setMaximumSize(30, 30)
    mainWindow.menu_button.setCheckable(True)

    mainWindow.horizontalLayout_3.addWidget(mainWindow.menu_button)

    mainWindow.ram_button = mainWindow.metric_bar.ram_button

    mainWindow.horizontalLayout_3.addWidget(mainWindow.ram_button)

    mainWindow.cpu_button = mainWindow.metric_bar.cpu_button

    mainWindow.horizontalLayout_3.addWidget(mainWindow.cpu_button)

    mainWindow.runtime_button = mainWindow.metric_bar.runtime_button

    mainWindow.horizontalLayout_3.addWidget(mainWindow.runtime_button)
    mainWindow.horizontalLayout_3.addWidget(mainWindow.status_bar)
    mainWindow.horizontalLayout_3.addItem(mainWindow.horizontalSpacer_3)

    mainWindow.horizontalLayout_5 = QHBoxLayout()

    mainWindow.select_all_checkbox.setMaximumWidth(80)
    mainWindow.horizontalLayout_5.addWidget(mainWindow.select_all_checkbox)

    mainWindow.horizontalLayout_5.addWidget(mainWindow.upper_limit)
    mainWindow.horizontalLayout_5.addWidget(mainWindow.lower_limit)
    mainWindow.upper_limit.setMaximumWidth(70)
    mainWindow.lower_limit.setMaximumWidth(70)

    mainWindow.horizontalLayout_3.addLayout(mainWindow.horizontalLayout_5, Qt.AlignRight)

    mainWindow.verticalLayout_5.addLayout(mainWindow.horizontalLayout_3)

    mainWindow.verticalLayout_6.addWidget(mainWindow.upper_bar)

    mainWindow.splitter = QSplitter(mainWindow.widget_3)
    mainWindow.splitter.setOrientation(Qt.Horizontal)

    mainWindow.stacked_widget.addWidget(mainWindow.ram_graph_widget)
    mainWindow.page_2 = QWidget()
    mainWindow.stacked_widget.addWidget(mainWindow.cpu_graph_widget)
    mainWindow.page_3 = QWidget()
    mainWindow.stacked_widget.addWidget(mainWindow.bar_chart_widget)
    mainWindow.splitter.addWidget(mainWindow.stacked_widget)

    mainWindow.splitter.addWidget(mainWindow.table_widget)

    mainWindow.verticalLayout_6.addWidget(mainWindow.splitter)

    mainWindow.horizontalLayout_4.addWidget(mainWindow.widget_3)

    mainWindow.setCentralWidget(mainWindow.centralwidget)
    QWidget.setTabOrder(mainWindow.pause_button, mainWindow.cancel_button)
    QWidget.setTabOrder(mainWindow.cancel_button, mainWindow.load_button)

    QWidget.setTabOrder(mainWindow.menu_button, mainWindow.ram_button)
    QWidget.setTabOrder(mainWindow.ram_button, mainWindow.cpu_button)
    QWidget.setTabOrder(mainWindow.cpu_button, mainWindow.runtime_button)
    QWidget.setTabOrder(mainWindow.runtime_button, mainWindow.table_widget)

    mainWindow.sidebar.setHidden(True)
    mainWindow.menu_button.toggled.connect(mainWindow.sidebar.setVisible)

    QMetaObject.connectSlotsByName(mainWindow)

    resume_icon = qta.icon("msc.debug-restart")
    mainWindow.pause_button.setIcon(resume_icon)
    load_icon = qta.icon("fa.file")
    mainWindow.load_button.setIcon(load_icon)
    resume_icon = qta.icon("msc.debug-restart")
    mainWindow.pause_button.setIcon(resume_icon)
    icon = qta.icon("ei.align-justify")
    mainWindow.menu_button.setIcon(icon)
    # setupUi
