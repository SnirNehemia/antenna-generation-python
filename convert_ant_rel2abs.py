
import numpy as np

def rel2abs(ant_parameters, model_parameters):
    ant_parameters_abs = ant_parameters.copy()
    if model_parameters['type'] == 3:
        Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
              - model_parameters['feed_length'] / 2)
        Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
        for key, value in ant_parameters.items():
            if len(key) == 4:
                if key[2] == 'z':
                    ant_parameters_abs[key] = np.round(value * Sz, decimals=2)
                if key[2] == 'y':
                    ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
            if key == 'fx':
                ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
    if model_parameters['type'] == 6:
        ant_parameters_abs['L1_rel'] = ant_parameters_abs['L1_rel'] * model_parameters['LG_y']
        ant_parameters_abs['L2_rel'] = ant_parameters_abs['L2_rel'] * (model_parameters['A_z'] - ant_parameters_abs['W2'])
        ant_parameters_abs['L3_rel'] = ant_parameters_abs['L3_rel'] * (model_parameters['LG_y'] - ant_parameters_abs['W1']*3 - ant_parameters_abs['gap'])
        ant_parameters_abs['L4_rel'] = ant_parameters_abs['L4_rel'] * ant_parameters_abs['L2_rel']
    if model_parameters['type'] == 5:
        ant_parameters_abs = ant_parameters.copy()
        Sz = model_parameters['Sz'] - ant_parameters['w'] / 2 - model_parameters['feed_length'] / 2
        Sy = model_parameters['Sy'] - ant_parameters['w']
        for key, value in ant_parameters.items():
            if len(key) == 4:
                if key[2] == 'z':
                    ant_parameters_abs[key] = np.round(value * Sz, decimals=2)
                if key[2] == 'y':
                    ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
            if key == 'fx':
                ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
    return ant_parameters_abs

def abs2rel(ant_parameters_abs, model_parameters):
    ant_parameters_rel = ant_parameters_abs.copy()
    if model_parameters['type'] == 5:
        Sz = model_parameters['Sz'] - ant_parameters_abs['w'] / 2 - model_parameters['feed_length'] / 2
        Sy = model_parameters['Sy'] - ant_parameters_abs['w']
        for key, value in ant_parameters_abs.items():
            if len(key) == 4:
                if key[2] == 'z':
                    ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
                if key[2] == 'y':
                    ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
            if key == 'fx':
                ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
    if model_parameters['type'] == 3:
        Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
              - model_parameters['feed_length'] / 2)
        Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
        for key, value in ant_parameters_abs.items():
            if len(key) == 4:
                if key[2] == 'z':
                    ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
                if key[2] == 'y':
                    ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
            if key == 'fx':
                ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
    if model_parameters['type'] == 6:
        ant_parameters_rel['L4_rel'] = ant_parameters_abs['L4_rel'] / ant_parameters_abs['L2_rel']
        ant_parameters_rel['L1_rel'] = ant_parameters_abs['L1_rel'] / model_parameters['LG_y']
        ant_parameters_rel['L2_rel'] = ant_parameters_abs['L2_rel'] / (
                    model_parameters['A_z'] - ant_parameters_abs['W2'])
        ant_parameters_rel['L3_rel'] = ant_parameters_abs['L3_rel'] / (
                    model_parameters['LG_y'] - ant_parameters_abs['W1'] * 3 - ant_parameters_abs['gap'])
    return ant_parameters_rel

def model_rel2abs(model_parameters):
    model_parameters_abs = model_parameters.copy()
    if model_parameters['type'] == 5:
        model_parameters_abs = model_parameters.copy()
        model_parameters_abs['Lz'] = model_parameters['Sz'] * model_parameters_abs['Lz']
        model_parameters_abs['Ly'] = model_parameters['Sy'] * model_parameters_abs['Ly']
        # model_parameters_abs['d'] = model_parameters['d'] * model_parameters['height']
    if model_parameters['type'] == 3:
        axes = ['x','y','z']
        dimensions = ['width','height','length']

        elements = ['a','b','c','d']
        for e in elements:
            for [axis,i_axis] in enumerate(axes):
                model_parameters_abs[e+'d' + axis] = model_parameters[e+'d' + axis] * model_parameters[dimensions[i_axis]]
                model_parameters_abs[e+'r' + axis] = model_parameters[e+'r' + axis] * model_parameters[e+'d' + axis] * model_parameters[dimensions[i_axis]]
        model_parameters_abs['a'] = model_parameters['a'] *model_parameters['width']
        model_parameters_abs['b'] = model_parameters['b'] * model_parameters['height']
        model_parameters_abs['c'] = model_parameters['c'] * model_parameters['height']
        # model_parameters_abs['d'] = model_parameters['d'] * model_parameters['height']
    if model_parameters['type'] == 6:
        return model_parameters_abs
    return model_parameters_abs

# def model_abs2rel(ant_parameters_abs, model_parameters):
#     ant_parameters_rel = ant_parameters_abs.copy()
#     Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
#           - model_parameters['feed_length'] / 2)
#     Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
#     for key, value in ant_parameters_abs.items():
#         if len(key) == 4:
#             if key[2] == 'z':
#                 ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
#             if key[2] == 'y':
#                 ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
#         if key == 'fx':
#             ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
#     return ant_parameters_rel


# ---------------------------------------------------------------------------------------------------------------------------

def check_ant_validity(ant_parameters, model_parameters) -> int:
    Sz = model_parameters['Sz'] - ant_parameters['w'] / 2 - model_parameters['feed_length'] / 2
    Sy = model_parameters['Sz'] - ant_parameters['w']
    wings = ['w1', 'w2', 'q1', 'q2']
    for key in ant_parameters:
        if ant_parameters[key] < 0: return 0
        if key != 'w' and ant_parameters[key] > 1: return 0
    for wing in wings:
        if (ant_parameters[f'{wing}z3'] > ant_parameters[f'{wing}z1'] > ant_parameters[f'{wing}z2'] and
                ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y2']):
            return 0
        if (ant_parameters[f'{wing}z2'] > ant_parameters[f'{wing}z1'] > ant_parameters[f'{wing}z3'] and
                ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y2']):
            return 0
        if (ant_parameters[f'{wing}z1'] > ant_parameters[f'{wing}z3'] > ant_parameters[f'{wing}z2'] and
                ant_parameters[f'{wing}y3'] > ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y2']):
            return 0
        if (ant_parameters[f'{wing}z2'] > ant_parameters[f'{wing}z3'] > ant_parameters[f'{wing}z1'] and
                ant_parameters[f'{wing}y3'] > ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y2']):
            return 0
        if (ant_parameters[f'{wing}z2'] > ant_parameters[f'{wing}z3'] > ant_parameters[f'{wing}z1'] and
                ant_parameters[f'{wing}y2'] > ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y3']):
            return 0
        if (ant_parameters[f'{wing}z1'] > ant_parameters[f'{wing}z3'] > ant_parameters[f'{wing}z2'] and
                ant_parameters[f'{wing}y2'] > ant_parameters[f'{wing}y1'] > ant_parameters[f'{wing}y3']):
            return 0
        if np.abs(ant_parameters[f'{wing}z2'] - ant_parameters[f'{wing}z1']) < ant_parameters['w'] / Sz: return 0
        if np.abs(ant_parameters[f'{wing}z1'] - ant_parameters[f'{wing}z3']) < ant_parameters['w'] / Sz: return 0
        if np.abs(ant_parameters[f'{wing}z2'] - ant_parameters[f'{wing}z3']) < ant_parameters['w'] / Sz: return 0
        if ant_parameters[f'{wing}y1'] < ant_parameters['w'] / Sy: return 0
        if ant_parameters[f'{wing}y2'] < ant_parameters['w'] / Sy: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y1']) < ant_parameters['w'] / Sy: return 0
        if np.abs(ant_parameters[f'{wing}y1'] - ant_parameters[f'{wing}y3']) < ant_parameters['w'] / Sy: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y3']) < ant_parameters['w'] / Sy: return 0
    if (Sz * ant_parameters[f'q1z3'] - ant_parameters['w'] / 2 <= 5
            and (ant_parameters[f'q1y3'] < ant_parameters['fx'] < ant_parameters[f'q1y2'] or
                 ant_parameters[f'q1y2'] < ant_parameters['fx'] < ant_parameters[f'q1y3'])): return 0
    if (Sz * ant_parameters[f'w1z3'] - ant_parameters['w'] / 2 <= 5
            and (ant_parameters[f'w1y3'] < ant_parameters['fx'] < ant_parameters[f'w1y2'] or
                 ant_parameters[f'w1y2'] < ant_parameters['fx'] < ant_parameters[f'w1y3'])): return 0
    wings = ['w1', 'w2', 'w3', 'q1', 'q2', 'q3']
    for wing in wings:
        if np.abs(ant_parameters[f'{wing}z0'] - ant_parameters[f'{wing}z1']) <= ant_parameters['w'] / Sz: return 0
    if np.min([ant_parameters[f'q3z0'], ant_parameters[f'w3z0']]) > 0.2: return 0
    return 1


def model_rel2abs(model_parameters):
    model_parameters_abs = model_parameters.copy()
    model_parameters_abs['Lz'] = model_parameters['Sz'] * model_parameters_abs['Lz']
    model_parameters_abs['Ly'] = model_parameters['Sy'] * model_parameters_abs['Ly']
    # model_parameters_abs['d'] = model_parameters['d'] * model_parameters['height']
    return model_parameters_abs



def ant_rel2abs(ant_parameters: dict, model_parameters: dict):
    ant_parameters_abs = ant_parameters.copy()
    Sz = model_parameters['Sz'] - ant_parameters['w'] / 2 - model_parameters['feed_length'] / 2
    Sy = model_parameters['Sz'] - ant_parameters['w']
    for key, value in ant_parameters.items():
        if len(key) == 4:
            if key[2] == 'z':
                ant_parameters_abs[key] = np.round(value * Sz, decimals=2)
            if key[2] == 'y':
                ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
        if key == 'fx':
            ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
    return ant_parameters_abs


def ant_abs2rel(ant_parameters_abs: dict, model_parameters: dict):
    ant_parameters_rel = ant_parameters_abs.copy()
    Sz = model_parameters['Sz'] - ant_parameters['w'] / 2 - model_parameters['feed_length'] / 2
    Sy = model_parameters['Sz'] - ant_parameters['w']
    for key, value in ant_parameters_abs.items():
        if len(key) == 4:
            if key[2] == 'z':
                ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
            if key[2] == 'y':
                ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
        if key == 'fx':
            ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
    return ant_parameters_rel



class data_linewidth_plot:
    def __init__(self, x, y, **kwargs):
        self.ax = kwargs.pop("ax", plt.gca())
        self.fig = self.ax.get_figure()
        self.lw_data = kwargs.pop("linewidth", 1)
        self.lw = 1
        self.fig.canvas.draw()

        self.ppd = 72. / self.fig.dpi
        self.trans = self.ax.transData.transform
        self.linehandle, = self.ax.plot([], [], **kwargs)
        if "label" in kwargs: kwargs.pop("label")
        self.line, = self.ax.plot(x, y, **kwargs)
        self.line.set_color(self.linehandle.get_color())
        self._resize()
        self.cid = self.fig.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        lw = ((self.trans((1, self.lw_data)) - self.trans((0, 0))) * self.ppd)[1]
        if lw != self.lw:
            self.line.set_linewidth(lw)
            self.lw = lw
            self._redraw_later()

    def _redraw_later(self):
        self.timer = self.fig.canvas.new_timer(interval=10)
        self.timer.single_shot = True
        self.timer.add_callback(lambda: self.fig.canvas.draw_idle())
        self.timer.start()


def plot_antenna_figure(model_parameters, ant_parameters, alpha=1):
    plt.ioff()
    f, ax1 = plt.subplots()
    wings = ['w1', 'w2', 'q1', 'q2']
    Sz = model_parameters['Sz'] - ant_parameters['w'] / 2 - model_parameters['feed_length'] / 2
    Sy = model_parameters['Sz'] - ant_parameters['w']
    data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
                        [-10, 10], linewidth=ant_parameters['w'] + 0.1, alpha=alpha, color='k')
    for wing in wings:
        if wing[0] == 'q':
            sign = -1
        else:
            sign = 1
        z = [Sz * ant_parameters[f'{wing}z0']]
        y = [0, 0]
        for i1 in range(3):
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
        y.pop()
        data_linewidth_plot(y, sign * np.array(z),
                            linewidth=ant_parameters['w'], alpha=alpha, color='b')
    wings = ['w3', 'q3']
    for wing in wings:
        if wing[0] == 'q':
            sign = -1
        else:
            sign = 1
        z = [Sz * ant_parameters[f'{wing}z0']]
        y = [Sy * ant_parameters['fx'], Sy * ant_parameters['fx']]
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        y.append(Sy * ant_parameters[f'{wing}y{1:d}'])
        data_linewidth_plot(y, sign * np.array(z),
                            linewidth=ant_parameters['w'], alpha=alpha, color='b')
    data_linewidth_plot([0, 0],
                        [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
                        linewidth=ant_parameters['w'], alpha=alpha, color='w')
    data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
                        [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
                        linewidth=ant_parameters['w'] + 0.1, alpha=alpha, color='r')
    plt.title('dimensions in mm')
    ax1.set_aspect('equal')
    # plt.show()
    return f
