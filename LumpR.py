from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

class LumpR(QComponent):
    """Crossover pad for bridge by asm"""
    component_metadata = Dict(short_name='LR',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(sub_width='100um',
                           sub_height='100um',
                           cpw_width='8um',
                           cpw_gap='4um',
                           cpw_length='10um')
    """Default connector options"""

    TOOLTIP = """."""

    def make(self):
        """Build the component."""
        p = self.p
        sub_box = draw.rectangle(
            p.sub_width, p.sub_height)
        cpw_line = draw.LineString([[0, p.sub_height/2],
                                    [0, p.sub_height/2+p.cpw_length]])

        parts = [sub_box, cpw_line]
        parts = draw.rotate(parts, p.orientation, origin=(0, 0))
        parts = draw.translate(parts, p.pos_x, p.pos_y)
        [sub_box, cpw_line] = parts

        # Add to qgeometry tables
        self.add_qgeometry('path', {'cpw': cpw_line},
                           width=p.cpw_width,
                           layer=p.layer)
        self.add_qgeometry('path', {'cpw_sub': cpw_line},
                           width=p.cpw_width + 2 * p.cpw_gap,
                           subtract=True,
                           layer=p.layer)
        self.add_qgeometry(
            'poly', {'box': sub_box}, layer=p.layer, subtract=True)

        # Add pins
        prime_pin_list = cpw_line.coords

        self.add_pin('tie_1',
                     points=np.array(prime_pin_list),
                     width=p.cpw_width,
                     input_as_norm=True)
        self.add_pin('tie_2',
                points=np.array(prime_pin_list[::-1]),
                width=p.cpw_width,
                input_as_norm=True)
