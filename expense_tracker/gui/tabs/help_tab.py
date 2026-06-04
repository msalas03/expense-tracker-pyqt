from PyQt6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget


def build_help_tab(win) -> None:
    win.tab_help = QWidget()
    win.tabs.addTab(win.tab_help, win.tr_gui("tab_help"))

    v = QVBoxLayout(win.tab_help)

    win.lbl_help_title = QLabel()
    win._bind_text(win.lbl_help_title, "setText", "help_title")
    title = win.lbl_help_title

    f = title.font()
    f.setPointSize(f.pointSize() + 2)
    f.setBold(True)
    title.setFont(f)
    v.addWidget(title)

    win.help_view = QTextBrowser()
    win.help_view.setOpenExternalLinks(True)
    win.help_view.setOpenLinks(True)
    win.help_view.setHtml(help_html(win))
    win.help_view.setMinimumHeight(300)

    v.addWidget(win.help_view)


def help_html(win) -> str:
    return win.tr_gui("help_html")