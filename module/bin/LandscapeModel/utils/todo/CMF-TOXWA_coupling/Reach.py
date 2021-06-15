# -*- coding: utf-8 -*-
import os, io, re, subprocess
import pandas as pd

class Reach(object):
    """
    Class for reach
    """
    def __init__(self, ID):
        """
        ID of this reach
        """
        self.ID = ID

    def set_upstreamIDs(self,upstreamIDs):
        """
        IDs of upstream reaches
        """
        self.upstreamIDs = upstreamIDs

    def set_downstreamIDs(self,downstreamIDs):
        """
        IDs of downstream reaches (currently not used)
        """
        self.downstreamIDs = downstreamIDs

    def set_upstreamFractions(self,upstreamFractions):
        """"
        Sets the fractions of the mass flow that flow into this reach.
        Only matters if upstream reach has multiple outflows
        """
        self.upstreamFractions = upstreamFractions
