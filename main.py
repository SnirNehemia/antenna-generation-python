
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
bounds = [(-100, 100), (-100, 100)]
max_poly_num = 10  # maximum amount of polygons

# define bounding polygon in format of [(x),(y)], for now it's a simple rectangle

bounds_polygon = Polygon([(bounds[0][0], bounds[1][0]),
                          (bounds[0][1], bounds[1][0]),
                          (bounds[0][1], bounds[1][1]),
                          (bounds[0][0], bounds[1][1])])

# create feed and define "safe zone" around it
feed_length = 5
buffer_size = feed_length/2
feed_center = np.random.uniform(-50, 50, (2, 1))
feed_size = [np.random.uniform(max(feed_length*3,50), 50), 5]
feed_angle = 0 #np.random.uniform(0, 360)

feed_PEC = rectangle(feed_center, feed_size, feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))
feed_poly = rectangle(feed_center, (feed_length, feed_size[1]), feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))

feed_buffer = shapely.buffer(feed_poly, buffer_size)

feed_PEC = feed_PEC - feed_poly

# generate antenna polygons
ant_polys = []
count_failed = 0
for i in range(rect_amount):
    center = np.random.uniform(-100, 100, (2, 1))
    size = [np.random.uniform(10, 50), np.random.uniform(2, 10)]
    angle = np.random.uniform(0, 360)
    poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
    if poly != 0:
        ant_polys.append(poly)
    else:
        count_failed += 1
print(str(count_failed) + ' rectangles failed')

mergedPolys = unary_union(ant_polys)  # merge the polygons
ant_polys = list(mergedPolys.geoms)
ant_polys.sort(key=lambda x: x.area, reverse=True)  # sort from largest to smallest

if len(ant_polys) > max_poly_num:
    largest_ant_polys = ant_polys[0:max_poly_num]
else:
    largest_ant_polys = ant_polys

mergedPolys = unary_union(largest_ant_polys)

# if i want to count them
if mergedPolys.geom_type == 'MultiPolygon':
    polygon_list = list(mergedPolys.geoms)  # extract it back to a polygon list
    polygon_num = len(polygon_list)
else:
    polygon_num = 1

# plot the antenna
f, ax = plt.subplots()
gpd.GeoSeries(ant_polys).boundary.plot(ax=ax, alpha=0.2)
gpd.GeoSeries([mergedPolys]).plot(ax=ax)
gpd.GeoSeries(feed_PEC).boundary.plot(ax=ax, color='black')
gpd.GeoSeries(feed_buffer).boundary.plot(ax=ax, color='red', alpha=0.5, linestyle='--')
gpd.GeoSeries(feed_poly).plot(ax=ax, color='red', alpha=0.5)

# save the model

os.chdir(r"C:\Users\Snir\OneDrive - Tel-Aviv University\Snir - FemtoNano Group's files\AI RF design\python tests")

if not mergedPolys.geom_type == 'MultiPolygon':
    PEC_rects = MultiPolygon(mergedPolys)
else:
    PEC_rects = mergedPolys
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


poly = rectangle([-50, -50], [50, 50], 0, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))

p = PEC_rects - poly
f, ax = plt.subplots()
gpd.GeoSeries(p).plot(ax=ax, color='black')


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

