from PyQt5.QtCore import QSize, Qt, QMetaObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpacerItem,
                             QSplitter)

import qtawesome as qta


def setup_ui(main_window):
    """Sets up all layouts and sizes for the main window so the widgets fit in nicely"""
    main_window.centralwidget = main_window.central_widget
    main_window.sidebar = QWidget(main_window.centralwidget)
    main_window.widget_3 = QWidget(main_window.centralwidget)
    main_window.upper_bar = QWidget(main_window.widget_3)
    # Layouts
    main_window.main_layout = QHBoxLayout(main_window.centralwidget)
    main_window.sidebar_layout = QVBoxLayout(main_window.sidebar)
    main_window.main_horizontal_layout = QVBoxLayout(main_window.widget_3)
    main_window.upper_bar_layout = QVBoxLayout(main_window.upper_bar)
    main_window.upper_bar_tool_layout = QHBoxLayout()
    main_window.upper_bar_horizontal = QHBoxLayout()

    main_window.horizontalLayout = QHBoxLayout()
    main_window.sidebar_button_layout = QVBoxLayout()

    main_window.resize(800, 615)
    sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
    main_window.setSizePolicy(sizePolicy)
    main_window.main_layout.setSpacing(5)
    main_window.main_layout.setContentsMargins(0, 0, 0, 0)
    main_window.verticalSpacer_2 = QSpacerItem(20, 495, QSizePolicy.Minimum, QSizePolicy.Expanding)
    main_window.horizontalSpacer_3 = QSpacerItem(30, 20, QSizePolicy.Minimum)
    #configuring sidebar
    main_window.sidebar.setMinimumSize(QSize(140, 0))
    main_window.sidebar.setMaximumSize(QSize(400, 16777215))
    main_window.sidebar_layout.setSpacing(0)
    main_window.sidebar_layout.setContentsMargins(3, 3, 3, 3)
    main_window.horizontalLayout.setSpacing(10)
    main_window.sidebar_button_layout.setSpacing(10)
    main_window.label = QLabel(main_window.sidebar)
    main_window.sidebar_button_layout.addWidget(main_window.label)
    icon_label2 = QLabel()
    icon_label2.setAlignment(Qt.AlignHCenter)
    icon_label2.setPixmap(QIcon('src/view/GUI/Images/CTIEngineLogo.png').pixmap(40, 40))
    main_window.sidebar_button_layout.addWidget(icon_label2)
    main_window.load_button = main_window.menu_bar.load_file_button
    main_window.sidebar_button_layout.addWidget(main_window.load_button)
    main_window.cancel_button = main_window.menu_bar.cancel_button
    main_window.sidebar_button_layout.addWidget(main_window.cancel_button)
    main_window.pause_button = main_window.menu_bar.pause_resume_button
    main_window.sidebar_button_layout.addWidget(main_window.pause_button)
    main_window.project_scroll_button = main_window.menu_bar.scroll_button
    main_window.scroll_bar = main_window.menu_bar.scroll_bar
    main_window.scroll_bar.setWidgetResizable(True)
    main_window.scroll_bar.setHidden(True)
    main_window.scroll_bar.setMaximumSize(135, 500)
    main_window.scroll_bar.setMinimumHeight(200)
    main_window.sidebar_button_layout.addWidget(main_window.project_scroll_button)
    main_window.sidebar_button_layout.addWidget(main_window.scroll_bar)
    main_window.horizontalLayout.addLayout(main_window.sidebar_button_layout)
    main_window.sidebar_layout.addLayout(main_window.horizontalLayout)
    main_window.verticalSpacer = QSpacerItem(20, 700, QSizePolicy.Maximum, QSizePolicy.Expanding)
    main_window.sidebar_layout.addItem(main_window.verticalSpacer)
    main_window.switch_style_box = main_window.menu_bar.switch_style_box
    main_window.sidebar_layout.addWidget(main_window.switch_style_box)
    main_window.main_layout.addWidget(main_window.sidebar, 0, Qt.AlignLeft)

    # configuring the upper bar
    main_window.main_horizontal_layout.setSpacing(10)
    main_window.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
    main_window.upper_bar.setMinimumWidth(1000)
    main_window.upper_bar.setMaximumSize(QSize(1500, 50))
    main_window.upper_bar_layout.setSpacing(0)
    main_window.upper_bar_layout.setContentsMargins(0, 0, 0, 0)
    main_window.upper_bar_tool_layout.setSpacing(10)
    main_window.menu_button = QPushButton(main_window.upper_bar)
    main_window.menu_button.setMaximumSize(30, 30)
    main_window.menu_button.setCheckable(True)
    main_window.small_spacer = QSpacerItem(4, 0, QSizePolicy.Minimum)
    main_window.upper_bar_tool_layout.addItem(main_window.small_spacer)
    main_window.upper_bar_tool_layout.addWidget(main_window.menu_button)
    main_window.ram_button = main_window.metric_bar.ram_button
    main_window.upper_bar_tool_layout.addWidget(main_window.ram_button)
    main_window.cpu_button = main_window.metric_bar.cpu_button
    main_window.upper_bar_tool_layout.addWidget(main_window.cpu_button)
    main_window.runtime_button = main_window.metric_bar.runtime_button
    main_window.upper_bar_tool_layout.addWidget(main_window.runtime_button)
    main_window.upper_bar_tool_layout.addWidget(main_window.status_bar)
    main_window.upper_bar_tool_layout.addItem(main_window.horizontalSpacer_3)
    main_window.upper_bar_horizontal.addWidget(main_window.line_edit)
    main_window.line_edit.setPlaceholderText("Search...")
    main_window.upper_bar_horizontal.addWidget(main_window.search_button)
    main_window.upper_bar_horizontal.addWidget(main_window.upper_limit)
    main_window.upper_bar_horizontal.addWidget(main_window.lower_limit)
    main_window.upper_limit.setMaximumWidth(70)
    main_window.lower_limit.setMaximumWidth(70)
    main_window.select_all_checkbox.setMaximumWidth(80)
    main_window.upper_bar_horizontal.addWidget(main_window.select_all_checkbox)
    main_window.upper_bar_tool_layout.addLayout(main_window.upper_bar_horizontal, Qt.AlignRight)
    main_window.upper_bar_layout.addLayout(main_window.upper_bar_tool_layout)
    main_window.main_horizontal_layout.addWidget(main_window.upper_bar)
    # configuring the center (graphical widgets)
    main_window.splitter = QSplitter(main_window.widget_3)
    main_window.splitter.setOrientation(Qt.Horizontal)
    main_window.stacked_widget.addWidget(main_window.ram_graph_widget)
    main_window.page_2 = QWidget()
    main_window.stacked_widget.addWidget(main_window.cpu_graph_widget)
    main_window.page_3 = QWidget()
    main_window.stacked_widget.addWidget(main_window.bar_chart_widget)
    main_window.splitter.addWidget(main_window.stacked_widget)
    main_window.splitter.addWidget(main_window.stacked_table_widget)
    main_window.main_horizontal_layout.addWidget(main_window.splitter)
    main_window.main_layout.addWidget(main_window.widget_3)
    main_window.setCentralWidget(main_window.centralwidget)
    QWidget.setTabOrder(main_window.pause_button, main_window.cancel_button)
    QWidget.setTabOrder(main_window.cancel_button, main_window.load_button)

    QWidget.setTabOrder(main_window.menu_button, main_window.ram_button)
    QWidget.setTabOrder(main_window.ram_button, main_window.cpu_button)
    QWidget.setTabOrder(main_window.cpu_button, main_window.runtime_button)
    QWidget.setTabOrder(main_window.runtime_button, main_window.current_table)

    main_window.sidebar.setHidden(True)
    main_window.menu_button.toggled.connect(main_window.sidebar.setVisible)

    QMetaObject.connectSlotsByName(main_window)
    # add icons and stylistic details
    resume_icon = qta.icon("msc.debug-restart")
    main_window.pause_button.setIcon(resume_icon)
    load_icon = qta.icon("fa.file")
    main_window.load_button.setIcon(load_icon)
    resume_icon = qta.icon("msc.debug-restart")
    main_window.pause_button.setIcon(resume_icon)
    icon = qta.icon("ei.align-justify")
    main_window.menu_button.setIcon(icon)

    cancel_icon = qta.icon("ei.ban-circle")
    main_window.cancel_button.setIcon(cancel_icon)
    menu_icon = qta.icon("ei.align-justify")
    main_window.project_scroll_button.setIcon(menu_icon)
    search_icon = qta.icon("fa.search")
    main_window.search_button.setIcon(search_icon)

    main_window.current_table.setStyleSheet("::section{Background-color: #4095a1}")
    main_window.sidebar.setStyleSheet(u"background-color: rgb(61, 61, 61);")





