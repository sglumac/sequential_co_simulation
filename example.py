import master
import configuration
import sequence

import matplotlib.pyplot as plt
import numpy as np

import os
import sys
import itertools


fmuDir = sys.argv[1]

fig, axs = plt.subplots(6, 2, sharex=True, sharey=True)

slaveNames = ['Step', 'Gain', 'Subtraction']
sequences = list(itertools.permutations(range(3)))

fmus, connections = configuration.read(fmuDir, 'StepSubtraction.xml')
dt = .25
t0, tEnd = 0., 2.

axs[0, 0].set_title('Gain, y2')
axs[0, 1].set_title('Subtraction, y3')
for idx in range(6):
    sequenceIdx = tuple(slaveNames[i] for i in sequences[idx])

    print "The master is producing data for the sequence {0} -> {1}".format(sequences[idx], sequenceIdx)
    data = master.run(fmus, connections, sequenceIdx, dt, t0, tEnd)

    ax = axs[idx, 0]
    t2s, y2s = data[('Gain', 'y')]
    ax.step(t2s, t2s > 1, 'r--')
    ax.stem(t2s, y2s, color='red', basefmt='--')
    plt.xlim([t0, tEnd])
    ax.set_ylabel(r'$\sigma$ = {0}'.format(sequences[idx]))

    ax = axs[idx, 1]
    t3s, y3s = data[('Subtraction', 'y')]
    ax.step(t2s, np.zeros(t2s.shape), 'r--')
    ax.stem(t3s, y3s, basefmt='--')
    plt.xlim([t0, tEnd])

fig.set_size_inches(12, 16)

plt.show()

sequences = sequence.calculate(connections)
sequencesIndices = [tuple(map(slaveNames.index, sequenceNames)) for sequenceNames in sequences]
print "The constraint programming algorithm calculated the set of calling sequences {0}".format(sequences)
print "In terms of slave indices the set is equal to {0}".format(sequencesIndices)

