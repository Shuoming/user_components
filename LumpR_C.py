from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class LumpRC(QComponent):
    """Crossover pad for bridge by asm"""
    component_metadata = Dict(short_name='LR',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(sub_width='500um',
                           sub_height='500um',
                           term_type='Open',  # or "Short"
                           width='10um', gap='6um', termination_gap='6um',
                           term_sub_gap='20um',
                           )
    """Default connector options"""

    TOOLTIP = """."""

    def make(self):
        """Build the component."""
        p = self.p
        sub_box = draw.rectangle(
            p.sub_width, p.sub_height)

        open_port_line = draw.translate(draw.LineString(
            [(0, -p.width / 2), (0, p.width / 2)]), p.sub_width/2-p.term_sub_gap, -p.sub_height/2+p.term_sub_gap)
        open_termination = draw.translate(draw.box(0, -(p.width / 2 + p.gap),
                                                   p.termination_gap, (p.width / 2 + p.gap)), p.sub_width/2-p.term_sub_gap, -p.sub_height/2+p.term_sub_gap)

        short_port_line = draw.translate(draw.LineString(
            [(0, -p.width / 2), (0, p.width / 2)]), p.sub_width/2, -p.sub_height/2+p.term_sub_gap)

        parts = [sub_box, open_port_line,
                 open_termination, short_port_line]

        parts = draw.rotate(parts, p.orientation, origin=(0, 0))
        parts = draw.translate(parts, 0, -p.sub_height/2)
        parts = draw.translate(parts, p.pos_x, p.pos_y)
        [sub_box, open_port_line,
            open_termination, short_port_line] = parts

        # Add to qgeometry tables
        self.add_qgeometry(
            'poly', {'box': sub_box}, layer=p.layer, subtract=True)
        if p.term_type == 'Open':
            self.add_qgeometry('poly', {'open_to_ground': open_termination},
                               subtract=True,
                               layer=p.layer)

        # Add pins
        if p.term_type == 'Open':
            self.add_pin('open', open_port_line.coords, p.width)
        elif p.term_type == 'Short':
            self.add_pin('short', list(
                draw.shapely.geometry.shape(short_port_line).coords), p.width)
        else:
            print('Wrong term typpes: "Open" or "Short"')
