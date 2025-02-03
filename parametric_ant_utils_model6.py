
import numpy as np
import matplotlib.pyplot as plt
# from detect_good_ants import count

class data_linewidth_plot():
    def __init__(self, x, y, **kwargs):
        self.ax = kwargs.pop("ax", plt.gca())
        self.fig = self.ax.get_figure()
        self.lw_data = kwargs.pop("linewidth", 1)
        self.lw = 1
        self.fig.canvas.draw()

        self.ppd = 72./self.fig.dpi
        self.trans = self.ax.transData.transform
        self.linehandle, = self.ax.plot([],[],**kwargs)
        if "label" in kwargs: kwargs.pop("label")
        self.line, = self.ax.plot(x, y, **kwargs)
        self.line.set_color(self.linehandle.get_color())
        self._resize()
        self.cid = self.fig.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        lw =  ((self.trans((1, self.lw_data))-self.trans((0, 0)))*self.ppd)[1]
        if lw != self.lw:
            self.line.set_linewidth(lw)
            self.lw = lw
            self._redraw_later()

    def _redraw_later(self):
        self.timer = self.fig.canvas.new_timer(interval=10)
        self.timer.single_shot = True
        self.timer.add_callback(lambda : self.fig.canvas.draw_idle())
        self.timer.start()




def get_parameters_names():
    parameters_names = []
    for iw in range(3):
        parameters_names.append(f'L{iw + 1:d}_rel')
    parameters_names.append('W1')
    parameters_names.append('W2')
    parameters_names.append('gap')
    return parameters_names

def randomize_ant(parameters_names,model_parameters,seed=0):
    ant_parameters = {}
    if seed > 0:
        np.random.seed(seed)
    valid_ant = 0
    count_retries = 0
    while not valid_ant:
        for iw in range(4):
            ant_parameters[f'L{iw + 1:d}_rel'] = np.round(np.random.uniform(), decimals=2)
        ant_parameters['W1'] = np.round(np.random.uniform(0.5,2.5), decimals=1)
        ant_parameters['W2'] = np.round(np.random.uniform(0.5, 3), decimals=1)
        ant_parameters['gap'] = np.round(np.random.uniform(0.1, 1), decimals=1)
        valid_ant = check_ant_validity(ant_parameters, model_parameters)
        count_retries += 1
        if count_retries % 1000 == 0:
            print(f'retried {count_retries:d} times, trying some more')
    print(f'retried {count_retries:d} times')
    return ant_parameters


def check_ant_validity(ant_parameters,model_parameters):
    if (model_parameters['LG_y'] - ant_parameters['W1'] * 3 - ant_parameters['gap']) <= 0:
        return 0
    for [key,item] in ant_parameters.items():
        if item <= 0:
            return 0
    for iw in range(4):
        if ant_parameters[f'L{iw + 1:d}_rel'] > 1:
            return 0
    # if ant_parameters['L4'] > ant_parameters['L2']:
    #     return 0
    return 1

def create_bricks_list(model_parameters,ant_parameters):

    ant_parameters['L1'] = ant_parameters['L1_rel'] * model_parameters['LG_y']
    ant_parameters['L2'] = ant_parameters['L2_rel'] * (model_parameters['A_z'] - ant_parameters['W2'])
    ant_parameters['L3'] = (ant_parameters['L3_rel'] *
                            (model_parameters['LG_y'] - 3*ant_parameters['W2'] - ant_parameters['gap']))
    ant_parameters['L4'] = ant_parameters['L4_rel'] * ant_parameters['L2']

    feed_PEC_bricks = [
        [[0, 0, 0], [0, ant_parameters['W1'], 10]]
        [[-0.8, 0, 0], [-0.8,  ant_parameters['W1'], -10]]]

    feed_brick = [[-0.8, 0, 0], [0, ant_parameters['W1'], 0]]

    ant_PEC_bricks = [
        [[0, 0, 0], [0, ant_parameters['W1'], model_parameters['A_z']]],
        [[0, 0, model_parameters['A_z']], [-0.8, ant_parameters['W1'], model_parameters['A_z']]],
        [[-0.8, 0, model_parameters['A_z']], [-0.8, ant_parameters['L1'], model_parameters['A_z']-ant_parameters['W1']]],
        [[0, ant_parameters['W1']+ant_parameters['gap'], 0], # ant_parameters['W1']+ant_parameters['gap'] is the new y=0
         [0, ant_parameters['W1']+ant_parameters['gap'] + ant_parameters['W1'],
          ant_parameters['W2'] + ant_parameters['L2']]],
        [[0, ant_parameters['W1']+ant_parameters['gap'] + ant_parameters['W1'], ant_parameters['L2']],
         # ant_parameters['W1']+ant_parameters['gap'] is the new y=0
         [0, ant_parameters['W1'] + ant_parameters['gap'] + ant_parameters['W1'] + ant_parameters['L3'],
          ant_parameters['W2'] + ant_parameters['L2']]],
        [[0, ant_parameters['W1'] + ant_parameters['gap'] + ant_parameters['W1'] + ant_parameters['L3'],
          ant_parameters['W2'] + ant_parameters['L2']],
         # ant_parameters['W1']+ant_parameters['gap'] is the new y=0
         [0, ant_parameters['W1'] + ant_parameters['gap'] + 2 * ant_parameters['W1'] + ant_parameters['L3'],
          ant_parameters['L2'] - ant_parameters['L4']]]

    ]
    # now we have 3 lists:
    #   1. feed_points - the points describing the feed (not PEC)
    #   2. feed_PEC_points - the points of the (not adjustable) feed PEC legs
    #   3. ant_PEC - a list of lists - each describes a set of points of a specific antenna PEC leg.
    # all of these 'lines' have the save width in the simulation - ant_parameters['w']

    # the translation of the axes should be:
        # rotation of 180 degs around [1, 0, 0]
        # shift of [-0.8, model_parameters['LG_y'], 0]

    return [feed_brick, feed_PEC_bricks, ant_PEC_bricks]


    
def save_figure(model_parameters,ant_parameters, output_path, run_ID, alpha=1):
    return 0
    # plt.ioff()
    # f, ax1 = plt.subplots()
    # wings = ['w1', 'w2', 'q1', 'q2']
    # Sz = (model_parameters['Sz'] / 2 - ant_parameters['w'] / 2
    #       - model_parameters['feed_length'] / 2)
    # Sy = model_parameters['Sy'] - ant_parameters['w']
    # data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
    #                     [-10,10], linewidth=ant_parameters['w'] + 0.1, alpha=alpha, color='k')
    # for wing in wings:
    #     if wing[0]=='q':
    #         sign=-1
    #     else:
    #         sign=1
    #     z = [Sz * ant_parameters[f'{wing}z0']]
    #     y = [0, 0]
    #     for i1 in range(3):
    #         z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
    #         z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
    #         y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
    #         y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
    #     y.pop()
    #     data_linewidth_plot(y, sign*np.array(z),
    #                         linewidth=ant_parameters['w']-0.01, alpha=alpha, color='b')
    # wings = ['w3', 'q3']
    # for wing in wings:
    #     if wing[0]=='q':
    #         sign=-1
    #     else:
    #         sign=1
    #     z = [Sz * ant_parameters[f'{wing}z0']]
    #     y = [Sy * ant_parameters['fx'], Sy * ant_parameters['fx']]
    #     z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
    #     z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
    #     y.append(Sy * ant_parameters[f'{wing}y{1:d}'])
    #     data_linewidth_plot(y, sign*np.array(z),
    #                         linewidth=ant_parameters['w']-0.01, alpha=alpha, color='b')
    # data_linewidth_plot([0, 0],
    #                     [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
    #                     linewidth=ant_parameters['w'], alpha=alpha, color='w')
    # data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
    #                     [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
    #                     linewidth=ant_parameters['w']+0.1, alpha=alpha, color='r')
    # plt.title('dimensions in mm')
    # ax1.set_aspect('equal')
    # plt.show(block=False)
    # f.savefig(output_path + '\\output\\model_pictures\\image_' + str(run_ID) + '.png')
    # plt.close(f)

# a = get_parameters_names()
# aa = randomize_ant(a,20,32,2)
if __name__ == "__main__":
    import pickle
    import os
    path = r'G:\local_model_5_path\simplified\output\models\90'
    ant_path = os.path.join(path, 'ant_parameters.pickle')
    model_path = os.path.join(path, 'model_parameters.pickle')
    ant_params = pickle.load(open(ant_path, 'rb'))
    model_params = pickle.load(open(model_path, 'rb'))
    print(check_ant_validity(ant_params, model_params))