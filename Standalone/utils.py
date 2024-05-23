def center_window(window, width, height):
    screen_width = window.screen().size().width()
    screen_height = window.screen().size().height()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.setGeometry(int(x), int(y), width, height)
