from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class BCross(QComponent):
    """Crossover pad for bridge by asm"""
    component_metadata = Dict(short_name='bcross',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(prime_width='10um',
                           prime_height='10um',
                           prime_gap='20um',
                           pad_gap='4um',
                           cpw_width='8um',
                           cpw_gap='4um',
                           cpw_length='10um',
                           left_cpw = False,
                           left_cpw_width='20um',
                           left_cpw_gap='10um',)
    """Default connector options"""

    TOOLTIP = """."""

    def make(self):
        """Build the component."""
        p = self.p
        prime_box = draw.rectangle(
            p.prime_width, p.prime_height)
        pad_box = draw.rectangle(
            p.prime_width-2*p.pad_gap, p.prime_height-2*p.pad_gap)
        cpw_line = draw.LineString([[p.prime_width/2-p.pad_gap, 0],
                                    [p.prime_width/2-p.pad_gap+p.cpw_length, 0]])
        parts = [prime_box, pad_box, cpw_line]
        [prime_box, pad_box, cpw_line] = draw.translate(
            parts, (p.prime_gap+p.prime_width)/2, 0, 0)
        first_parts = [prime_box, pad_box, cpw_line]
        [prime_box_second, pad_box_second, cpw_line_second] = draw.rotate(
            first_parts, 180.0, origin=(0, 0))

        parts = [prime_box, pad_box, cpw_line,
                 prime_box_second, pad_box_second, cpw_line_second]
        parts = draw.rotate(parts, p.orientation, origin=(0, 0))
        parts = draw.translate(parts, p.pos_x, p.pos_y)
        [prime_box, pad_box, cpw_line,
                 prime_box_second, pad_box_second, cpw_line_second] = parts

        # Add to qgeometry tables
        self.add_qgeometry('path', {'prime_cpw': cpw_line},
                           width=p.cpw_width,
                           layer=p.layer)
        self.add_qgeometry('path', {'prime_cpw_sub': cpw_line},
                           width=p.cpw_width + 2 * p.cpw_gap,
                           subtract=True,
                           layer=p.layer)
        if p.left_cpw == True:
            self.add_qgeometry('path', {'second_cpw': cpw_line_second},
                           width=p.left_cpw_width,
                           layer=p.layer)
            self.add_qgeometry('path', {'second_cpw_sub': cpw_line_second},
                           width=p.left_cpw_width + 2 * p.left_cpw_gap,
                           subtract=True,
                           layer=p.layer)
        else:
            self.add_qgeometry('path', {'second_cpw': cpw_line_second},
                            width=p.cpw_width,
                            layer=p.layer)
            self.add_qgeometry('path', {'second_cpw_sub': cpw_line_second},
                            width=p.cpw_width + 2 * p.cpw_gap,
                            subtract=True,
                            layer=p.layer)

        self.add_qgeometry(
            'poly', {'prime_box': prime_box}, layer=p.layer, subtract=True)
        self.add_qgeometry('poly', {'pad_box': pad_box}, layer=p.layer)

        self.add_qgeometry(
            'poly', {'prime_box_second': prime_box_second}, layer=p.layer, subtract=True)
        self.add_qgeometry(
            'poly', {'pad_box_second': pad_box_second}, layer=p.layer)

        # Add pins
        prime_pin_list = cpw_line.coords
        second_pin_list = cpw_line_second.coords

        self.add_pin('start',
                     points=np.array(prime_pin_list),
                     width=p.cpw_width,
                     input_as_norm=True)
        self.add_pin('end',
                     points=np.array(second_pin_list),
                     width=p.cpw_width,
                     input_as_norm=True)
