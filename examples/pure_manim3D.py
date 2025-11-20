from manim import *
import math
import matplotlib.pyplot as plt
from colormap import rgb2hex
import pylab as pl
import geopandas as gpd
import numpy as np  # needed for np.array, np.radians, etc.

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world = world.explode('geometry')  # need this to extract all polygon when there is a multipart geometry

cmap = plt.get_cmap('viridis')
norm = plt.Normalize(
    world['pop_est'].min(),
    10**8.5
)

### Create Colorbar to add it to the scene
a = np.array([[0, 1]])
pl.figure(figsize=(1, 4))
img = pl.imshow(a, cmap="viridis")
pl.gca().set_visible(False)
cax = pl.axes([0.1, 0.2, 0.35, 0.6])
pl.colorbar(orientation="vertical", cax=cax)

cax.set_yticks([0, 1])
mod_ticklabels = ["0", ">1B"]

cax.set_yticklabels(mod_ticklabels, color='black', fontsize=13)
pl.tight_layout()
pl.savefig(
    r"colorbar_world_vertical.png",
    transparent=True,
    bbox_inches='tight',
    dpi=200
)


class Earth3DScene(ThreeDScene):
    def construct(self):

        self.camera.background_color = WHITE
        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-200, 200],  # Longitude (theta) range
            y_range=[-100, 100],  # Latitude (phi) range
            z_range=[0, 1],       # Radius (r) range (scaled to fit within [0, 1])
        )

        ### This part loops over the country, extract polygon boundary,
        ### and add the polygon to axes
        twoD_vgroup = VGroup()
        threeD_vgroup = VGroup()
        for row in world.itertuples():
            polygon_coords = np.array(
                world[world['name'] == row.name].geometry.values[0].exterior.coords
            )
            projected_points = [
                self.spherical_projection(lat, lon) for lon, lat in polygon_coords
            ]
            color = cmap(norm(row.pop_est))
            hex_color = rgb2hex(*color)

            points = axes.coords_to_point(polygon_coords)
            area = Polygon(
                *points,
                fill_opacity=1,
                color=hex_color,
                stroke_width=1
            )

            twoD_vgroup.add(area)
            polygon = Polygon(
                *projected_points,
                color=hex_color,
                fill_opacity=1,
                stroke_width=0.5
            )
            threeD_vgroup.add(polygon)

        #         except:
        #             print(f"{row.name} encountered issues")
        #             pass
        title = Text(
            "World Population Size by Country",
            font_size=25,
            color=BLACK
        )
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.add_fixed_in_frame_mobjects(title)

        colorbar = ImageMobject(r"colorbar_world_vertical.png")
        colorbar.scale(1.5).to_edge(RIGHT)
        self.add_fixed_in_frame_mobjects(colorbar)

        twoD_vgroup.scale(.7)

        self.play(Create(twoD_vgroup, run_time=1))
        self.wait(0.5)

        # Create a sphere representing the Earth
        earth = Sphere(
            radius=1,
            resolution=20,
            # color=WHITE
        )
        earth.set_color(BLUE)

        # Adjust camera orientation
        # self.set_camera_orientation(phi=np.mean(lats) * DEGREES, theta=np.mean(lons) * DEGREES)
        self.set_camera_orientation(
            phi=60 * DEGREES,     # Adjust for latitude
            theta=-102 * DEGREES  # Adjust for longitude
        )

        self.play(
            ReplacementTransform(twoD_vgroup, threeD_vgroup.scale(3)),
            runtime=30
        )
        # self.play(Create(earth.scale(3)), run_time=2)
        self.add(earth.scale(3))

        # self.play(earth.scale(5), runtime=1)
        # self.play(Create(vgroup.scale(3)), runtime=10)

        self.begin_ambient_camera_rotation(rate=0.1, about='theta')
        self.wait(30)

        self.stop_ambient_camera_rotation(about='theta')

    def spherical_projection(self, lat, lon):
        """Projects geographic coordinates onto a unit sphere."""
        theta = np.radians(lon)  # Convert longitude to radians
        phi = np.radians(lat)    # Convert latitude to radians

        x = np.cos(phi) * np.cos(theta)
        y = np.cos(phi) * np.sin(theta)
        z = np.sin(phi)

        return np.array([x, y, z])