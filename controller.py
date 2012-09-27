#!/usr/bin/env python2
#-*- encoding:utf8 -*-
"""

Simple DMX Controller using a python WX app, and an arduino + transistor driver

This use pyserial as a transmitter

"""
import sys
import os
import  wx
import serial

class DMXController(wx.Frame):
    """
    Main class for controller
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="DMX Controller", size=(150, -1))

        self.CreateStatusBar()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Python DMX Controller")
        self.sliders_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # instanciate 3 sliders
        self.slider_r = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.Bind(wx.EVT_SLIDER, self.SliderR, self.slider_r)
        self.slider_g = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.Bind(wx.EVT_SLIDER, self.SliderG, self.slider_g)
        self.slider_b = wx.Slider(self, -1, style=wx.SL_VERTICAL)
        self.Bind(wx.EVT_SLIDER, self.SliderB, self.slider_r)

        # Add the to the slider
        for slider in [self.slider_r, self.slider_g, self.slider_b]:
            self.sliders_sizer.Add(slider, 1, wx.EXPAND)

        self.main_sizer.Add(title, 0, wx.EXPAND)
        self.main_sizer.Add(self.sliders_sizer, 1, wx.EXPAND)

        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)
        self.main_sizer.Fit(self)
        self.Show()

    def SliderR(self, event): self.ComputeSlider('R', event)
    def SliderG(self, event): self.ComputeSlider('G', event)
    def SliderB(self, event): self.ComputeSlider('B', event)

    def ComputeSlider(self, slider, event):
        pass

if __name__=='__main__':
    app = wx.App(False)
    frame = DMXController(None)
    app.MainLoop()

