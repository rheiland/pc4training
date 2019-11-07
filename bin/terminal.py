from ipywidgets import Output
from IPython.display import display, HTML

class TerminalTab(object):

    def __init__(self):
        # self.tab = Output(layout={'height': '600px'})
        self.tab = Output(layout={'height': 'auto'})
        self.tab.append_display_data(HTML(filename='doc/about.html'))
        
        from ipywidgets import HTML, Tab, Layout
tab = Tab([HTML(value="<iframe width='100%' height='100%' src='../terminals/new'></iframe>", layout=Layout(height='600px'))])
tab.set_title(0, "Terminal")
display(tab)
