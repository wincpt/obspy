# -*- coding: utf-8 -*-
"""
Keyhole Markup Language (KML) output support in ObsPy

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA

from math import log

from lxml.etree import Element, SubElement, tostring
from matplotlib.cm import get_cmap


def inventory_to_kml_string(
        inventory,
        icon_url="http://maps.google.com/mapfiles/kml/shapes/triangle.png",
        icon_size=1.5, label_size=1.0, cmap="Paired", encoding="UTF-8"):
    """
    Convert an :class:`~obspy.core.inventory.inventory.Inventory` to a kml
    string representation.

    :type inventory: :class:`~obspy.core.inventory.inventory.Inventory`
    :param inventory: Input station metadata.
    :type icon_url: str
    :param icon_url: Internet URL of icon to use for station (e.g. png image).
    :type icon_size: float
    :param icon_size: Icon size.
    :type label_size: float
    :param label_size: Label size.
    :type encoding: str
    :param encoding: Encoding used for XML string.
    :rtype: str
    :return: String containing KML information of the station metadata.
    """
    # construct the KML file
    kml = Element("kml")
    kml.set("xmlns", "http://www.opengis.net/kml/2.2")

    document = SubElement(kml, "Document")
    SubElement(document, "name").text = "Inventory"

    # style definition
    cmap = get_cmap(name=cmap, lut=len(inventory.networks))
    for i in range(len(inventory.networks)):
        color = _rgba_tuple_to_kml_color_code(cmap(i))
        style = SubElement(document, "Style")
        style.set("id", "station_%i" % i)

        iconstyle = SubElement(style, "IconStyle")
        SubElement(iconstyle, "color").text = color
        SubElement(iconstyle, "scale").text = str(icon_size)
        icon = SubElement(iconstyle, "Icon")
        SubElement(icon, "href").text = icon_url
        hotspot = SubElement(iconstyle, "hotSpot")
        hotspot.set("x", "0.5")
        hotspot.set("y", "0.5")
        hotspot.set("xunits", "fraction")
        hotspot.set("yunits", "fraction")

        labelstyle = SubElement(style, "LabelStyle")
        SubElement(labelstyle, "color").text = color
        SubElement(labelstyle, "scale").text = str(label_size)

    for i, net in enumerate(inventory):
        folder = SubElement(document, "Folder")
        SubElement(folder, "name").text = str(net.code)
        SubElement(folder, "open").text = "1"

        SubElement(folder, "description").text = str(net)

        style = SubElement(folder, "Style")
        liststyle = SubElement(style, "ListStyle")
        SubElement(liststyle, "listItemType").text = "check"
        SubElement(liststyle, "bgColor").text = "00ffff"
        SubElement(liststyle, "maxSnippetLines").text = "5"

        # add one marker per station code
        for sta in net:
            placemark = SubElement(folder, "Placemark")
            SubElement(placemark, "name").text = ".".join((net.code, sta.code))
            SubElement(placemark, "styleUrl").text = "#station_%i" % i
            SubElement(placemark, "color").text = color
            if sta.longitude is not None and sta.latitude is not None:
                point = SubElement(placemark, "Point")
                SubElement(point, "coordinates").text = "%.10f,%.10f,0" % \
                    (sta.longitude, sta.latitude)

            SubElement(placemark, "description").text = str(sta)

    # generate and return KML string
    return tostring(kml, pretty_print=True, xml_declaration=True,
                    encoding=encoding)


def catalog_to_kml_string(
        catalog,
        icon_url="http://maps.google.com/mapfiles/kml/shapes/earthquake.png",
        label_func=None, icon_size_func=None, encoding="UTF-8"):
    """
    Convert an :class:`~obspy.core.event.Catalog` to a kml string
    representation.

    :type catalog: :class:`~obspy.core.event.Catalog`
    :param catalog: Input catalog data.
    :type icon_url: str
    :param icon_url: Internet URL of icon to use for events (e.g. png image).
    :type label_func: func
    :type label_func: Custom function to use for determining each event's
        label. User provided function is supposed to take an
        :class:`~obspy.core.event.Event` object as single argument, e.g. for
        empty labels use `label_func=lambda x: ""`.
    :type icon_size_func: func
    :type icon_size_func: Custom function to use for determining each
        event's icon size. User provided function is supposed to take an
        :class:`~obspy.core.event.Event` object as single argument.
    :type encoding: str
    :param encoding: Encoding used for XML string.
    :rtype: str
    :return: String containing KML information of the event metadata.
    """
    # default label and size functions
    if not label_func:
        def label_func(event):
            origin = (event.preferred_origin() or
                      event.origins and event.origins[0] or
                      None)
            mag = (event.preferred_magnitude() or
                   event.magnitudes and event.magnitudes[0] or
                   None)
            label = origin.time and str(origin.time.date) or ""
            if mag:
                label += " %.1f" % mag.mag
            return label
    if not icon_size_func:
        def icon_size_func(event):
            mag = (event.preferred_magnitude() or
                   event.magnitudes and event.magnitudes[0] or
                   None)
            if mag:
                try:
                    icon_size = 1.2 * log(1.5 + mag.mag)
                except ValueError:
                    icon_size = 0.1
            else:
                icon_size = 0.5
            return icon_size

    # construct the KML file
    kml = Element("kml")
    kml.set("xmlns", "http://www.opengis.net/kml/2.2")

    document = SubElement(kml, "Document")
    SubElement(document, "name").text = "Catalog"

    # style definitions for earthquakes
    style = SubElement(document, "Style")
    style.set("id", "earthquake")

    iconstyle = SubElement(style, "IconStyle")
    SubElement(iconstyle, "scale").text = "0.5"
    icon = SubElement(iconstyle, "Icon")
    SubElement(icon, "href").text = icon_url
    hotspot = SubElement(iconstyle, "hotSpot")
    hotspot.set("x", "0.5")
    hotspot.set("y", "0.5")
    hotspot.set("xunits", "fraction")
    hotspot.set("yunits", "fraction")

    labelstyle = SubElement(style, "LabelStyle")
    SubElement(labelstyle, "color").text = "ff0000ff"
    SubElement(labelstyle, "scale").text = "0.8"

    folder = SubElement(document, "Folder")
    SubElement(folder, "name").text = "Catalog"
    SubElement(folder, "open").text = "1"

    SubElement(folder, "description").text = str(catalog)

    style = SubElement(folder, "Style")
    liststyle = SubElement(style, "ListStyle")
    SubElement(liststyle, "listItemType").text = "check"
    SubElement(liststyle, "bgColor").text = "00ffffff"
    SubElement(liststyle, "maxSnippetLines").text = "5"

    # add one marker per event
    for event in catalog:
        origin = (event.preferred_origin() or
                  event.origins and event.origins[0] or
                  None)

        placemark = SubElement(folder, "Placemark")
        SubElement(placemark, "name").text = label_func(event)
        SubElement(placemark, "styleUrl").text = "#earthquake"
        style = SubElement(placemark, "Style")
        icon_style = SubElement(style, "IconStyle")
        liststyle = SubElement(style, "ListStyle")
        SubElement(liststyle, "maxSnippetLines").text = "5"
        SubElement(icon_style, "scale").text = str(icon_size_func(event))
        if origin:
            if origin.longitude is not None and origin.latitude is not None:
                point = SubElement(placemark, "Point")
                SubElement(point, "coordinates").text = "%.10f,%.10f,0" % \
                    (origin.longitude, origin.latitude)

        SubElement(placemark, "description").text = str(event)

    # generate and return KML string
    return tostring(kml, pretty_print=True, xml_declaration=True,
                    encoding=encoding)


def _rgba_tuple_to_kml_color_code(rgba):
    """
    Convert tuple of (red, green, blue, alpha) float values (0.0-1.0) to KML
    hex color code string "aabbggrr".
    """
    try:
        r, g, b, a = rgba
    except:
        r, g, b = rgba
        a = 1.0
    return "".join([hex(int(x * 255))[-2:] for x in (a, b, g, r)])


if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
