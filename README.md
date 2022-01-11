# PyPhyUtils
This is a small python package containing utility functions for parsing IQ-Tree, RAxML-NG, and RAxML8 log files that I use frequently.

Note that the functions are currently untested and incomplete. Furthermore, the functions rely on regex parsing, so in 
case the logging outout of any of the programs changes, the functions might not work anymore.

Currently implemented functions:
* Get final likelihood, execution time, random seed, starting tree type and run parameters from RAxML-NG log files
* Get final likelihood, execution time and run parameters from IQ-Tree log files
* Get execution time from RAxML8 log files
* Get results of the statistical tests from IQ-Tree .iqtree files
* Get results of the statisical tests from RAxML8 log files
* Get average RF-Distance, pairwise distances from RAxML-NG log files  

You can install it as pip package:
```shell
cd PyPhyUtils && pip install -e .
```