import ipywidgets as widgets
import xml.etree.ElementTree as ET  # https://docs.python.org/2/library/xml.etree.elementtree.html
import os
import glob
import shutil
import math
import datetime
import tempfile
from about import AboutTab
# from terminal import TerminalTab
from notebook import notebookapp

from config import ConfigTab
from microenv_params import MicroenvTab
from user_params import UserTab
# from svg import SVGTab
from substrates import SubstrateTab
from pathlib import Path
import platform
import subprocess
from debug import debug_view

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import RunCommand, Submit
        from hublib.ui import PathSelector, Dropdown
    except:
        hublib_flag = False
else:
    hublib_flag = False


# join_our_list = "(Join/ask questions at https://groups.google.com/forum/#!forum/physicell-users)\n"


# create the tabs, but don't display yet
about_tab = AboutTab()
config_tab = ConfigTab()

xml_file = os.path.join('data', 'PhysiCell_settings.xml')
full_xml_filename = os.path.abspath(xml_file)

tree = ET.parse(full_xml_filename)  # this file cannot be overwritten; part of tool distro
xml_root = tree.getroot()
microenv_tab = MicroenvTab()
user_tab = UserTab()
# svg = SVGTab()
sub = SubstrateTab()

nanoHUB_flag = False
if( 'HOME' in os.environ.keys() ):
    nanoHUB_flag = "home/nanohub" in os.environ['HOME']


def read_config_cb(_b):
    # with debug_view:
    #     print("read_config_cb", read_config.value)

    if read_config.value is None:  #occurs when a Run just finishes and we update pulldown with the new cache dir??
        # with debug_view:
        #     print("NOTE: read_config_cb(): No read_config.value. Returning!")
        return

    if os.path.isdir(read_config.value):
        is_dir = True
        config_file = os.path.join(read_config.value, 'config.xml')
    else:
        is_dir = False
        config_file = read_config.value

    if Path(config_file).is_file():
        # with debug_view:
        #     print("read_config_cb:  calling fill_gui_params with ",config_file)
        fill_gui_params(config_file)  #should verify file exists!
    else:
        # with debug_view:
        #     print("read_config_cb: ",config_file, " does not exist.")
        return
    
    # update visualization tabs
    if is_dir:
        # svg.update(read_config.value)
        sub.update(read_config.value)
    else:  # may want to distinguish "DEFAULT" from other saved .xml config files
        # FIXME: really need a call to clear the visualizations
        # svg.update('')
        sub.update('')
        

# Using the param values in the GUI, write a new .xml config file
def write_config_file(name):
    # with debug_view:
    #     print("write_config_file: based on ",full_filename)
    tree = ET.parse(full_xml_filename)  # this file cannot be overwritten; part of tool distro
    xml_root = tree.getroot()
    config_tab.fill_xml(xml_root)
    microenv_tab.fill_xml(xml_root)
    user_tab.fill_xml(xml_root)
    tree.write(name)

    # update substrate mesh layout (beware of https://docs.python.org/3/library/functions.html#round)
    sub.numx =  math.ceil( (config_tab.xmax.value - config_tab.xmin.value) / config_tab.xdelta.value )
    sub.numy =  math.ceil( (config_tab.ymax.value - config_tab.ymin.value) / config_tab.ydelta.value )
    # print("------- sub.numx, sub.numy = ", sub.numx, sub.numy)


# callback from write_config_button
def write_config_file_cb(b):
    path_to_share = os.path.join('~', '.local','share','pc4training')
    dirname = os.path.expanduser(path_to_share)

    val = write_config_box.value
    if val == '':
        val = write_config_box.placeholder
    name = os.path.join(dirname, val)
    write_config_file(name)


# Fill the "Load Config" dropdown widget with valid cached results (and 
# default & previous config options)
def get_config_files():
    cf = {'DEFAULT': full_xml_filename}
    path_to_share = os.path.join('~', '.local','share','pc4training')
    dirname = os.path.expanduser(path_to_share)
    try:
        os.makedirs(dirname)
    except:
        pass
    files = glob.glob("%s/*.xml" % dirname)
    # dict.update() will append any new (key,value) pairs
    cf.update(dict(zip(list(map(os.path.basename, files)), files)))

    # Find the dir path (full_path) to the cached dirs
    if nanoHUB_flag:
        full_path = os.path.expanduser("~/data/results/.submit_cache/pc4training")  # does Windows like this?
    else:
        # local cache
        try:
            cachedir = os.environ['CACHEDIR']
            full_path = os.path.join(cachedir, "pc4training")
        except:
            # print("Exception in get_config_files")
            return cf

    # Put all those cached (full) dirs into a list
    dirs_all = [os.path.join(full_path, f) for f in os.listdir(full_path) if f != '.cache_table']

    # Only want those dirs that contain output files (.svg, .mat, etc), i.e., handle the
    # situation where a user cancels a Run before it really begins, which may create a (mostly) empty cached dir.
    dirs = [f for f in dirs_all if len(os.listdir(f)) > 5]   # "5" somewhat arbitrary
    # with debug_view:
    #     print(dirs)

    # Get a list of sorted dirs, according to creation timestamp (newest -> oldest)
    sorted_dirs = sorted(dirs, key=os.path.getctime, reverse=True)
    # with debug_view:
    #     print(sorted_dirs)

    # Get a list of timestamps associated with each dir
    sorted_dirs_dates = [str(datetime.datetime.fromtimestamp(os.path.getctime(x))) for x in sorted_dirs]
    # Create a dict of {timestamp:dir} pairs
    cached_file_dict = dict(zip(sorted_dirs_dates, sorted_dirs))
    cf.update(cached_file_dict)
    # with debug_view:
    #     print(cf)
    return cf

#-------------------------------------------------
# def updateDropdown( ps, tb ):
# #    options = [file[1] for file in ps.select.options if file[0].startswith("[") is False]
#    options = [file[1] for file in ps.select.options]
#    if len(options) > 0:
#        tb.dd.options = options
#        tb.dd.value = options[0]
#    else:
#        tb.dd.options = ["."]
#        tb.dd.value = "."

# if (nanoHUB_flag or hublib_flag):
#     # path_sel = PathSelector('.', select_file=False)
#     path_sel = PathSelector('.', select_file=True)
#     out_dir_dropdown = Dropdown( name='Output', value='.', options=['.'])
#     path_sel.select.observe(lambda change: updateDropdown(path_sel, out_dir_dropdown), 'value')            
#     updateDropdown(path_sel, out_dir_dropdown)
#     # widgets.VBox([path_sel.accord,out_dir_dropdown])

def updateDropdown( ps ):
#    options = [file[1] for file in ps.select.options if file[0].startswith("[") is True]
#    print(ps.value)
    output_dir = ps.value
    sub.update(output_dir)

if (nanoHUB_flag or hublib_flag):
    path_sel = PathSelector('.', select_file=False)
    path_sel.select.observe(lambda change: updateDropdown(path_sel), 'value')
    updateDropdown(path_sel)

# if nanoHUB_flag or hublib_flag:
#     read_config = widgets.Dropdown(
#         description='Load Config',
#         options=get_config_files(),
#         tooltip='Config File or Previous Run',
#     )
#     read_config.style = {'description_width': '%sch' % str(len(read_config.description) + 1)}
#     read_config.observe(read_config_cb, names='value') 

tab_height = 'auto'
tab_layout = widgets.Layout(width='auto',height=tab_height, overflow_y='scroll',)   # border='2px solid black',

#---------------------
servers = list(notebookapp.list_running_servers())
url = None
if nanoHUB_flag:
    with open(os.environ["SESSIONDIR"]+"/resources") as file:
        sessionid = [line.split(" ", 1)[1].strip() for line in file.readlines() if line.startswith('sessionid')]
        if len(sessionid) > 0:
            url = [server['base_url'] for server in servers if sessionid[0] in server['base_url']]
            url = url[0] + "terminals/new"
else:
    # url = "/" + "terminals/new"
    url = "/" 
if url is not None:
    iframe = "<iframe width='100%' height='100%' src='"+url+"'></iframe>"
    html = widgets.HTML(value="", layout=widgets.Layout(height='600px'))
    term_tab = widgets.Tab([html])
#---------------------

titles = ['About', 'Terminal', 'Out: Plots']
tabs = widgets.Tab(children=[about_tab.tab, term_tab, sub.tab],
                  _titles={i: t for i, t in enumerate(titles)},
                  layout=tab_layout)
tabs.observe(lambda c, w=html: setattr(w, "value", iframe if c["new"] == 1 else ""), names=['selected_index'])

homedir = os.getcwd()

tool_title = widgets.Label(r'\(\textbf{PhysiCell training workbench}\)')
if nanoHUB_flag or hublib_flag:
#    top_row = widgets.HBox(children=[read_config, tool_title])
    # top_row = widgets.HBox(children=[out_dir_dropdown, tool_title])
    top_row = widgets.HBox(children=[path_sel.accord, tool_title])
    gui = widgets.VBox(children=[top_row, tabs])
    # fill_gui_params(read_config.options['DEFAULT'])
else:
    top_row = widgets.HBox(children=[tool_title])
    # gui = widgets.VBox(children=[top_row, tabs, run_button])
    gui = widgets.VBox(children=[top_row, tabs])
    # fill_gui_params("data/PhysiCell_settings.xml")


# pass in (relative) directory where output data is located
# output_dir = "tmpdir"
# svg.update(output_dir)
# sub.update_dropdown_fields("data")
# sub.update(output_dir)
