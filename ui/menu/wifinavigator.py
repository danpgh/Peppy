# Copyright 2019 Peppy Player peppy.player@gmail.com
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

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from util.config import COLORS, COLOR_DARK_LIGHT
from util.keys import GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_HOME, KEY_PLAYER, KEY_PARENT, KEY_NETWORK, KEY_SETUP, \
    KEY_PLAY_PAUSE, KEY_BACK, KEY_CALLBACK, KEY_REFRESH, KEY_SORT

PERCENT_ARROW_WIDTH = 16.0

class WiFiNavigator(Container):
    """ Wi-Fi screen navigator menu """

    def __init__(self, util, bounding_box, listeners, pages):
        """ Initializer

        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param pages: number of Wi-Fi menu pages
        """
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "wifi.navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        bgr = util.config[COLORS][COLOR_DARK_LIGHT]

        arrow_layout = BorderLayout(bounding_box)
        arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)

        if pages > 1:
            constr = arrow_layout.LEFT
            self.left_button = self.factory.create_page_down_button(constr, "0", 40, 100)
            self.left_button.add_release_listener(listeners[GO_LEFT_PAGE])
            self.add_component(self.left_button)
            self.menu_buttons.append(self.left_button)

            constr = arrow_layout.RIGHT
            self.right_button = self.factory.create_page_up_button(constr, "0", 40, 100)
            self.right_button.add_release_listener(listeners[GO_RIGHT_PAGE])
            self.add_component(self.right_button)
            self.menu_buttons.append(self.right_button)
            layout = GridLayout(arrow_layout.CENTER)
        else:
            layout = GridLayout(bounding_box)

        layout.set_pixel_constraints(1, 5, 1, 0)
        layout.current_constraints = 0
        image_size = 64

        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr,
                                                      image_size_percent=image_size)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)

        constr = layout.get_next_constraints()
        self.sort_strength = self.factory.create_button(KEY_REFRESH, KEY_SETUP, constr, listeners[KEY_REFRESH], bgr,
                                                        image_size_percent=image_size)
        self.add_component(self.sort_strength)
        self.menu_buttons.append(self.sort_strength)

        constr = layout.get_next_constraints()
        self.sort_abc = self.factory.create_button(KEY_SORT, KEY_PARENT, constr, listeners[KEY_SORT], bgr,
                                                      image_size_percent=image_size)
        self.add_component(self.sort_abc)
        self.menu_buttons.append(self.sort_abc)

        constr = layout.get_next_constraints()
        self.network_button = self.factory.create_button(KEY_NETWORK, KEY_BACK, constr, listeners[KEY_CALLBACK], bgr,
                                                         image_size_percent=image_size)
        self.add_component(self.network_button)
        self.menu_buttons.append(self.network_button)

        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], bgr,
                                                        image_size_percent=image_size)
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)

    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
