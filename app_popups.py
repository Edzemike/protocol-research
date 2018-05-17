# -*- coding: utf-8 -*-
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class AppPopups():
    popup_connected = Popup(title='Connected',
                          content=Label(text='Succsessfully connected to broker'),
                          size_hint=(1, .5))
    popup_connection_failed = Popup(title='Not connected',
                                    content=Label(text='Attempt to connect failed'),
                                    size_hint=(1, .5))
    testvalue = "pasiekė kintamaji"
