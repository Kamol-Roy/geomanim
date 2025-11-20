# Full code
import geopandas as gpd
import matplotlib.pyplot as plt
from manim import *
from colormap import rgb2hex
import numpy as np  # needed for np.array

us_population_2017 = gpd.read_file(
    "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/"
    "USA_States_Generalized/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
)
relevant_columns = ['STATE_NAME', 'POPULATION', 'POP_SQMI', 'geometry']
# us_population_2017[relevant_columns].head()

us_population_2017 = us_population_2017.explode()

us_population_2017 = us_population_2017[
    ~us_population_2017['STATE_NAME'].isin(['Alaska', 'Hawaii'])
]
us_population_2017 = us_population_2017.sort_values(by='POP_SQMI', ascending=False)

cmap = plt.get_cmap('viridis')
norm = plt.Normalize(us_population_2017['POP_SQMI'].min(), 500)


def get_line_coord(linestring):
    border_xy = np.array(linestring.boundary.coords)
    return border_xy


def get_line_and_area(axes, border_xy, pop):
    color = cmap(norm(pop))
    hex_color = rgb2hex(*color)
    line = axes.plot_line_graph(
        border_xy[:, 0],
        border_xy[:, 1],
        add_vertex_dots=False,
        line_color=BLACK,
        stroke_width=1
    )
    points = axes.coords_to_point(border_xy)
    area = Polygon(
        *points,
        fill_opacity=0.5,
        color=hex_color,
        stroke_width=1
    )
    dist_center = area.get_center()

    # line.to_edge(UR)
    # area.to_edge(UR)
    return line, area, dist_center


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

exploded_usa = world[world['iso_a3'] == 'USA'].explode()  # to convert multipolygon to polygon
exploded_usa['part'] = [f'part_{i}' for i in range(len(exploded_usa))]
# exploded_usa.explore(column='part')

polygon = exploded_usa[exploded_usa['part'] == 'part_0'].geometry.values[0]  # excluding Alaska and Hawai
# extract the coordinates
polygon_border_xy = np.array(polygon.boundary.coords)


class Animate_population_density(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # set up Manim Axis
        axes = Axes(
            x_range=[min(polygon_border_xy[:, 0]) - 2.5,
                     max(polygon_border_xy[:, 0]) + 2.5],
            y_range=[min(polygon_border_xy[:, 1]),
                     max(polygon_border_xy[:, 1])],
            axis_config={"color": BLUE},
        )
        boundary_line = axes.plot_line_graph(
            polygon_border_xy[:, 0],
            polygon_border_xy[:, 1],
            add_vertex_dots=False,
            line_color=BLACK,
            stroke_width=5
        )
        # bd_line.move_to(LEFT*3)
        self.play(Create(boundary_line, run_time=1))
        self.wait(0.5)

        for state in us_population_2017['STATE_NAME'].unique():
            state_df = us_population_2017[us_population_2017['STATE_NAME'] == state]

            if len(state_df) > 1:

                states_line_group = VGroup()
                state_area_group = VGroup()

                for row in state_df.itertuples():
                    geometry = row.geometry
                    density = row.POP_SQMI
                    state_line, state_area, center = get_line_and_area(
                        axes,
                        get_line_coord(geometry),
                        density
                    )

                    states_line_group.add(state_line)
                    state_area_group.add(state_area)

                state_label = Text(
                    f"{state}: {density:.2f} per square mile ",
                    font_size=25,
                    color=BLACK
                )

                state_label.move_to(UP + 2.3 * UP)

                self.play(Create(states_line_group), Write(state_label), run_time=2)

                self.play(Create(state_area_group), run_time=2)

                self.play(FadeOut(state_label))
            else:
                geometry = state_df.geometry.values[0]
                density = state_df.POP_SQMI.values[0]

                state_line, state_area, center = get_line_and_area(
                    axes,
                    get_line_coord(geometry),
                    density
                )
                state_label = Text(
                    f"{state}: {density:.2f} per square mile ",
                    font_size=25,
                    color=BLACK
                )

                state_label.move_to(UP + 2.3 * UP)

                self.play(Create(state_line), Write(state_label), run_time=2)

                self.play(Create(state_area), run_time=2)

                self.play(FadeOut(state_label))