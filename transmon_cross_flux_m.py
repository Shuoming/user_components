# 2 flux pins inherented from TransmonCrossFL
"""Child of transmon cross, adds a flux line (galvanic T) to the arm with the
DC SQUID."""
# pylint: disable=invalid-name
# Modification of Transmon Pocket Object to include a charge line (would be better to just make as a child)

import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.user_components.transmon_cross_betterpin import TransmonCrossBetter


class TransmonCrossFLM(TransmonCrossBetter):  # pylint: disable=invalid-name
    """The base `TransmonCrossFLM` class.

    Inherits `TransmonCross` class

    Description:
        Simple Metal Transmon Cross object. Creates the X cross-shaped island,
        the "junction" on the south end, and up to 3 connectors on the remaining arms
        (claw or gap).

        'claw_width' and 'claw_gap' define the width/gap of the CPW line that
        makes up the connector. Note, DC SQUID currently represented by single
        inductance sheet

        Add connectors to it using the `connection_pads` dictonary. See BaseQubit for more
        information.

        Flux line is added by default to the 'south' arm where the DC SQUID is located,
        default is a symmetric T style

        Default Options:
        Convention: Values (unless noted) are strings with units included, (e.g., '30um')

        * make_fl -         (Boolean) If True, adds a flux line
        * t_top -           length of the flux line for mutual inductance to the SQUID
        * t_inductive_gap - amount of metallization between the flux line and SQUID
        * t_offset -        degree by which the tail of the T is offset from the center
        * t_width -         width of the flux line's transmission line center trace
        * t_gap -           dielectric gap of the flux line's transmission line

    .. image::
        transmon_cross_fl.png

    .. meta::
        Transmon Cross Flux Line

    """

    component_metadata = Dict(short_name='Q',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(make_fl=True,
                           fl_options=Dict(t_width_h='8um',
                                           t_gap_h='4um',
                                           t_l_h='20um',
                                           t_width_v='8um',
                                           t_gap_v='4um',
                                           t_l_v='20um',
                                           t_inductive_gap='2um',
                                           t_top='25um',
                                           t_offset='0um',
                                           ))
    """Default drawing options"""

    TOOLTIP = """The base `TransmonCrossFLM` class."""

    def make(self):
        """Define the way the options are turned into QGeometry."""
        super().make()

        if self.options.make_fl == True:
            self.make_flux_line()


#####################################################################


    def make_flux_line(self):
        """Creates the flux line if the user has flux line option to
        TRUE."""

        # Grab option values
        pf = self.p.fl_options
        p = self.p
        # Make the T flux line
        h_line = draw.LineString(
            [(-pf.t_l_h / 2, 0), (pf.t_l_h / 2, 0)])
        v_line = draw.LineString([(pf.t_l_h / 2-pf.t_width_v/2, -pf.t_width_h/2),
                                  (pf.t_l_h / 2-pf.t_width_v/2, -pf.t_width_h/2-pf.t_l_v/2)])
        top_line = draw.LineString(
            [(-pf.t_top / 2, pf.t_width_h/2+pf.t_gap_h/2), (pf.t_top / 2, pf.t_width_h/2+pf.t_gap_h/2)])
        connect_line = draw.LineString(
            [(float(pf.t_l_h / 2 + pf.t_gap_v / 2), -pf.t_width_h/2), (pf.t_l_h / 2 + pf.t_gap_v / 2, pf.t_width_h/2+pf.t_gap_h)])
        parts_temp = [h_line, v_line, connect_line]
        [h_line, v_line, connect_line] = draw.translate(
            parts_temp, pf.t_offset, 0, 0)
        parts = [h_line, v_line, top_line, connect_line]

        # Move the flux line down to the SQUID
        parts = draw.translate(
            parts, 0, -(p.cross_length + p.cross_gap + pf.t_inductive_gap +
                        pf.t_width_h / 2 + pf.t_gap_h))

        # Rotate and translate based on crossmon location
        parts = draw.rotate(parts, p.orientation, origin=(0, 0))
        parts = draw.translate(parts, p.pos_x, p.pos_y)

        [h_line, v_line, top_line, connect_line] = parts

        # Adding to qgeometry table
        self.add_qgeometry('path', {
            'h_line': h_line,
        },
            width=pf.t_width_h,
            layer=p.layer)

        self.add_qgeometry('path', {
            'h_line_sub': h_line,
        },
            width=pf.t_width_h + 2 * pf.t_gap_h,
            subtract=True,
            layer=p.layer)

        self.add_qgeometry('path', {
            'v_line': v_line,
        },
            width=pf.t_width_v,
            layer=p.layer)

        self.add_qgeometry('path', {
            'v_line_sub': v_line,
        },
            width=pf.t_width_v + 2 * pf.t_gap_v,
            subtract=True,
            layer=p.layer)
        self.add_qgeometry('path', {
            'top_line_sub': top_line,
        },
            width=pf.t_gap_h,
            subtract=True,
            layer=p.layer)
        self.add_qgeometry('path', {
            'coonect_line_sub': connect_line,
        },
            width=pf.t_gap_v,
            subtract=True,
            layer=p.layer)

        # Generating pin
        pin_line = v_line.coords
        self.add_pin("flux_line",
                     points=pin_line,
                     width=pf.t_width_v,
                     gap=pf.t_gap_v,
                     input_as_norm=True)
