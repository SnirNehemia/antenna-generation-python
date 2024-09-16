
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
        for i1 in range(3):
            if iw==2 and i1>=2:
                continue
            parameters_names.append(f'w{iw+1:d}z{i1+1:d}')
            parameters_names.append(f'w{iw + 1:d}y{i1 + 1:d}')
    for iw in range(3):
        for i1 in range(3):
            if iw==2 and i1>=2:
                continue
            parameters_names.append(f'q{iw+1:d}z{i1+1:d}')
            parameters_names.append(f'q{iw + 1:d}y{i1 + 1:d}')
    return parameters_names

def randomize_ant(parameters_names,model_parameters,seed=0):
    ant_parameters = {}
    if seed > 0:
        np.random.seed(seed)
    valid_ant = 0
    count_retries = 0
    ant_parameters['fx'] = np.round(np.random.uniform(), decimals=1)
    while not valid_ant:
        for key in parameters_names:
            ant_parameters[key] = np.max([np.round(np.random.uniform(),decimals=1),0.1])
        ant_parameters['w'] = np.random.randint(1, 5)
        ant_parameters['q1z3'] = np.round(np.random.uniform(),decimals=1)
        ant_parameters['w1z3'] = np.round(np.random.uniform(), decimals=1)
        Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
              - model_parameters['feed_length'] / 2)
        Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
        valid_ant = check_ant_validity(ant_parameters,Sz,Sy)
        count_retries += 1
        if count_retries%1000 == 0:
            print(f'retried {count_retries:d} times, trying some more')
    print(f'retried {count_retries:d} times')
    return ant_parameters

def check_ant_validity(ant_parameters,Sz,Sy):
    wings = ['w1','w2','q1','q2']
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
        if np.abs(ant_parameters[f'{wing}z2'] - ant_parameters[f'{wing}z1']) < ant_parameters['w']/Sz: return 0
        if np.abs(ant_parameters[f'{wing}z1'] - ant_parameters[f'{wing}z3']) < ant_parameters['w']/Sz: return 0
        if np.abs(ant_parameters[f'{wing}z2'] - ant_parameters[f'{wing}z3']) < ant_parameters['w']/Sz: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y1']) < ant_parameters['w']/Sz: return 0
        if np.abs(ant_parameters[f'{wing}y1'] - ant_parameters[f'{wing}y3']) < ant_parameters['w']/Sz: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y3']) < ant_parameters['w']/Sz: return 0
    return 1

def save_figure(model_parameters,ant_parameters, output_path, run_ID, alpha=1):
    plt.ioff()
    f, ax1 = plt.subplots()
    wings = ['w1', 'w2', 'q1', 'q2']
    Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']

    for wing in wings:
        if wing[0]=='q':
            sign=-1
        else:
            sign=1
        z = [model_parameters['feed_length'] / 2]
        y = [0, 0]
        for i1 in range(3):
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
        y.pop()
        data_linewidth_plot(y, sign*np.array(z),
                            linewidth=ant_parameters['w'], alpha=alpha, color='b')
    wings = ['w3', 'q3']
    for wing in wings:
        if wing[0]=='q':
            sign=-1
        else:
            sign=1
        z = [model_parameters['feed_length'] / 2]
        y = [Sy * ant_parameters['fx'], Sy * ant_parameters['fx']]
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        y.append(Sy * ant_parameters[f'{wing}y{1:d}'])
        data_linewidth_plot(y, sign*np.array(z),
                            linewidth=ant_parameters['w'], alpha=alpha, color='b')
    data_linewidth_plot([0, 0],
                        [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
                        linewidth=ant_parameters['w'], alpha=alpha, color='w')
    data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
                        [model_parameters['feed_length'] / 2, -model_parameters['feed_length'] / 2],
                        linewidth=ant_parameters['w']+0.1, alpha=alpha, color='r')
    plt.title('dimensions in mm')
    ax1.set_aspect('equal')
    plt.show(block=False)
    f.savefig(output_path + '\\output\\model_pictures\\image_' + str(run_ID) + '.png')
    plt.close(f)

# a = get_parameters_names()
# aa = randomize_ant(a,20,32,2)