#!/usr/bin/env python2
#-*- encoding:utf8 -*-
"""

Simple DMX Controller using a python WX app, and an arduino + transistor driver

This use pyserial as a transmitter

"""
import sys
from glob import glob
import wx
from serial import Serial, SerialException

class DMXController(wx.Frame):
    """
    Main class for controller
    """

    def __init__(self, parent):
        # Define hte size as a class atribute
        self.size = (300, 500)
        wx.Frame.__init__(self, parent, title="DMX Controller", size=self.size)

        # initial values for DMX
        self.values = {
            'r': 0,
            'g': 0,
            'b': 0
        }

        self.baudrate = 9600
        self.conn = False

        title = wx.StaticText(self, label="Python DMX Controller")

        # sliders will be contained in three vertical sizer stacked in a horizontal one
        self.sliders_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # instanciate 3 sliders
        self.sliders = {}
        self.sliders['r'] = wx.Slider(self, -1, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.sliders['g'] = wx.Slider(self, -1, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.sliders['b'] = wx.Slider(self, -1, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.Bind(wx.EVT_SLIDER, self.SliderR, self.sliders['r'])
        self.Bind(wx.EVT_SLIDER, self.SliderG, self.sliders['g'])
        self.Bind(wx.EVT_SLIDER, self.SliderB, self.sliders['b'])

        # Add the to the slider
        buttons = []
        for slider,name,flash,stop_flash in [(self.sliders['r'],"&Red", self.FlashRed, self.StopFlashRed),
                            (self.sliders['g'],"&Green", self.FlashGreen, self.StopFlashGreen),
                            (self.sliders['b'],"&Blue", self.FlashBlue, self.StopFlashBlue)]:
            # create vertical sizer for slider+text
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(slider, 1, wx.EXPAND) # add the slider itself

            buttons.append(wx.Button(self, -1, name))
            buttons[-1].Bind(wx.EVT_LEFT_DOWN, flash)
            buttons[-1].Bind(wx.EVT_LEFT_UP, stop_flash)

            sizer.Add(buttons[-1])

            # then stuck the sizer in the horizontal one
            self.sliders_sizer.Add(sizer, 1, wx.EXPAND)
            # set min and max values to slider
            slider.SetMin(0)
            slider.SetMax(255)

        # create a logger and add this to the horizontal sizer
        self.logger = wx.TextCtrl(self, size=(-1,50), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Ports Menu
        self.ports_menu = wx.Menu()
        find_ports = self.ports_menu.Append(-1, "&Find Serial Ports", "Try to find some ports in /dev/*")
        self.Bind(wx.EVT_MENU, self.FindSerialPorts, find_ports)


        # macros menu
        macros_menu = wx.Menu()
        self.Bind(wx.EVT_MENU,
                  self.Macro_BlackOut,
                  macros_menu.Append(-1, "&BlackOut", "Turn all 3 channels to 0")
                 )
        self.Bind(wx.EVT_MENU,
                  self.Macro_SpotLight,
                  macros_menu.Append(-1, "&SpotLight", "Turn all 3 channels to max")
                 )
        macros_menu.AppendSeparator()
        self.Bind(wx.EVT_MENU,
                  self.Macro_Red,
                  macros_menu.Append(-1, "&Red", "All red")
                 )
        self.Bind(wx.EVT_MENU,
                  self.Macro_Green,
                  macros_menu.Append(-1, "&Green", "All green")
                 )
        self.Bind(wx.EVT_MENU,
                  self.Macro_Blue,
                  macros_menu.Append(-1, "B&lue", "All blue")
                 )



        # main menu
        main_menu = wx.Menu()
        main_menu_exit = main_menu.Append(wx.ID_EXIT, "&Quit", "Quit this program")
        self.Bind(wx.EVT_MENU, self.OnExit, main_menu_exit)

        # This will be the main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.EXPAND)
        self.main_sizer.Add(self.sliders_sizer, 1, wx.EXPAND)
        self.main_sizer.Add(self.logger, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)

        # init menubar
        menubar = wx.MenuBar()
        menubar.Append(main_menu, "&General")
        menubar.Append(macros_menu, "&Macros")
        menubar.Append(self.ports_menu, "&Serial")
        self.SetMenuBar(menubar)

        self.CreateStatusBar()

        # Look up for ports before showing the window
        self.FindSerialPorts()

        # now, show it
        self.Show()


    def OnExit(self, event):
        """
        Close any existent connection and terminate the program
        """
        if self.conn:
            self.conn.close()
        self.Close(True)


    def FindSerialPorts(self, event=None):
        """
        Just glob over /dev/tty{ACM,USB}* to find the arduino serial port

        I could have used serial.tools.list_ports.comports(), but it's simpler like that
        """

        # First get a list as in ls /dev/tty{ACM,USB}*
        self.serial_ports = {}
        serial_ports = glob("/dev/ttyACM*")+glob("/dev/ttyUSB*")

        # if only one item, open a connection on it
        if len(serial_ports) == 1:
            self.SelectPort(chosen_port=serial_ports[0])

        # if some ports found, tell the number to user through the logger and add them to menu
        if len(serial_ports):
            self.logger.AppendText("{} serial ports found\n".format(len(serial_ports)))

            self.ports_menu.AppendSeparator()
            for s in serial_ports:
                this = self.ports_menu.Append(-1, s, s)
                self.Bind(wx.EVT_MENU, self.SelectPort, this)
                self.serial_ports[this.GetId()] = s

        else:
            self.logger.AppendText("I didn't find any opened serial port. You won't control anything\n")


    def SelectPort(self, event=None, chosen_port=None):
        """ Init a serial connection on chosen serial port """
        if not chosen_port:
            chosen_port = self.serial_ports[event.GetId()]

        # first, close current connection if exists
        if self.conn:
            self.conn.close()
            self.conn = False

        # then try to open a new one on the selected port
        self.logger.AppendText("Trying to initalize connection through {}\n".format(chosen_port))
        try:
            self.conn = Serial(chosen_port, self.baudrate, timeout=1)
        except SerialException as e:
            self.logger.AppendText(e)


    def send_values(self, values=None):
        """ Send values from values parameter to arduino """

        # if not any specific set of values specified, just use self.values
        if not values:
            values = self.values

        # send each value through connection and tell error if any (in logger)
        try:
            for c in ['r','g','b']:
                self.conn.write(chr(values[c]))
        except ValueError as e:
            self.logger.AppendText(str(e))


    # Redirection functions
    def SliderR(self, event): self.ComputeSlider('r', event)
    def SliderG(self, event): self.ComputeSlider('g', event)
    def SliderB(self, event): self.ComputeSlider('b', event)

    def ComputeSlider(self, slider, event):
        """ Get the new value from slider and ressend order to arduino """
        if not self.conn:
            self.logger.AppendText("No connection \n")
        else:
            value = self.sliders[slider].GetValue()

            self.values[slider] = value

            # send new values to the arduino
            self.send_values()


    def align_sliders(self):
        """
        Put sliders at the right place according to self.values

        if self.values is durabily modified, move the slider to fit
        """
        for s in self.values.keys():
            self.sliders[s].SetValue(self.values[s])

    ### Flashes ###
    def Flash(self, chan, level):
        """ put one level at "level" and resend all """
        values = {k:self.values[k] for k in self.values.keys()}
        values[chan] = level
        self.send_values(values)

    # redirection functions
    def FlashRed(self, e): self.Flash('r', 255)
    def FlashGreen(self, e): self.Flash('g', 255)
    def FlashBlue(self, e): self.Flash('b', 255)

    def StopFlashRed(self, e): self.Flash('r', self.values['r'])
    def StopFlashGreen(self, e): self.Flash('g', self.values['g'])
    def StopFlashBlue(self, e): self.Flash('b', self.values['b'])


    ### Macros ###
    def Macro_BlackOut(self, e):
        """ Turn off all 3 channels """
        self.values = {_:0 for _ in self.values.keys()}
        self.align_sliders()
        self.send_values()

    def Macro_SpotLight(self, e):
        """ Turn on all 3 channels """
        self.values = {_:255 for _ in self.values.keys()}
        self.align_sliders()
        self.send_values()

    def Macro_Red(self, e):
        """ Turn all channels off and red chan to max """
        self.values = {_:0 for _ in self.values.keys()}
        self.values['r'] = 255
        self.align_sliders()
        self.send_values()

    def Macro_Green(self, e):
        """ Turn all channels off and green chan to max """
        self.values = {_:0 for _ in self.values.keys()}
        self.values['g'] = 255
        self.align_sliders()
        self.send_values()

    def Macro_Blue(self, e):
        """ Turn all channels off and blue chan to max """
        self.values = {_:0 for _ in self.values.keys()}
        self.values['b'] = 255
        self.align_sliders()
        self.send_values()



if __name__=='__main__':
    app = wx.App(False)
    frame = DMXController(None)
    app.MainLoop()

