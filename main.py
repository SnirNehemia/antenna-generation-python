
import matplotlib
import shapely
matplotlib.use('TkAgg')
from shapely import affinity
from matplotlib import pyplot as plt
import geopandas as gpd # just for plots
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity, Point
import numpy as np
from shapely import MultiPolygon
import os
from shapely.geometry import mapping
import ezdxf.addons.geo
import ezdxf
np.random.seed(1)


def rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=0):
    # create a rectangle and returns it. if it is out of bounds it returns 0
    rect = Polygon([(center[0]-size[0]/2, center[1]-size[1]/2),
                    (center[0]+size[0]/2, center[1]-size[1]/2),
                    (center[0]+size[0]/2, center[1]+size[1]/2),
                    (center[0]-size[0]/2, center[1]+size[1]/2)])
    rect = affinity.rotate(rect, angle, origin='center')
    if intersection_bool:
        if not rect.intersects(feed_buffer):
            rect = shapely.intersection(rect, bounds_polygon)
            return rect
        else:
            return 0
    else:
        if bounds_polygon.contains(rect) and not rect.intersects(feed_buffer):
            return rect
        else:
            return 0


# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print('starting run...')

# define the constant parameters:
rect_amount = 100
# add rect properties - center and size
sub_amount = 10
sub_size = [[3, 20], [0.5, 1.5]]
bounds = [(-100, 100), (-100, 100)]
max_poly_num = 5  # maximum amount of polygons
discrete_angle = 45  # discrete angle of rectangles

# define bounding polygon in format of [(x),(y)], for now it's a simple rectangle

bounds_polygon = Polygon([(bounds[0][0], bounds[1][0]),
                          (bounds[0][1], bounds[1][0]),
                          (bounds[0][1], bounds[1][1]),
                          (bounds[0][0], bounds[1][1])])

# create feed and define "safe zone" around it
feed_length = 5
buffer_size = feed_length/2
feed_center = np.random.uniform(-50, 50, (2, 1))
feed_size = [np.random.uniform(max(feed_length*3, 50), 50), 5]
feed_angle = 0  #np.random.uniform(0, 360)

feed_PEC = rectangle(feed_center, feed_size, feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))
feed_poly = rectangle(feed_center, (feed_length, feed_size[1]), feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))

feed_buffer = shapely.buffer(feed_poly, buffer_size)

feed_PEC = feed_PEC - feed_poly

# generate antenna polygons
ant_polys = []
count_failed = 0
for i in range(rect_amount):
    center = np.round(np.random.uniform(-100, 100, (2, 1)),1)
    size = np.round([np.random.uniform(10, 50), np.random.uniform(2, 10)],1)
    angle = np.random.randint(0, int(360/discrete_angle))*discrete_angle
    poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
    if poly != 0:
        ant_polys.append(poly)
    else:
        count_failed += 1
print(str(count_failed) + ' rectangles failed')
ants_merged = unary_union(ant_polys)  # merge the polygons

# generate sub polygons
sub_polys = []
count_failed = 0
for i in range(sub_amount):
    center = np.round(np.random.uniform(-100, 100, (2, 1)),1)
    size = np.round([np.random.uniform(sub_size[0][0], sub_size[0][1]),
                     np.random.uniform(sub_size[1][0], sub_size[1][1])],1)
    angle = np.random.randint(0, int(360/discrete_angle))*discrete_angle
    poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
    if poly != 0:
        sub_polys.append(poly)
    else:
        count_failed += 1
print(str(count_failed) + ' rectangles failed')
sub_merged = unary_union(sub_polys)  # merge the polygons

ants_merged = unary_union(ants_merged - sub_merged)
ant_polys = list(ants_merged.geoms)
ant_polys.sort(key=lambda x: x.area, reverse=True)  # sort from largest to smallest

if len(ant_polys) > max_poly_num:
    largest_ant_polys = ant_polys[0:max_poly_num]
else:
    largest_ant_polys = ant_polys

ants_merged = unary_union(largest_ant_polys)

# if i want to count them
if ants_merged.geom_type == 'MultiPolygon':
    polygon_list = list(ants_merged.geoms)  # extract it back to a polygon list
    polygon_num = len(polygon_list)
else:
    polygon_num = 1

# plot the antenna
f, ax = plt.subplots()
gpd.GeoSeries(ant_polys).boundary.plot(ax=ax, alpha=0.2)
gpd.GeoSeries(ants_merged).plot(ax=ax, alpha=0.5)
gpd.GeoSeries(feed_PEC).boundary.plot(ax=ax, color='black')
gpd.GeoSeries(feed_buffer).boundary.plot(ax=ax, color='red', alpha=0.5, linestyle='--')
gpd.GeoSeries(feed_poly).plot(ax=ax, color='red', alpha=0.5)

gpd.GeoSeries(sub_merged).plot(ax=ax, color='gold', alpha=0.1)

# save the model

os.chdir(r"C:\Users\Snir\OneDrive - Tel-Aviv University\Snir - FemtoNano Group's files\AI RF design\python tests")

if not ants_merged.geom_type == 'MultiPolygon':
    PEC_rects = MultiPolygon(ants_merged)
else:
    PEC_rects = ants_merged
PEC_feed = feed_PEC
feed = feed_poly

polygon_lists = [PEC_rects, PEC_feed, feed]
files_name_list = ['PEC_rects', 'PEC_feed', 'feed']

for i, file_name in enumerate(files_name_list):

    doc = ezdxf.new("AC1032")
    geoproxy = ezdxf.addons.geo.GeoProxy.parse(mapping(polygon_lists[i]))
    msp = doc.modelspace()
    # Use LWPOLYLINE instead of hatch.
    for entity in geoproxy.to_dxf_entities(polygon=2):
        msp.add_entity(entity)
    doc.saveas(file_name + ".dxf")

print('finished')


# # find which rectangles are contained to subtract them(?)
# PEC_rect_list = list(PEC_rects.geoms)
# PEC_rect_list.sort(key=lambda x: x.area, reverse=True)
# index_inside = []
# holes = []
# for rect, i_rect in enumerate(PEC_rect_list):
#     for i_small in range(i_rect, len(PEC_rect_list)):
#         if shapely.contains(rect, PEC_rect_list[i_small]):
#             holes.append(PEC_rect_list[i_small])
#             index_inside.append(i_small)



def normalize_gain(theta_degrees, phi_degrees, gain, gain_pol=np.NAN):
    # assume gain is in linear units, theta and phi are in degrees.
    #   gain_pol is for the case shen you want to normalize Abs(phi) or Abs(theta).
    theta_rad, phi_rad = np.array([theta_degrees, phi_degrees]) * np.pi / 180
    d_theta = np.max(np.diff(theta_rad))
    d_phi = np.max(np.diff(phi_rad))
    efficiency = np.sum(np.multiply(gain, np.sin(theta_rad))) * d_theta * d_phi / (4*np.pi)
    directivity = gain / efficiency
    if np.isnan(gain_pol):
        return directivity
    else:
        directivity_pol = gain_pol / efficiency
        return directivity_pol