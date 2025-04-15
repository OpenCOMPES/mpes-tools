class SubplotClickHandler:
    def __init__(self, ax, on_subplot_click=None):
        self.ax = ax
        self.on_subplot_click = on_subplot_click

    def handle_double_click(self, event):
        # print(f"event.inaxes id: {id(event.inaxes)}, self.ax id: {id(self.ax)}")
        if not event.dblclick or event.inaxes != self.ax:
            return
        # self.ax.set_title("Clicked", color='red')
        if self.on_subplot_click:
            self.on_subplot_click(self.ax)
