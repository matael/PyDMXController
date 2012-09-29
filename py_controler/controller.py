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
        self.size = (150, 500)
        wx.Frame.__init__(self, parent, title="DMX Controller", size=self.size)

        # initial values for DMX
        self.values = {
            'r': 0x42,
            'g': 0x42,
            'b': 0x42
        }

        self.baudrate = 9600
        self.conn = False

        title = wx.StaticText(self, label="Python DMX Controller")

        # sliders will be contained in three vertical sizer stacked in a horizontal one
        self.sliders_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # instanciate 3 sliders
        self.slider_r = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.slider_g = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.slider_b = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.Bind(wx.EVT_SLIDER, self.SliderR, self.slider_r)
        self.Bind(wx.EVT_SLIDER, self.SliderG, self.slider_g)
        self.Bind(wx.EVT_SLIDER, self.SliderB, self.slider_r)

        # Add the to the slider
        for slider,name in [(self.slider_r,"R"), (self.slider_g,"G"), (self.slider_b,"B")]:
            # create vertical sizer for slider+text
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(slider, 1, wx.EXPAND) # add the slider itself
            # and the associated text
            sizer.Add(wx.StaticText(self, label=name), 0, wx.EXPAND)
            # then stuck the sizer in the horizontal one
            self.sliders_sizer.Add(sizer, 1, wx.EXPAND)
            # set min and max values to slider
            slider.SetMin(0)
            slider.SetMax(255)

        # create a logger and add this to the horizontal sizer
        self.logger = wx.TextCtrl(self, size=(-1,50), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Menu
        self.menu = wx.Menu()
        find_ports = self.menu.Append(-1, "&Find Serial Ports", "Try to find some ports in /dev/*")
        self.Bind(wx.EVT_MENU, self.FindSerialPorts, find_ports)

        # This will be the main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.EXPAND)
        self.main_sizer.Add(self.sliders_sizer, 1, wx.EXPAND)
        self.main_sizer.Add(self.logger, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)

        menubar = wx.MenuBar()
        menubar.Append(self.menu, "&Serial")
        self.SetMenuBar(menubar)

        self.CreateStatusBar()
        self.Show()


    def FindSerialPorts(self, event=None):
        """
        Just glob over /dev/tty{ACM,USB}* to find the arduino serial port

        I could have used serial.tools.list_ports.comports(), but it's simpler like that
        """
        self.serial_ports = {}
        serial_ports = glob("/dev/ttyACM*")+glob("/dev/ttyUSB*")
        if len(serial_ports):
            self.logger.AppendText("{} serial ports found\n".format(len(serial_ports)))

            for s in serial_ports:
                this = self.menu.Append(-1, s, s)
                self.Bind(wx.EVT_MENU, self.SelectPort, this)
                self.serial_ports[this.GetId()] = s

        else:
            self.logger.AppendText("I didn't find any opened serial port. You won't control anything\n")

    def SelectPort(self, event):
        """ Init a serial connection on chosen serial port """
        chosen_port = self.serial_ports[event.GetId()]
        if self.conn:
            self.conn.close()
            self.conn = False
        self.logger.AppendText("Trying to initalize connection through {}\n".format(chosen_port))
        try:
            self.conn = Serial(chosen_port, self.baudrate, timeout=1)
        except SerialException as e:
            self.logger.AppendText(e)


    def SliderR(self, event): self.ComputeSlider('R', event)
    def SliderG(self, event): self.ComputeSlider('G', event)
    def SliderB(self, event): self.ComputeSlider('B', event)

    def ComputeSlider(self, slider, event):
        if not self.conn:
            self.logger.AppendText("No connection \n")
        else:
            if slider=='R':
                value = self.slider_r.GetValue()
            elif slider=='G':
                value = self.slider_g.GetValue()
            else:
                value = self.slider_b.GetValue()

            self.values[slider.lower()] = value

            try:
                for c in ['r','g','b']:
                    self.conn.write(char(self.values[c]))
            except ValueError as e:
                self.logger.AppendText(e)

if __name__=='__main__':
    app = wx.App(False)
    frame = DMXController(None)
    app.MainLoop()

