from qiskit_metal import draw
from qiskit_metal.toolbox_python.attr_dict import Dict
from qiskit_metal.qlibrary.core import QComponent

# Define class and options for the launch geometry


class Taper(QComponent):
    """
    """

    default_options = Dict(up_width='20um',
                           up_gap='10um',
                           low_width='8um',
                           low_gap='4um',
                           height='20um')
    """Default options"""

    TOOLTIP = """"""

    def make(self):
        """This is executed by the user to generate the qgeometry for the
        component."""

        p = self.p
        #########################################################

        # Geometry of main structure
        # The shape is a polygon and we prepare this point as orientation is 0 degree
        taper_pad = draw.Polygon([
            (-p.low_width/2, -p.height/2),
            (-p.up_width/2, p.height/2),
            (p.up_width/2, p.height/2),
            (p.low_width/2, -p.height/2),
            (-p.low_width/2, -p.height/2),
        ])

        taper_pocket = draw.Polygon([
            (-(p.low_width+2*p.low_gap)/2, -p.height/2),
            (-(p.up_width+2*p.up_gap)/2, p.height/2),
            ((p.up_width+2*p.up_gap)/2, p.height/2),
            ((p.low_width+2*p.low_gap)/2, -p.height/2),
            (-(p.low_width+2*p.low_gap)/2, -p.height/2),
        ])

        # These variables are used to graphically locate the pin locations
        pin_line = draw.LineString([( 0,-p.height/2),
                                    ( 0,p.height/2)])

        # Create polygon object list
        polys1 = [pin_line, taper_pad, taper_pocket]

        # Rotates and translates all the objects as requested. Uses package functions in
        # 'draw_utility' for easy rotation/translation
        polys1 = draw.rotate(polys1, p.orientation, origin=(0, 0))
        polys1 = draw.translate(polys1, xoff=p.pos_x, yoff=p.pos_y)
        [pin_line, taper_pad, taper_pocket] = polys1

        # Adds the object to the qgeometry table
        self.add_qgeometry('poly', dict(launch_pad=taper_pad), layer=p.layer)

        # Subtracts out ground plane on the layer its on
        self.add_qgeometry('poly',
                           dict(pocket=taper_pocket),
                           subtract=True,
                           layer=p.layer)

        # Generates the pins
        self.add_pin('tie_up', pin_line.coords, p.up_width, input_as_norm = True)
        self.add_pin(
            'tie_down', pin_line.coords[::-1], p.low_width, input_as_norm=True)
