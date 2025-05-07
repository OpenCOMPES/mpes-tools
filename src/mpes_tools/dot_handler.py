class Dot_handler:
    def __init__(self,fig,ax, artist, changes=None):
        self.artist=artist
        self.active_cursor=None
        self.changes=changes
        self.ax=ax
        self.fig=fig
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
    def on_pick(self,event): # function to pick up the cursors or the dots
        if event.artist == self.artist:
            self.active_cursor = self.artist
    def on_motion(self,event): # function to move the cursors or the dots
        if self.active_cursor is not None and event.inaxes == self.ax:
            if self.active_cursor == self.artist:
                self.artist.center= (event.xdata, event.ydata)
                self.changes()
    def on_release(self,event):
        self.active_cursor = None  
        
                
