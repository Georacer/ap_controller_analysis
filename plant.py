"""Module containing plant models. Does not contain controllers.

# Conventions
# A: sympy symbol
# A_: expression
# A__: evaluated expression or symbol
"""

import sympy as sp
from penbegone import common as bgcom

###############################################################################
# Shared symbolic variables.
###############################################################################

t = sp.symbols("t", real=True)  # Time.

F_t = sp.symbols("F_t", real=True)  # Maximum thrust, N.
S = sp.symbols("S", real=True)  # Aerodynamic surface, m^2.
c_drag = sp.symbols("C_drag", real=True)  # Coefficient of drag.
g = sp.symbols("g", real=True)  # Acceleration of gravity, m/s^2.
h = sp.symbols("h", real=True)  # Altitude, m.
h_dot = sp.symbols("h_dot", real=True)  # Derivative of altitude (climb rate), m/s.
m = sp.symbols("m", real=True)  # Mass, kg.
pitch = sp.symbols("theta", real=True)  # Pitch angle, rad.
rho = sp.symbols("rho", real=True)  # Air density, kg/m^3.
theta_0 = sp.symbols("theta_0", real=True)  # Trim pitch, rad.
throttle = sp.symbols("delta_t", real=True)  # Throttle, 0-1.
v = sp.symbols("v", real=True)  # Airspeed, m/s.
v_dot = sp.symbols("v_dot", real=True)  # Derivative of airspeed, m/s^2.

###############################################################################
# Shared symbolic functions of time.
###############################################################################

# v = bgcom.functions("v", t)  # Airspeed, m/s.
# h = bgcom.functions("h", t)  # Altitude, m.
h_dot_ = sp.diff(h, t)
v_dot_ = sp.diff(v, t)


###############################################################################
# Models
###############################################################################
def build_longitudinal_nonlinear_model():
    """
    Returns the nonlinear model of the longitudinal aircraft dynamics.

    The system has the following symbolic variables as inputs:
        pitch
        throttle

    The system has the following symbolic variables as parameters:
        m
        F_t
        c_drag
        rho
        theta_0

    The model has the form dot{x}=f(x) with states:
        v
        h
    """
    drag_ = 0.5*S*rho*v*v*c_drag
    f_v_dot_ = 1/m*(-sp.sin(pitch)*g + F_t*throttle - drag_)
    f_h_dot_ = v*sp.sin(pitch-theta_0)  # Perhaps add effect of increasing lift as airspeed increases?

    eqs = bgcom.Equations()
    eqs.add(v_dot, f_v_dot_)
    eqs.add(h_dot, f_h_dot_)

    return eqs
