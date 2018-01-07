import numpy as np
import pyfmi


def variables_by_causality(slave, causality):
    mvs = slave.get_model_variables().keys()
    return [mv for mv in mvs if slave.get_variable_causality(mv) == causality]

def inputs(slave):
    return variables_by_causality(slave, pyfmi.fmi.FMI2_INPUT)

def outputs(slave):
    return variables_by_causality(slave, pyfmi.fmi.FMI2_OUTPUT)

def _initialize(slaves, connections):
    for sy in slaves:
        for y in outputs(slaves[sy]):
            value = slaves[sy].get(y)

    for _ in slaves: # repeat n times
        for su in slaves:
            for u in inputs(slaves[su]):
                sy, y = connections[su, u]
                v = slaves[sy].get(y)
                slaves[su].set(u, v)


def run(fmus, connections, sequence, dt, t0, tEnd):
    
    slaves = dict()
    for name, fmu in fmus.items():
        slave = pyfmi.load_fmu(fmu['archivePath'])
        slave.setup_experiment()
        slave.enter_initialization_mode()
        for parameter, value in fmu['parameters'].items():
            slave.set(parameter, float(value))
        slaves[name] = slave

    _initialize(slaves, connections)
    for s in slaves:
        slaves[s].exit_initialization_mode()

    
    values = dict()
    for name, slave in slaves.items():
        for y in outputs(slave):
            values[name, y] = [(0., slave.get(y)[0])]

    t = t0
    while t < tEnd:
        for name in sequence:
            slave = slaves[name]
            for u in inputs(slave):
                s, y = connections[name, u]
                v = slaves[s].get(y)
                slave.set(u, v)

            slave.do_step(t0, dt, pyfmi.fmi.FMI2_TRUE)

            for y in outputs(slave):
                v = slave.get(y)
                values[name, y].append((t + dt, v[0]))
        t = t + dt
                
    for signal in values:
        values[signal] = np.array(values[signal]).T

    return values

