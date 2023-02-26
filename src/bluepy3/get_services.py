#!/usr/bin/env python3

"""
Fetch UUIDs for characteristics, descriptors, formats, services and units from bluetooth.com
and store them in uuids.json for later use by `btle.py`

Note that the original tables from which the UUIDs were gathered nolonger exist.
Therefore, the archived webpages are used from archive.com
"""

import errno
import os
import tempfile

import requests
from bs4 import BeautifulSoup

URL_CHARACTERISTICS = "https://web.archive.org/web/20170201044907/https://www.bluetooth.com/specifications/gatt/characteristics"
URL_DESCRIPTORS = "https://web.archive.org/web/20170201043201/https://www.bluetooth.com/specifications/gatt/descriptors"
URL_FORMATS = "https://web.archive.org/web/20160410055350/https://developer.bluetooth.org/gatt/Pages/FormatTypes.aspx"
URL_SERVICES = "https://web.archive.org/web/20170711074819/https://www.bluetooth.com/specifications/gatt/services"
URL_UNITS = "https://web.archive.org/web/20160305020847/https://developer.bluetooth.org/gatt/units/Pages/default.aspx"

DEBUG = True


def get_html(url: str, local_filename: str) -> object:
    """Fetch a URL and store it in a local tempfile

    Args:
        url (str): URL of webpage to fetch
        local_filename: location where to store the webpage

    Returns:
        object: content of webpage
    """
    cachedir = os.path.join(tempfile.gettempdir(), "bluepy3")
    try:
        os.mkdir(cachedir)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    cachefilename = os.path.join(cachedir, local_filename)

    try:
        html = open(cachefilename, 'r').read()
    except:
        html = requests.get(url).content
        open(cachefilename, "wb").write(html)
    return html


def get_table_rows(html=None):
    if html is None:
        html = get_html()

    soup = BeautifulSoup(html)

    tables = soup.find_all("table")

    biggest_table = max(tables, key=len)

    # service_table=soup.find("table", attrs={"summary":"Documents This library contains Services."})

    assert biggest_table

    for row in biggest_table.find_all("tr"):
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        outrow = [ele for ele in cols if ele]  # Get rid of empty values
        if outrow:
            yield outrow


def get_table(url, local_filename, table_defs):
    """Grabs the largest table from a webpage.

    table_defs is a list of column name, interpretation function.
    """
    html = get_html(url, local_filename)
    for row in get_table_rows(html):
        if DEBUG:
            print(f"got {row}")
        try:
            assert len(row) == len(table_defs)

        ret = {}
        for col, (name, func) in zip(row, table_defs):
            try:
                if func is None:

                    def func(x):
                        return x

                ret[name] = func(col)
            except:
                print(name)
                print(col)
                print(row)
                raise
        yield ret


def get_service_names():
    if DEBUG:
        print("\nservices")
    for row in get_table(
        "https://web.archive.org/web/20160318231314/https://developer.bluetooth.org/gatt/services/Pages/ServicesHome.aspx",
        "services.html",
        (
            ("Name", None),
            ("Type", None),
            ("Number", lambda x: int(x, 16)),
            ("Level", None),
        ),
    ):
        if DEBUG:
            # example:
            # row {'Name': 'Weight Scale', 'Type': 'org.bluetooth.service.weight_scale', 'Number': 6173, 'Level': 'Adopted'}
            print(f"row {row}")
        row["cname"] = row["Type"].split(".")[-1]
        yield row


def get_descriptors():
    if DEBUG:
        print("\ndescriptors")
    for row in get_table(
        "https://web.archive.org/web/20160318161646/https://developer.bluetooth.org/gatt/descriptors/Pages/DescriptorsHomePage.aspx",
        "descriptors.html",
        (
            ("Name", None),
            ("Type", None),
            ("Number", lambda x: int(x, 16)),
            ("Level", None),
        ),
    ):
        if DEBUG:
            # example
            # row {'Name': 'Value Trigger Setting', 'Type': 'org.bluetooth.descriptor.value_trigger_setting', 'Number': 10506, 'Level': 'Adopted'}
            print(f"row {row}")
        row["cname"] = row["Type"].split(".")[-1]
        yield row


def get_characteristics():
    if DEBUG:
        print("\ncharacteristics")
    for row in get_table(
        "https://web.archive.org/web/20160318225546/https://developer.bluetooth.org/gatt/characteristics/Pages/CharacteristicsHome.aspx",
        "characteristics.html",
        (
            ("Name", None),
            ("Type", None),
            ("Number", lambda x: int(x, 16)),
            ("Level", None),
        ),
    ):
        if DEBUG:
            # example:
            # row {'Name': 'Wind Chill', 'Type': 'org.bluetooth.characteristic.wind_chill', 'Number': 10873, 'Level': 'Adopted'}
            print(f"row {row}")
        row["cname"] = row["Type"].split(".")[-1]
        yield row


def get_units():
    if DEBUG:
        print("\nunits")
    for row in get_table(
        "https://web.archive.org/web/20160305020847/https://developer.bluetooth.org/gatt/units/Pages/default.aspx",
        "units.html",
        (("Number", lambda x: int(x, 16)), ("Name", None), ("Type", None)),
    ):
        if DEBUG:
            # example:
            # {'Number': 10168, 'Name': 'mass (pound)', 'Type': 'org.bluetooth.unit.mass.pound'}
            print(row)
        row["cname"] = row["Type"].split(".")[-1]
        yield row


def get_formats():
    if DEBUG:
        print("\nformats")
    for row in get_table(
        "https://web.archive.org/web/20160410055350/https://developer.bluetooth.org/gatt/Pages/FormatTypes.aspx",
        "formats.html",
        (("Name", None), ("Description", None)),
    ):
        if DEBUG:
            # example:
            # row {'Name': 'float64', 'Description': 'IEEE-754 64-bit floating point'}
            print(f"row {row}")
        row["cname"] = row["Name"]
        yield row


class Definitions(object):
    def __init__(self):
        self._characteristics = None
        self._units = None
        self._services = None
        self._descriptors = None
        self._formats = None

    @property
    def characteristics(self):
        if not self._characteristics:
            self._characteristics = list(get_characteristics())
        return self._characteristics

    @property
    def units(self):
        if not self._units:
            self._units = list(get_units())
        return self._units

    @property
    def services(self):
        if not self._services:
            self._services = list(get_service_names())
        return self._services

    @property
    def descriptors(self):
        if not self._descriptors:
            self._descriptors = list(get_descriptors())
        return self._descriptors

    @property
    def formats(self):
        if not self._formats:
            self._formats = list(get_formats())
        return self._formats

    def data(self):
        """
        Makes tables like this:
        number, name, common name.
        """
        return {
            "characteristic_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.characteristics],
            "service_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.services],
            "descriptor_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.descriptors],
            "units_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.units],
            "formats": [(row["Name"], row["Description"]) for row in self.formats],
        }


    def data_debug(self):
        """ FOR DEVBUGGING ONLY
        Makes tables like this:
        number, name, common name.
        """
        return {
            # Units = OK
            # "units_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.units],
            # Formats = OK
            # "formats": [(row["Name"], row["Description"]) for row in self.formats],
            # Characteristics = OK
            # "characteristic_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.characteristics],
            # "service_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.services],
            "descriptor_UUIDs": [(row["Number"], row["cname"], row["Name"]) for row in self.descriptors],
        }


if __name__ == "__main__":
    d = Definitions()

    import json

    print(json.dumps(d.data(), indent=4, sort_keys=True))
