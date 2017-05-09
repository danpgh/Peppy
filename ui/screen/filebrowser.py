# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
# 
# This file is part of Peppy Player.
# 
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import pygame
import os

from ui.page import Page
from ui.component import Component
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.keys import SCREEN_RECT, COLOR_DARK_LIGHT, COLOR_CONTRAST, COLORS, \
    GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, \
    KEY_PLAY_FILE, CLICKABLE_RECT, FILE_PLAYBACK
from util.config import CURRENT_FOLDER, AUDIO, MUSIC_FOLDER, CURRENT_FILE_PLAYBACK_MODE, CURRENT_FILE_PLAYLIST
from util.fileutil import FILE_AUDIO, FILE_PLAYLIST
from ui.menu.navigator import Navigator
from ui.menu.filemenu import FileMenu
from ui.state import State

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 16.50
PERCENT_TITLE_FONT = 66.66

class FileBrowserScreen(Container):
    """ File Browser Screen """
    
    def __init__(self, util, get_current_playlist, playlist_provider, listeners):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        """
        self.util = util
        self.config = util.config
        Container.__init__(self, util, background=(0, 0, 0))
        self.factory = Factory(util)
        self.bounding_box = self.config[SCREEN_RECT]
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        font_size = (layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        color_dark_light = self.config[COLORS][COLOR_DARK_LIGHT]
        color_contrast = self.config[COLORS][COLOR_CONTRAST]
        current_folder = self.util.file_util.current_folder  
        
        self.screen_title = self.factory.create_dynamic_text("file_browser_screen_title", layout.TOP, color_dark_light, color_contrast, int(font_size))
        Container.add_component(self, self.screen_title)
        d = {"current_title" : current_folder}
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            f = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            p = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            d = f + os.sep + p
        
        self.screen_title.set_text(d)
        
        rows = 3
        columns = 3
        self.filelist = None
        
        if not self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]:
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] = FILE_AUDIO
        
        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_AUDIO:
            folder_content = self.util.load_folder_content(current_folder, rows, columns, layout.CENTER)  
            self.filelist = Page(folder_content, rows, columns)
        elif self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            s = State()
            s.folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            s.music_folder = self.config[AUDIO][MUSIC_FOLDER]
            s.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
            
            pl = self.get_filelist_items(get_current_playlist)
            if len(pl) == 0:            
                pl = self.util.load_playlist(s, playlist_provider, rows, columns)
            else:
                pl = self.util.load_playlist_content(pl, rows, columns)
            self.filelist = Page(pl, rows, columns)
        
        self.file_menu = FileMenu(self.filelist, util, playlist_provider, (0, 0, 0), layout.CENTER)
        
        Container.add_component(self, self.file_menu)
        self.file_menu.add_change_folder_listener(self.screen_title.set_text)
        self.file_menu.add_play_file_listener(listeners[KEY_PLAY_FILE])
        
        listeners[GO_LEFT_PAGE] = self.file_menu.page_down
        listeners[GO_RIGHT_PAGE] = self.file_menu.page_up
        listeners[GO_USER_HOME] = self.file_menu.switch_to_user_home
        listeners[GO_ROOT] = self.file_menu.switch_to_root
        listeners[GO_TO_PARENT] = self.file_menu.switch_to_parent_folder
        listeners[KEY_PLAY_FILE] = listeners[KEY_PLAY_FILE]
        listeners[GO_BACK] = listeners[GO_BACK]
        
        layout.BOTTOM.h = self.bounding_box.h - (layout.TOP.h + layout.CENTER.h + 2)
        layout.BOTTOM.y = layout.TOP.h + layout.CENTER.h + 1
        if self.bounding_box.h == 320:
            layout.BOTTOM.h += 1
            layout.BOTTOM.y -= 1
        self.navigator = Navigator(util, layout.BOTTOM, listeners, color_dark_light)
        left = str(self.filelist.get_left_items_number())
        right = str(self.filelist.get_right_items_number())
        self.navigator.left_button.change_label(left)
        self.navigator.right_button.change_label(right)
        
        self.file_menu.add_left_number_listener(self.navigator.left_button.change_label)
        self.file_menu.add_right_number_listener(self.navigator.right_button.change_label)
        Container.add_component(self, self.navigator)
        self.page_turned = False    
    
    def get_filelist_items(self, get_current_playlist):
        """ Call player for files in the playlist 
        
        :return: list of files from playlist
        """
        playlist = get_current_playlist()
        files = []
        if playlist:
            for n in range(len(playlist)):
                st = State()
                st.index = st.comparator_item = n
                st.file_type = FILE_AUDIO
                st.file_name = st.url = playlist[n]
                files.append(st)
        return files
    
    def get_clickable_rect(self):
        """ Return file browser bounding box. 
        
        :return: list of rectangles
        """
        bb = self.screen_title.bounding_box
        x = 0
        y = bb.h
        w = self.bounding_box.width
        h = self.bounding_box.height - bb.h
        
        c = Component(self.util)
        c.name = CLICKABLE_RECT
        c.bgr = c.fgr = (0, 0, 0)
        c.content_x = c.content_y = 0
        c.content = pygame.Rect(x, y, w, h)
        d = [c]       
        return d
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
    