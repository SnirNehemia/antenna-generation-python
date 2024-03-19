
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
import pickle
from distutils.dir_util import copy_tree


def plot_DXF(file_name):
    doc = ezdxf.readfile(file_name)
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)


def rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=0):
    # create a rectangle and returns it. if it is out of bounds it returns 0
    rect = Polygon([(center[0]-size[0]/2, center[1]-size[1]/2),
                    (center[0]+size[0]/2, center[1]-size[1]/2),
                    (center[0]+size[0]/2, center[1]+size[1]/2),
                    (center[0]-size[0]/2, center[1]+size[1]/2)])
    rect = affinity.rotate(rect, angle, origin='center')
    if intersection_bool == -1: # debug mode
        return rect
    if intersection_bool:
        if not rect.intersects(feed_buffer):
            rect = shapely.intersection(rect, bounds_polygon)
            if rect.area <= 1e-6:   # check if this polygon had area i.e. not 1d line
                return 0
            return rect
        else:
            return 0
    else:
        if bounds_polygon.contains(rect) and not rect.intersects(feed_buffer):
            return rect
        else:
            return 0


def rot_mat(angle):
    c = np.cos(angle * np.pi/180)
    s = np.sin(angle * np.pi/180)
    return np.array([[c, -s], [s, c]])

def CreateDXF(plot=False, seed=-1, run_ID='', suppress_prints=True, save=True, debug_mode=False, polygons_parameters='',
              project_name='', local_path='', model=''):
    # debug mode prints the failed polygon
    if seed > 0:
        np.random.seed(seed)
    # initializations:
    # generate antenna polygons
    if model['type']==1:
        # height = 160 # coordinate along the y (green) axis
        # width = 300 # coordinate along the x (red) axis
        # adx = 0.8
        # arx = 0.75
        # ady = 0.8
        # ary = 0.8
        bounds = [(0, model['width'] * model['adx'] * model['arx']), (0, model['height'] * model['ady'] * model['ary'])]
    if model['type']==3:
        if model['plane'] == 'xz':
            bounds = [(0, model['width']*model['a']*model['adx']*model['arx']),
                      (0, model['length']*model['adz']*model['arz'])]
        if model['plane'] == 'yz':
            bounds = [(0, model['height'] * model['ady'] * model['ary']),
                      (0, model['length'] * model['adz'] * model['arz'])]

    l = np.max(bounds)
    ant_polys = []
    poly_list = []
    count_failed = 0
    chain_count = 0
    centers = []
    sizes = []
    angles = []
    # define the constant parameters:
    rect_amount = 75
    sub_amount = 10
    sub_size = [[l/20, l/10], [0.5, 1.5]]
    rect_size = [[l/20, l/10], [0.5, 2]]
    rect_center = [[bounds[0][1]*0.1, bounds[0][1]*0.9], [bounds[1][1]*0.1, bounds[1][1]*0.9]]
    max_poly_num = 5  # maximum amount of merged polygons
    discrete_angle = 45  # discrete angle of rectangles

    mode = 'chain'
    chain_chance = 0.95
    polygon_type = 0 # polygon_type = :
                        # 0 for first chain - 1st polygon
                        # 1 for second chain - 1st polygon
                        # -1 for any othe polygon
    # define bounding polygon in format of [(x),(y)], for now it's a simple rectangle

    bounds_polygon = Polygon([(bounds[0][0], bounds[1][0]),
                              (bounds[0][1], bounds[1][0]),
                              (bounds[0][1], bounds[1][1]),
                              (bounds[0][0], bounds[1][1])])

    # create feed and define "safe zone" around it
    feed_length = 1
    buffer_size = feed_length * 1
    # feed_center =  np.round(np.random.uniform(20, 80, 2),1)
    feed_center = np.round(np.random.uniform(np.array([bounds[0][1], bounds[1][1]])*0.2,
                                             np.array([bounds[0][1], bounds[1][1]])*0.8),1)
    feed_size =  np.round(np.array([np.random.uniform(max(feed_length*5, l/5), l/5), 1]),1)
    feed_angle = 0  #np.random.uniform(0, 360)

    centers.append(feed_center)
    sizes.append(feed_size)
    angles.append(feed_angle)

    # create feed polygon:

    feed_PEC = rectangle(feed_center, feed_size, feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))
    feed_poly = rectangle(feed_center, (feed_length, feed_size[1]), feed_angle, bounds_polygon, Point([bounds[0][0], bounds[1][0]]))

    feed_buffer = shapely.buffer(feed_poly, buffer_size)

    feed_PEC = feed_PEC - feed_poly

    for i in range(rect_amount):
        # if it's in 'chain' mode AND it's not the first piece AND we continue the same chain
        if mode == 'chain' and not len(poly_list) == 0 and np.random.random() < chain_chance: # TODO: check it's fine with first chain element
            poly = 0
            failed = 0
            while not poly:  # as long as it didn't find a proper polygon:
                # center_prev = center
                # angle_prev = angle
                # size_prev = size
                size = np.round([np.random.uniform(rect_size[0][0], rect_size[0][1]),
                                 np.random.uniform(rect_size[1][0], rect_size[1][1])], 1)
                angle = np.random.randint(0, int(360 / discrete_angle)) * discrete_angle #(-1)**failed # so it change sign between failed attempts
                center = (centers[-1] + 1 *
                          np.matmul(rot_mat(angles[-1] ), (sizes[-1] - np.array([1, 0])) * np.array([1, 0])) / 2 +
                          np.matmul(rot_mat(angle), size * np.array([1, 0])) / 2)
                poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
                if not suppress_prints:
                    if poly!=0:
                        print(f' polygon successful')
                    else:
                        print(f' polygon failed')
                if debug_mode:
                    if poly == 0:
                        poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=-1)
                        print(f' center: {center[0]:.0f}, {center[1]:.0f} ')
                        print(f' size: {size[0]:.0f}, {size[1]:.0f} ')
                        print(f' angle: {angle:.0f} ')

                        f, ax = plt.subplots()
                        gpd.GeoSeries(feed_PEC).boundary.plot(ax=ax, color='black')
                        gpd.GeoSeries(feed_buffer).boundary.plot(ax=ax, color='red', alpha=0.5, linestyle='--')
                        gpd.GeoSeries(feed_poly).plot(ax=ax, color='red', alpha=0.5)
                        gpd.GeoSeries(poly).plot(ax=ax, color='blue', alpha=0.5)
                        gpd.GeoSeries(ant_polys).plot(ax=ax, color='green', alpha=0.5)

                        #a = input('press enter to continue')
                        #plt.close(f)
                        poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
                if poly == 0:
                    failed = failed + 1
                    if failed > 10:
                        print('failed too many times! there is a bug in dxf generation!')
                        break
            # centers.append(center)
            # sizes.append(size)
            # angles.append(angle)
        else: # if we start a new chain:
            if mode == 'chain':
                chain_count += 1
                if not suppress_prints:
                    print('started a new chain #'+str(chain_count))
            poly = 0
            while poly == 0: # as long as there is not yet a valid polygon:
                # roll parameters
                center = np.round([np.random.uniform(rect_center[0][0], rect_center[0][1]),
                                 np.random.uniform(rect_center[1][0], rect_center[1][1])], 1)
                size = np.round([np.random.uniform(rect_size[0][0], rect_size[0][1]),
                                 np.random.uniform(rect_size[1][0], rect_size[1][1])], 1)
                angle = np.random.randint(0, int(360/discrete_angle))*discrete_angle
                if mode == 'chain' and chain_count == 1:  # if it's the first chain:
                    center = (feed_center + -1 *
                              np.matmul(rot_mat(feed_angle), feed_size * np.array([1, 0])) / 2 +
                              np.matmul(rot_mat(angle), size * np.array([1, 0])) / 2)

                if mode == 'chain' and chain_count == 2: # if it's the second chain:
                    center = (feed_center +
                              np.matmul(rot_mat(feed_angle), feed_size * np.array([1, 0])) / 2 +
                              np.matmul(rot_mat(angle), size * np.array([1, 0])) / 2)

                poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)

                if poly == 0 and debug_mode: # if it failed in one of the two edges of the feed:
                    poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=-1)
                    print(f' center: {center[0]:.0f}, {center[1]:.0f} ')
                    print(f' size: {size[0]:.0f}, {size[1]:.0f} ')
                    print(f' angle: {angle:.0f} ')

                    f1, ax1 = plt.subplots()
                    gpd.GeoSeries(feed_PEC).boundary.plot(ax=ax1, color='black')
                    gpd.GeoSeries(feed_buffer).boundary.plot(ax=ax1, color='red', alpha=0.5, linestyle='--')
                    gpd.GeoSeries(feed_poly).plot(ax=ax1, color='red', alpha=0.5)
                    gpd.GeoSeries(poly).plot(ax=ax1, color='blue', alpha=0.5)
                    gpd.GeoSeries(ant_polys).plot(ax=ax1, color='green', alpha=0.5)
                    print(f'failed in {chain_count:.0f} chain first polygon')
                    poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
        if poly != 0:
            ant_polys.append(poly)
            centers.append(center)
            sizes.append(size)
            angles.append(angle)
            poly_list.append([center, size, angle])
        else:
            count_failed += 1
    if not suppress_prints:
        print(str(count_failed) + ' rectangles failed')
    # print(poly_list)
    ants_merged = unary_union(ant_polys)  # merge the polygons

    # generate sub polygons
    sub_polys = []
    count_failed = 0
    for i in range(sub_amount):
        center = np.round([np.random.uniform(rect_center[0][0], rect_center[0][1]),
                             np.random.uniform(rect_center[1][0], rect_center[1][1])], 1)
        size = np.round([np.random.uniform(sub_size[0][0], sub_size[0][1]),
                         np.random.uniform(sub_size[1][0], sub_size[1][1])], 1)
        angle = np.random.randint(0, int(360/discrete_angle))*discrete_angle
        poly = rectangle(center, size, angle, bounds_polygon, feed_buffer, intersection_bool=1)
        if poly != 0:
            sub_polys.append(poly)
        else:
            count_failed += 1
    if not suppress_prints:
        print(str(count_failed) + ' rectangles failed')
        print('total chain amount: ' + str(chain_count) + f' with {rect_amount:.0f} polygons')
    sub_merged = unary_union(sub_polys)  # merge the polygons

    ants_merged = unary_union(ants_merged - sub_merged)
    if ants_merged.geom_type == 'MultiPolygon':
        ant_polys = list(ants_merged.geoms)
        ant_polys.sort(key=lambda x: x.area, reverse=True)  # sort from largest to smallest

        if len(ant_polys) > max_poly_num:
            largest_ant_polys = ant_polys[0:max_poly_num]
        else:
            largest_ant_polys = ant_polys
        ants_merged = unary_union(largest_ant_polys)
        # if i want to count them
        polygon_list = list(ants_merged.geoms)  # extract it back to a polygon list
        polygon_num = len(polygon_list)
    else:
        polygon_num = 1
    if not plot:
        plt.ioff()
    # if plot:
    # plot the antenna
    f, ax = plt.subplots()
    gpd.GeoSeries(ant_polys).boundary.plot(ax=ax, alpha=0.2)
    gpd.GeoSeries(ants_merged).plot(ax=ax, alpha=0.5)
    gpd.GeoSeries(feed_PEC).boundary.plot(ax=ax, color='black')
    gpd.GeoSeries(feed_buffer).boundary.plot(ax=ax, color='red', alpha=0.5, linestyle='--')
    gpd.GeoSeries(feed_poly).plot(ax=ax, color='red', alpha=0.5)

    gpd.GeoSeries(sub_merged).plot(ax=ax, color='gold', alpha=0.1)

    if save:
        # save the model
        save_dir = local_path + project_name+'\\output\\models'
        save_pic_dir = local_path + project_name+'\\output\\model_pictures'
        if run_ID != '':
            save_dir = save_dir + '\\'+ run_ID
        # os.getcwd() # r"C:\Users\Snir\OneDrive - Tel-Aviv University\Snir - FemtoNano Group's files\AI RF design\python tests"
        if os.path.isdir(save_dir):
            os.chdir(save_dir)

        f.savefig(save_dir + r'\image.png')
        f.savefig(save_pic_dir + r'\image_' + run_ID + '.png')
        if not plot:
            plt.close(f)

        # if not ants_merged.geom_type == 'MultiPolygon':
        #     PEC_rects = MultiPolygon(ants_merged)
        # else:

        # PEC = unary_union([ants_merged,feed_PEC])
        rect_PEC = ants_merged
        # feed_PEC
        feed = feed_poly

        polygon_lists = [rect_PEC, feed_PEC, feed]
        files_name_list = ['layer_0_PEC', 'feed_PEC', 'feed']
        if not suppress_prints:
            print('saves files to ' + os.getcwd())

        for i, file_name in enumerate(files_name_list):

            doc = ezdxf.new("AC1032")
            geoproxy = ezdxf.addons.geo.GeoProxy.parse(mapping(polygon_lists[i]))
            msp = doc.modelspace()
            # Use LWPOLYLINE instead of hatch.
            for entity in geoproxy.to_dxf_entities(polygon=2):
                msp.add_entity(entity)
            doc.saveas(file_name + ".dxf")
            if not suppress_prints:
                print('saved: ' + file_name + ".dxf")

        file_name = 'feed_layer_parameters.pickle'
        file = open(file_name, 'wb')
        pickle.dump([centers, sizes, angles], file)
        file.close()
        target_folder = local_path + project_name + "\\DXF_Model"
        # target_folder = r'C:\Users\shg\OneDrive - Tel-Aviv University\Documents\CST_projects\phase_2\ALL_Model_1_1_layer\DXF_Model' # TODO: add some order to the saved directories!
        copy_tree(save_dir, target_folder)
        if not suppress_prints:
            print('updated dxf for file')
            print(' --- finished --- ')
    return [centers, sizes, angles]

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

if __name__ == '__main__':
    print('generating a DXF...')
    # for i in range(1):
    # project_name = r'TEMPLATE\ALL_Model_1_1_layer'
    # project_name = r'phase_2\test_performance'
    i=1
    project_name = r'Model3Again'
    model_parameters = {
        'type': 3,
        'height': 50,  # coordinate along the y (green) axis
        'width': 100,  # coordinate along the x (red) axis
        'adx': 0.9,
        'arx': 0.9,
        'adz': 0.85,
        'arz': 0.85,
        'a': 0.6
    }
    local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"
        # [centers, sizes, angles] = CreateDXF(plot=True, seed=i, suppress_prints=False, save=False, debug_mode=True)
    [centers, sizes, angles] = CreateDXF(plot=True, seed=i, suppress_prints=False, save=True, debug_mode=True,
                                         project_name=project_name, model=model_parameters,local_path=local_path)
        # print(f'\n finished with: {i:.0f} \n')