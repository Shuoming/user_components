from this import d
import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit
from qiskit_metal.draw.basic import subtract


class TransmonCrossBetterI(BaseQubit):  # pylint: disable=invalid-name
    """The base `TransmonCrossBetter` class.

    Inherits `BaseQubit` class.

    Simple Metal Transmon Cross object. Creates the X cross-shaped island,
    the "junction" on the south end, and up to 3 connectors on the remaining arms
    (claw or gap).

    'claw_width' and 'claw_gap' define the width/gap of the CPW line that
    makes up the connector. Note, DC SQUID currently represented by single
    inductance sheet

    Add connectors to it using the `connection_pads` dictionary. See BaseQubit for more
    information.

    Sketch:
        Below is a sketch of the qubit
        ::

                                        claw_length
            Claw:       _________                    Gap:
                        |   ________________             _________    ____________
                  ______|  |                             _________|  |____________
                        |  |________________
                        |_________


    .. image::
        transmon_cross.png

    .. meta::
        Transmon Cross

    BaseQubit Default Options:
        * connection_pads: Empty Dict -- The dictionary which contains all active connection lines for the qubit.
        * _default_connection_pads: empty Dict -- The default values for the (if any) connection lines of the qubit.

    Default Options:
        * cross_width: '20um' -- Width of the CPW center trace making up the Crossmon
        * cross_length: '200um' -- Length of one Crossmon arm (from center)
        * cross_gap: '20um' -- Width of the CPW gap making up the Crossmon
        * _default_connection_pads: Dict
            * connector_type: '0' -- 0 = Claw type, 1 = gap type
            * claw_length: '30um' -- Length of the claw 'arms', measured from the connector center trace
            * ground_spacing: '5um' -- Amount of ground plane between the connector and Crossmon arm (minimum should be based on fabrication capabilities)
            * claw_width: '10um' -- The width of the CPW center trace making up the claw/gap connector
            * claw_gap: '6um' -- The gap of the CPW center trace making up the claw/gap connector
            * connector_location: '0' -- 0 => 'west' arm, 90 => 'north' arm, 180 => 'east' arm
    """

    default_options = Dict(
        cross_width='20um',
        cross_length='200um',
        cross_gap='20um',
        tr='10',
        no_cap=False,
        thiner_gap='4um',
        thiner_location='0',  # 0 => 'west' arm, 90 => 'north' arm, 180 => 'east' arm
        chip='main',
        _default_connection_pads=Dict(
            connector_type='0',  # 0 = Claw type, 1 = gap type
            claw_length='30um',
            ground_spacing='5um',
            claw_width='10um',
            claw_gap='6um',
            connector_location='0',  # 0 => 'west' arm, 90 => 'north' arm, 180 => 'east' arm
            connector_width='8um',
            connector_gap='4um',
            drive_gap=False,
            thiner_cross=True,
            claw_gi='20um',
        ))
    """Default options."""

    component_metadata = Dict(short_name='Cross',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_junction='True')
    """Component metadata"""

    TOOLTIP = """Simple Metal Transmon Cross."""

    ############################################## MAKE######################################################

    def make(self):
        """This is executed by the GUI/user to generate the qgeometry for the
        component."""
        self.make_pocket()
        self.make_connection_pads()

################################### TRANSMON#############################################################

    def make_pocket(self):
        """Makes a basic Crossmon, 4 arm cross."""

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p

        cross_width = p.cross_width
        cross_length = p.cross_length
        cross_gap = p.cross_gap
        thiner_gap = p.thiner_gap
        thiner_location = p.thiner_location
        tr = p.tr
        np = p.no_cap

        # access to chip name
        chip = p.chip

        # Creates the cross and the etch equivalent.

        cross_line = draw.shapely.ops.unary_union([
            draw.LineString([(0, 0), (0, -cross_length/tr)]),
            draw.LineString([(cross_length, 0), (-cross_length, 0)])
        ])
        cross = cross_line.buffer(cross_width / 2, cap_style=2)
        cross_etch_main = cross.buffer(cross_gap, cap_style=3, join_style=2)
        t1 = draw.box(
            -(cross_width/2+cross_gap),
            (cross_width/2+cross_gap),
            -(cross_width/2+thiner_gap),
            cross_length+cross_gap)
        t2 = draw.box(
            (cross_width / 2+thiner_gap),
            (cross_width / 2+cross_gap),
            (cross_width / 2+cross_gap),
            cross_length+cross_gap)
        t3 = draw.box(
            -(cross_width/2+cross_gap),
            cross_length+thiner_gap,
            cross_width/2+cross_gap,
            cross_length+cross_gap,
        )
        # 0 => 'west' arm, 90 => 'north' arm, 180 => 'east' arm
        t1 = draw.rotate(t1, thiner_location-90, origin=(0, 0))
        t2 = draw.rotate(t2, thiner_location-90, origin=(0, 0))
        t3 = draw.rotate(t3, thiner_location-90, origin=(0, 0))
        t4 = draw.rotate(t1, thiner_location+180, origin=(0, 0))
        t5 = draw.rotate(t2, thiner_location+180, origin=(0, 0))
        t6 = draw.rotate(t3, thiner_location+180, origin=(0, 0))

        cross_etch_1 = subtract(cross_etch_main, t1)
        cross_etch_2 = subtract(cross_etch_1, t2)
        cross_etch_3 = subtract(cross_etch_2, t3)
        cross_etch_4 = subtract(cross_etch_3, t4)
        cross_etch_5 = subtract(cross_etch_4, t5)
        cross_etch_6 = subtract(cross_etch_5, t6)
        cross_etch = cross_etch_6
        # The junction/SQUID
        rect_jj = draw.LineString([(0, -cross_width/2),
                                   (0, -cross_width/2 - cross_gap)])

        #rotate and translate
        if not np:
            cross_0 = cross
        else:
            cap1 = draw.box(cross_length, -cross_width/2,
                            cross_length+thiner_gap, cross_width/2)
            cap2 = draw.box(-(cross_length+thiner_gap), -
                            cross_width/2, -cross_length, cross_width/2)
            cross_0 = draw.shapely.ops.unary_union([cross, cap1, cap2])

        polys = [cross_0, cross_etch, rect_jj]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)

        [cross, cross_etch, rect_jj] = polys

        # generate qgeometry
        self.add_qgeometry('poly', dict(cross=cross), chip=chip)
        self.add_qgeometry('poly',
                           dict(cross_etch=cross_etch),
                           subtract=True,
                           chip=chip)
        self.add_qgeometry('junction',
                           dict(rect_jj=rect_jj),
                           width=cross_width,
                           chip=chip)


############################ CONNECTORS##################################################################################################


    def make_connection_pads(self):
        """Goes through connector pads and makes each one."""
        for name in self.options.connection_pads:
            self.make_connection_pad(name)

    def make_connection_pad(self, name: str):
        """Makes individual connector pad.

        Args:
            name (str) : Name of the connector pad
        """

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p
        cross_width = p.cross_width
        cross_length = p.cross_length
        cg = p.cross_gap
        tg = p.thiner_gap
        # access to chip name
        chip = p.chip

        pc = self.p.connection_pads[name]  # parser on connector options
        c_g = pc.claw_gap
        c_l = pc.claw_length
        c_w = pc.claw_width
        g_s = pc.ground_spacing
        con_loc = pc.connector_location
        d_g = pc.drive_gap
        tc = pc.thiner_cross
        gi = pc.claw_gi

        cn_w = pc.connector_width
        cn_g = pc.connector_gap
        n = 10
        claw_cpw = draw.box(0, -cn_w / 2, -n * cn_w, cn_w / 2)

        if pc.connector_type == 0:  # Claw connector
            if not tc:
                cross_gap = cg
            else:
                cross_gap = tg
            t_claw_height = 2*c_g + 2 * c_w + 2*g_s + \
                2*cross_gap + cross_width  # temp value
            claw_base = draw.box(-c_w, -(t_claw_height) / 2, c_l,
                                 t_claw_height / 2)
            claw_subtract = draw.box(0, -t_claw_height / 2 + c_w, c_l,
                                     t_claw_height / 2 - c_w)
            claw_base = claw_base.difference(claw_subtract)

            connector_arm = draw.shapely.ops.unary_union(
                [claw_base, claw_cpw])
            if d_g:
                claw_cpw_e = draw.box(0, -(cn_w+2*(cn_g-c_g)) /
                                      2, -n * cn_w, (cn_w+2*(cn_g-c_g)) / 2)
            else:
                claw_cpw_e = draw.box(0, -(cn_w+2*(cn_g-c_g)) /
                                      2, -n * cn_w + c_g, (cn_w+2*(cn_g-c_g)) / 2)
            connector_arm_e = draw.shapely.ops.unary_union(
                [claw_base, claw_cpw_e])
            connector_etcher_0 = draw.buffer(connector_arm_e, c_g)

            claw_gt1 = draw.box(-c_w-c_g, t_claw_height / 2+c_g, c_l+c_g,
                                t_claw_height / 2+gi)
            claw_gt2 = draw.box(-c_w-c_g, -(t_claw_height / 2+gi), c_l+c_g,
                                -(t_claw_height / 2+c_g))
            connector_etcher_1 = draw.shapely.ops.unary_union(
                [connector_etcher_0, claw_gt1])
            connector_etcher_2 = draw.shapely.ops.unary_union(
                [connector_etcher_1, claw_gt2])
            connector_etcher = connector_etcher_2

        else:
            connector_arm = claw_cpw
            if d_g:
                connector_etcher = draw.buffer(
                    connector_arm, cn_g)
            else:
                connector_etcher = draw.buffer(
                    draw.box(0, -cn_w / 2, -n * cn_w+cn_g, cn_w / 2), cn_g)

        # Making the pin for  tracking (for easy connect functions).
        # Done here so as to have the same translations and rotations as the connector. Could
        # extract from the connector later, but since allowing different connector types,
        # this seems more straightforward.

        port_line = draw.LineString(
            [(-n * cn_w, -cn_w / 2), (-n * cn_w, cn_w / 2)])

        claw_rotate = 0
        if con_loc > 135:
            claw_rotate = 180
        elif con_loc > 45:
            claw_rotate = -90

        # Rotates and translates the connector polygons (and temporary port_line)
        polys = [connector_arm, connector_etcher, port_line]
        if pc.connector_type == 0:
            if not tc:
                cross_gap = cg
            else:
                cross_gap = tg
        else:
            cross_gap = cg
        polys = draw.translate(polys, -(cross_length + cross_gap + g_s + c_g),
                               0)
        polys = draw.rotate(polys, claw_rotate, origin=(0, 0))
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [connector_arm, connector_etcher, port_line] = polys

        # Generates qgeometry for the connector pads
        self.add_qgeometry('poly', {f'{name}_connector_arm': connector_arm},
                           chip=chip)
        self.add_qgeometry('poly',
                           {f'{name}_connector_etcher': connector_etcher},
                           subtract=True,
                           chip=chip)

        self.add_pin(name, port_line.coords, c_w)
