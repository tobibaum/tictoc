# TicTocer
This tool helps to time computation times of non-deterministic program flows. similar to any tic-toc it keeps the timing for the encapsulated functions. on top of that it also keeps track of the average time a single operation (or lines of code) took and how often it has been invoked over the entire execution process. and examplar output could look like this:

```
                  name  n     total      mean  std
0  outer                1  8.030651  8.030651  0.0
1  |  inner2            1  3.010727  3.010727  0.0
2  |  |  inner2_inner1  1  1.002265  1.002265  0.0
3  |  |  inner2_inner2  1  1.005126  1.005126  0.0
4  |  inner             1  4.015616  4.015616  0.0
5  |  |  inner1_inner1  1  1.002225  1.002225  0.0
6  |  |  inner1_inner2  1  1.005101  1.005101  0.0
```
Here, `name` is the string inside the tic/toc call pair. `n` is the number of times
it has been evoke, together with the `total`, `mean` and standard variation `std` times for
these operations.

This can be very helpful when designing an algorithm and trying to measure, which programs
paths are chosen and how much of the overall computation time they take.

### Usage
```
from tictoc import TicTocer

tt = TicTocer()

seed = 0
tt.tic('outer')
if True:
    time.sleep(2)
    tt.tic('inner')
    if True:
        time.sleep(4)
    tt.toc('inner')
    tt.tic('inner2')
    if True:
        time.sleep(1)
    tt.toc('inner2')
tt.toc('outer')

tt.print_timing_infos()

# the printed output looks like this:
#    name       n     total      mean  std
# 0  outer      1  7.007666  7.007666    0
# 1  |  inner2  1  1.001172  1.001172    0
# 2  |  inner   1  4.004073  4.004073    0
```


### Debug memory leaks
Yep, python leaks sometimes. this can quickly kill a process and is hard to debug.
Run `TicTocer` with:
```
tt = TicTocer(debug_memory=True)
```
to get memory consumption stats for each of the tic/toc pairs.

Example output:
```
                       active  available   buffers     cached       free  inactive       percent         used
function 1           5.033984   0.028672  0.000000   0.552960   0.000000  0.327680  1.000000e-07     4.907008
function 2           6.336512  27.840512  0.016384   1.699840  14.000128  0.843776  4.000000e-07     8.007680
func3                0.000000   0.000000  0.000000   0.000000   0.000000  0.000000  0.000000e+00     0.000000
the leak!         2814.636032   0.000000  0.012288   0.409600   0.000000  0.000000  8.400000e-06  2819.923968
inner func4          7.376896  27.394048  0.012288   1.646592  33.767424  0.000000  2.000000e-07     1.560576
eval                 0.081920   0.000000  0.000000   0.000000   0.000000  0.000000  0.000000e+00     0.286720
fix                  0.000000   0.000000  0.000000   0.000000   0.000000  0.000000  0.000000e+00     0.000000
load data         1482.641408   0.000000  0.004096   0.045056   0.000000  0.000000  4.400000e-06  1481.949184
```

This is a simple wrapper around `psutil.virtual_memory()`, so check the docs here:
https://psutil.readthedocs.io/en/latest/#memory


WARNING!! debugging the memory will mess up your other timings, so for proper time taken measurements, turn off memory profile.
