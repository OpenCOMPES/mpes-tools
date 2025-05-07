class Cursor_handler:
    def __init__(self,fig,ax, artist, changes=None,parent=None):
        self.artist=artist
        self.active_cursor=None
        self.changes=changes
        self.parent = parent
        self.ax=ax
        self.fig=fig
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
    def on_pick(self,event): # function to pick up the cursors or the dots
        if event.artist == self.artist and self.parent.active_handler is None:
            self.active_cursor = self.artist
            self.parent.active_handler = self 
    def on_motion(self,event): # function to move the cursors or the dots
        if self.active_cursor is not None and event.inaxes == self.ax:
            if self.active_cursor == self.artist:
                if self.artist.get_xdata()[0]==self.artist.get_xdata()[1]:
                    self.artist.set_xdata([event.xdata, event.xdata])
                    self.changes()
                else :
                    self.artist.set_ydata([event.ydata, event.ydata])
                    self.changes()
    def on_release(self,event):
        self.active_cursor = None  
        self.parent.active_handler = None
 
                
