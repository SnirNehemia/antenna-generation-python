
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
        parameters_names.append(f'w{iw + 1:d}z{0}')
        for i1 in range(3):
            if iw==2 and i1>=2:
                continue
            parameters_names.append(f'w{iw+1:d}z{i1+1:d}')
            parameters_names.append(f'w{iw + 1:d}y{i1 + 1:d}')
    for iw in range(3):
        parameters_names.append(f'q{iw + 1:d}z{0}')
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
    ant_parameters['fx'] = min([abs(np.round(np.random.normal(scale=0.5), decimals=1)),1])
    Sz = (model_parameters['Sz'] - model_parameters['feed_length'] / 2)
    Sy = model_parameters['Sy']
    wing_names = ['w','q']
    last_z = -1
    while not valid_ant:
        for key in parameters_names:
            ant_parameters[key] = np.max([np.round(np.random.uniform(),decimals=1),0.1])
        for wing_name in wing_names:
            for wing in range(3):
                wing = wing +1
                if Sz > 60:
                     last_z = min([abs(np.round(np.random.normal(scale=0.5), decimals=1)), 1])
                     sign_z = -1
                else:
                    last_z = np.round(np.random.uniform(),decimals=1)
                    sign_z = (-1) ** np.random.randint(2)
                last_y = np.round(np.random.uniform(), decimals=1)
                sign_y = (-1) ** np.random.randint(2)

                # if wing < 3:
                #     sign_y = +1
                #     last_y = 0.1
                # else:
                #     sign_y = (-1) ** np.random.randint(2)
                #     last_y = max([min([ant_parameters['fx'] + sign_y * 0.1, 1]),0])
                np.round(np.random.uniform(), decimals=1)

                ant_parameters[f'{wing_name}{wing:.0f}z1'] = last_z
                ant_parameters[f'{wing_name}{wing:.0f}y1'] = last_y

                for sub_wing in range(3):
                    sub_wing = sub_wing + 1
                    if wing==3 and sub_wing==3: continue
                    # last_z = max([min([last_z + np.round(np.random.uniform()*0.2-0.1, 1),1]),0])

                    if last_z <= 0.1: sign_z = 1
                    if last_z >= 0.9: sign_z = -1
                    if last_y <= 0.1: sign_y = 1
                    if last_y >= 0.9: sign_y = -1
                    last_z = last_z + sign_z * 0.1
                    last_y = last_y + sign_y * 0.1
                    ant_parameters[f'{wing_name}{wing:.0f}y{sub_wing:.0f}'] = last_y
                    ant_parameters[f'{wing_name}{wing:.0f}z{sub_wing:.0f}'] = last_z
        # wings = ['w1', 'w2', 'q1', 'q2']
        #     for wing in wings:
        ant_parameters['w'] = np.random.randint(1, 15)
        ant_parameters['q3z0'] = np.round(np.random.uniform(), decimals=1)#np.random.choice([0, 0.1])
        ant_parameters['w3z0'] = np.round(np.random.uniform(), decimals=1)#np.random.choice([0, 0.1])
        for key in parameters_names:
            ant_parameters[key] = np.round(ant_parameters[key], decimals=1)
        valid_ant = check_ant_validity(ant_parameters,model_parameters)
        count_retries += 1
        if count_retries%1000 == 0:
            print(f'retried {count_retries:d} times, trying some more')
    print(f'retried {count_retries:d} times')
    return ant_parameters

def check_ant_validity(ant_parameters,model_parameters):
    Sz = (model_parameters['Sz'] - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['Sy'] - ant_parameters['w']
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
        if ant_parameters[f'{wing}y1'] < ant_parameters['w'] / Sy: return 0
        if ant_parameters[f'{wing}y2'] < ant_parameters['w'] / Sy: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y1']) < ant_parameters['w']/Sy: return 0
        if np.abs(ant_parameters[f'{wing}y1'] - ant_parameters[f'{wing}y3']) < ant_parameters['w']/Sy: return 0
        if np.abs(ant_parameters[f'{wing}y2'] - ant_parameters[f'{wing}y3']) < ant_parameters['w']/Sy: return 0
    if (Sz * ant_parameters[f'q1z3'] - ant_parameters['w']/2 <= 5
        and (ant_parameters[f'q1y3'] < ant_parameters['fx'] < ant_parameters[f'q1y2'] or
            ant_parameters[f'q1y2'] < ant_parameters['fx'] < ant_parameters[f'q1y3'])): return 0
    if (Sz * ant_parameters[f'w1z3'] - ant_parameters['w']/2 <= 5
        and (ant_parameters[f'w1y3'] < ant_parameters['fx'] < ant_parameters[f'w1y2'] or
            ant_parameters[f'w1y2'] < ant_parameters['fx'] < ant_parameters[f'w1y3'])): return 0
    wings = ['w1', 'w2','w3', 'q1', 'q2','q3']
    for wing in wings:
        if np.abs(ant_parameters[f'{wing}z0'] - ant_parameters[f'{wing}z1']) <= ant_parameters['w'] / Sz: return 0
    if np.min([ant_parameters[f'q3z0'],ant_parameters[f'w3z0']]) > 0.2: return 0
    return 1

def save_figure(model_parameters,ant_parameters, output_path, run_ID, alpha=1):
    plt.ioff()
    f, ax1 = plt.subplots()
    wings = ['w1', 'w2', 'q1', 'q2']
    Sz = (model_parameters['Sz'] / 2 - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['Sy'] - ant_parameters['w']
    data_linewidth_plot([Sy * ant_parameters['fx'], Sy * ant_parameters['fx']],
                        [-10,10], linewidth=ant_parameters['w'] + 0.1, alpha=alpha, color='k')
    for wing in wings:
        if wing[0]=='q':
            sign=-1
        else:
            sign=1
        z = [Sz * ant_parameters[f'{wing}z0']]
        y = [0, 0]
        for i1 in range(3):
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
            y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
        y.pop()
        data_linewidth_plot(y, sign*np.array(z),
                            linewidth=ant_parameters['w']-0.01, alpha=alpha, color='b')
    wings = ['w3', 'q3']
    for wing in wings:
        if wing[0]=='q':
            sign=-1
        else:
            sign=1
        z = [Sz * ant_parameters[f'{wing}z0']]
        y = [Sy * ant_parameters['fx'], Sy * ant_parameters['fx']]
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
        y.append(Sy * ant_parameters[f'{wing}y{1:d}'])
        data_linewidth_plot(y, sign*np.array(z),
                            linewidth=ant_parameters['w']-0.01, alpha=alpha, color='b')
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