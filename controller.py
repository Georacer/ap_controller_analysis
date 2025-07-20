"""Module containing controller models."""

import sympy as sp
from penbegone import common as bgcom

import plant as p  # Import the plant to get already defined symbolic variables.

###############################################################################
# Shared symbolic variables.
###############################################################################

KE = sp.symbols("x_{KE}", real=True)
KE_int = sp.symbols("x_{intKE}", real=True)
SEB_dot = sp.symbols("x_{SEB}", real=True)
SEB_dot_int = sp.symbols("x_{intsebdot}", real=True)
STEdot_max = sp.symbols("Edot^*_max", real=True)
STEdot_min = sp.symbols("Edot^*_min", real=True)
STEdot_neg_max = sp.symbols("Edot^*_nmax", real=True)
THR_state = sp.symbols("x_{THR}", real=True)
climb_max = sp.symbols("hdot_cmax", real=True)  # Unused
h_dem = sp.symbols("h_d", real=True)
h_dem_dot = sp.symbols("h_d_dot", real=True)
integTHR_state = sp.symbols("x_{intthr}", real=True)
sink_max = sp.symbols("hdot_smax", real=True)  # Unused
sink_min = sp.symbols("hdot_smin", real=True)  # Unused
thr_max = sp.symbols("thr_{max}", real=True)
thr_min = sp.symbols("thr_{min}", real=True)
thr_trim = sp.symbols("thr_{trim}", real=True)
v_c = sp.symbols("v_cruise", real=True)
v_dem = sp.symbols("v_d", real=True)
v_dem_dot = sp.symbols("v_d_dot", real=True)
v_max = sp.symbols("V_max", real=True)
v_min = sp.symbols("V_min", real=True)  # Unused

# Gains
k_i = sp.symbols("k_i", real=True)  # TECS_INTEG_GAIN
k_pd = sp.symbols("k_pd", real=True)  # TECS_PITCH_DAMP
k_tc = sp.symbols("k_tc", real=True)  # TECS_TIME_CONST
k_td = sp.symbols("k_td", real=True)  # TECS_THR_DAMP
w = sp.symbols("w", real=True)  # TECS_SPDWEIGHT


###############################################################################
# Models
###############################################################################

def tecs_full():
    """
    Returns the nonlinear model of the TECS controller.

    The controller has the following symbolic variables as inputs:
        v_dem (There's also v_dem_dot, but not considered for now.)
        h_dem

    The controller has the following symbolic variables as parameters:
        

    The controller has the form dot{x}=f(x, u) with states:
        SEB_dot_int, with derivative SEB_dot. Named _integSEBdot in TECS.
        KE_int, with derivative KE. Named _integKE in TECS.
        integTHR_state, with derivative THR_state. _integTHR_state in TECS.

    The controller has the following outputs:
        throttle
        pitch
    """

    controller = bgcom.Equations()
    controller_states = []
    controller_inputs = [v_dem, h_dem]
    controller_outputs = [p.throttle, p.pitch]

    STEdot_max_ = p.g*climb_max
    STEdot_min_ = -p.g*sink_min
    STEdot_neg_max_ = -p.g*sink_max

    # _update_speed_demand

    # Perhaps the increase of _TAS_dem when at max sink plays a role?

    vel_rate_max_ = 0.5*STEdot_max_/p.v
    vel_rate_neg_cruise = 0.9*STEdot_min_/v_c
    vel_rate_neg_max = 0.9*STEdot_min_/v_max

    # I can add the LPF effect of TIME_CONST here, instead of pure differentiation.
    # controller_states = [v_dem]

    # _update_height_demand

    # Can add the LPF effect of HDEM_TCONST here, over h_dem.
    # controller_states.append(h_dem)

    # _update_energies

    SPE_dem_ = h_dem*p.g
    SKE_dem_ = 0.5*v_dem*v_dem
    SKE_est_ = 0.5*p.v*p.v
    SKE_dot_dem_ = p.v*v_dem_dot  # In the source vdot_dem_ is high-passed. How does this translate to the actual system?
    SKE_dot_ = p.v*p.v_dot_  # Same comment as above.
    SPE_est_ = p.h*p.g
    SPE_dot_ = p.h_dot_*p.g

    # _update_pitch

    w_k_ = w
    w_p_ = 2-w

    SEB_dem_ = SPE_dem_*w_p_ - SKE_dem_*w_k_
    SEB_est_ = SPE_est_*w_p_ - SKE_est_*w_k_
    SEB_err_ = SEB_dem_ - SEB_est_
    SEB_dot_est_ = SPE_dot_*w_p_ - SKE_dot_*w_k_

    SEB_dot_dem_ = SEB_err_/k_tc + h_dem_dot*p.g*w_p_
    SEB_dot_err_ = SEB_dot_dem_ - SEB_dot_est_
    SEB_dot_dem_tot_ = SEB_dot_dem_ + SEB_dot_err_*k_pd

    # Adding integrator states.
    controller_states.append(SEB_dot_int)
    SEB_dot_int_dot_ = SEB_dot_err_*k_i
    controller.add(SEB_dot, SEB_dot_int_dot_)

    controller_states.append(KE_int)
    KE_int_dot_ = (SKE_est_ - SKE_dem_)*w_k_/k_tc
    controller.add(KE, KE_int_dot_)

    pitch_dem_ = (SEB_dot_dem_tot_ + SEB_dot_int + KE_int) / (p.v * p.g)

    # _update_throttle_with_airspeed

    STE_error_ = SKE_dem_ - SKE_est_ + SPE_dem_ - SPE_est_
    SPE_dot_dem_ = (SPE_dem_ - SPE_est_)/k_tc
    STE_dot_dem_ = SPE_dot_dem_ + SKE_dot_dem_
    STE_dot_err_ = STE_dot_dem_ - SKE_dot_ - SPE_dot_

    K_thr2STE_ = (STEdot_max_ - STEdot_min_)/(thr_max - thr_min)
    K_STE2Thr_ = 1 / (K_thr2STE_ * k_tc)
    # Adding integrator state.
    controller_states.append(integTHR_state)
    integTHR_state_dot_ = STE_error_*k_i*K_STE2Thr_
    controller.add(THR_state, integTHR_state_dot_)

    ff_throttle = STE_dot_dem_/K_thr2STE_ + thr_trim

    throttle_dem_ = K_STE2Thr_*(STE_error_ + STE_dot_err_*k_td) + ff_throttle + integTHR_state
    controller_states_derivatives = [SEB_dot, KE, THR_state]

    controller.add(p.throttle, throttle_dem_)
    controller.add(p.pitch, pitch_dem_)
    # Perhaps return the dynamic state too, so that it can be turned into a SS system?

    return controller, controller_states, controller_states_derivatives, controller_inputs, controller_outputs
