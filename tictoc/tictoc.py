'''
author: Tobi Baumgartner
email: tobibaum@gmail.com
date: 03/03/16
'''
import math
import time
import psutil
from pandas import DataFrame
import pandas as pd
from collections import defaultdict
from toposort import toposort

class TicTocer(object):
    '''
    class to keep detailed timings for non-deterministic and varying execution paths
    '''
    def __init__(self, debug_memory=False):
        self.debug_memory = debug_memory
        self.timers = {}
        self.types = {}
        self.type_collects = defaultdict(dict)
        self.roll_mean_timers = defaultdict(lambda: {'n': 0, 
                                                     'mean': 0.,
                                                     'max': 0.,
                                                     'sq_mean': 0.,
                                                     'std': 0.})
        self.parents = {}
        self.prefix = ''
        self.prefix_stop = ''

    def tic(self, name, prefix=''):
        if self.prefix != '':
            name = self.prefix + name

        if prefix != '':
            self.prefix_stop = name
            self.prefix = prefix
            
        self.timers[name] = time.time()

        if self.debug_memory:
            self.types[name] = dict(psutil.virtual_memory()._asdict())
    
    def _dict_sum(self, *dicts):
        all_keys = [k for d in dicts for k in d]
        all_keys = set(list(all_keys))
        res_dict = {}

        for k in all_keys:
            val_sum = sum([d.get(k, 0) for d in dicts])
            if val_sum > 0:
                res_dict[k] = val_sum
        return res_dict

    def toc(self, name, print_it=False):
        if name == self.prefix_stop:
            self.prefix = ''

        if self.prefix != '':
            name = self.prefix + name

        # compute the time diff and update rolling mean stats
        time_taken = time.time() - self.timers[name]
        self.timers[name] = 0
        if print_it:
            print('%-40s took %.4f'%(name, time_taken))
        roll_max = self.roll_mean_timers[name]['max']
        roll_mean = self.roll_mean_timers[name]['mean']
        roll_sq_mean = self.roll_mean_timers[name]['sq_mean']
        n = self.roll_mean_timers[name]['n']
        if n == 0:
            new_roll_mean = time_taken
            new_roll_sq_mean = time_taken ** 2
        else:
            new_roll_mean = 1/float(n+1) * (n * roll_mean + time_taken)
            new_roll_sq_mean = 1/float(n+1) * (n * roll_sq_mean + time_taken**2)
        self.roll_mean_timers[name]['mean'] = new_roll_mean
        self.roll_mean_timers[name]['sq_mean'] = new_roll_sq_mean
        self.roll_mean_timers[name]['std'] = math.sqrt(new_roll_sq_mean - \
                                                       new_roll_mean**2)
        if time_taken > roll_max:
            self.roll_mean_timers[name]['max'] = time_taken

        self.roll_mean_timers[name]['n'] += 1

        # check which tics are active right now.
        if not name in self.parents:
            parents = set([p[0] for p in filter(lambda x: x[1]>0, self.timers.items())])
            self.parents[name] = parents

        if self.debug_memory:
            # compute number of types created
            new_types = dict(psutil.virtual_memory()._asdict())
            type_diff = {}
            for k, v_new in new_types.items():
                v_old = self.types[name].get(k, 0)
                v_diff = v_new - v_old 
                if v_diff != 0:
                    type_diff[k] = v_diff
            self.type_collects[name] = self._dict_sum(self.type_collects[name].copy(), type_diff)

    def print_timing_infos(self, reset=False):
        '''
        print out the average and std times for all tic-toced computations
        '''
        t_results = []
        for name, roll_means in self.roll_mean_timers.items():
            mean = roll_means['mean']
            maximum = roll_means['max']
            std = roll_means['std']
            n = roll_means['n']
            res = {'name': name,
                   'mean': mean,
                   'n': n,
                   'max': maximum,
                   'std': std,
                   'total': n*mean }
            t_results.append(res)
            if reset:
                roll_means['mean'] = 0
                roll_means['max'] = 0
                roll_means['name'] = 0
                roll_means['n'] = 0
        df_results = DataFrame(t_results)
        df = df_results[['name', 'n', 'total', 'mean', 'max']]

        # left justify all the names.

        try:
            assert(sum(self.timers.values()) == 0)
        except Exception as e:
            print('===tictoc ERROR===')
            print('not all timers were closed in loop')
            print('this probably means some escapes via "continue" or missing "tocs"')
            open_timers = [k for k, v in self.timers.items() if v!=0]
            print('open timers:', open_timers)
            print('===tictoc ERROR===')
            raise e

        order = []
        topo = list(toposort(self.parents))
        for level in topo:
            for n in list(level):
                if not n in order:
                    order.append(n)
                # check whether any new children can be added now.
                len_before = len(order)
                while True:
                    for k, v in sorted(self.parents.items(), key=lambda x:-len(x[1])):
                        if len(v - set(order)) == 0:
                            if not k in order:
                                order.append(k)
                                break
                    if len_before == len(order):
                        break
                    len_before = len(order)

        remain = set(self.timers.keys()) - set(order)
        order = list(remain) + order

        index_order = [list(df['name']).index(a) for a in order]
        name_to_level = dict([[t, l] for l, v in enumerate(topo) for t in v])
        for r in remain:
            name_to_level[r] = 0
        df = df.iloc[index_order]
        df['name'] = ['|  '*name_to_level[d] + d for d in df['name']]
        max_name_len = max([len(d) for d in df['name']])
        df['name'] = [d.ljust(max_name_len) for d in df['name']]
        df = df.reset_index(drop=True)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', lambda x: '%.2f'%(x*1000))

        print('')
        print(df)

        if self.debug_memory:
            df_types = DataFrame(self.type_collects)
            df_types[df_types.isnull()] = 0
            df_types /= 1e6 # display in ~MB
            print(df_types.T)

def test_simple():
    tt = TicTocer()

    print('running the example, should take ~5s')
    seed = 0
    tt.tic('outer')
    if True:
        time.sleep(1)
        tt.tic('inner')
        if True:
            time.sleep(1)
        if True:
            time.sleep(1)
            tt.tic('inner1_inner1')
            time.sleep(1)
            tt.toc('inner1_inner1')
            tt.tic('inner1_inner2')
            time.sleep(1)
            tt.toc('inner1_inner2')
        tt.toc('inner')
        tt.tic('inner2')
        if True:
            time.sleep(1)
            tt.tic('inner2_inner1')
            time.sleep(1)
            tt.toc('inner2_inner1')
            tt.tic('inner2_inner2')
            time.sleep(1)
            tt.toc('inner2_inner2')
        tt.toc('inner2')
    tt.toc('outer')

    tt.print_timing_infos()

if __name__=='__main__':
    test_simple()
