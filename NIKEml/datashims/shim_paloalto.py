import json
import sys, os, re
import pandas as pd
from NIKEml.datashims.apiShimBaseClass import apiShim
from pandevice import base, firewall, panorama, policies, objects, network, device
from netaddr import IPNetwork, IPAddress
from NIKEutil.logger import logger


class dataShim(apiShim):
    PASSWORD = "VwxgUT91F2YBCQlr9Zht"
    __dataSet = pd.DataFrame()

    @property
    def dataSet(self):
        return self.__dataSet

    def __init__(self):
        pass

    def loadData(self):
        self.connect_and_pull()

    def connect_and_pull(self):
        sNets = []
        auth = ("10.128.148.128", "cis_stm_ngfw_api",  self.PASSWORD)
        pano = base.PanDevice.create_from_device(*auth)
        l_TS = panorama.Template.refreshall(pano, add=True)
        for TS in l_TS:
            n_TS = TS.name
            l_Zn = TS.findall(network.Zone, recursive=True)
            for ZN in l_Zn:
                l_ZN_int = ZN.interface
                for counter, ZN_int in enumerate(l_ZN_int):
                    l_AI = TS.findall(network.AggregateInterface, recursive=True)
                    for AI in l_AI:
                        l_nIF = AI.findall(network.Layer3Subinterface, recursive=True)
                        for nIF in l_nIF:
                            if nIF.name == ZN_int:
                                if nIF.ip:
                                    for sIP in nIF.ip:
                                        d_row = [n_TS, ZN.name, sIP]
                                        sNets.append([n_TS, ZN.name, sIP])
                                else:
                                    sNets.append([n_TS, ZN.name, 'None'])

        self.__dataSet = pd.DataFrame(sNets, columns=['Location', 'Zone', 'Subnet'])

    def get_subnet(self, IP):
        found = False
        subnets = []
        for index, row in self.df.iterrows():
            if IPAddress(IP) in IPNetwork(row["Subnet"]):
                found = True
                subnets.append(row["Subnet"])
        return subnets

    def get_zone(self, IP):
        found = False
        zones = []
        for index, row in self.df.iterrows():
            if IPAddress(IP) in IPNetwork(row["Subnet"]):
                found = True
                zones.append(row["Zone"])
        return zones

    def get_location(self, IP):
        found = False
        locations = []
        for index, row in self.df.iterrows():
            if IPAddress(IP) in IPNetwork(row["Subnet"]):
                found = True
                locations.append(row["Location"])
        return locations

    def get_accessability(self, IP):
        found = False
        access = False
        for index, row in self.df.iterrows():
            if IPAddress(IP) in IPNetwork(row["Subnet"]):
                found = True
                if "EXT" in row["Zone"] or "DMZ" in row["Zone"]:
                    access = "External"
                else:
                    access = "Internal"
        return access

    def get_row(self, IP):
        found = False
        rowData = False
        for index, row in self.df.iterrows():
            if IPAddress(IP) in IPNetwork(row["Subnet"]):
                found = True
                rowData = row
        return rowData

    def get_all_zones(self):
        return self.df

    def get_record(ipAddress):
        paloAltoDetails = dict()
        paloAltoDetails["Subnet"] = self.get_subnet(ipAddress)
        paloAltoDetails["Zone"] = self.get_zone(ipAddress)
        paloAltoDetails["Location"] = self.get_location(ipAddress)
        paloAltoDetails["Access"] = self.get_accessability(ipAddress)
        return paloAltoDetails


if __name__ == '__main__':
    test = dataShim()
    dataShim.loadData(test)

