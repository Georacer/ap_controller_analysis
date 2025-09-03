# Notes

Thoughts and points to discuss in the presentation.

## Questions

- [ ] Is there a relation between pitch rise time and the ideal TECS_TIME_CONST?
- [ ] Are there parameter combinations that are more unstable than sweeping one at a time?
  - E.g. TECS_VERT_ACC doesn't seem to do anything.
- [ ] What does TECS_SPD_OMEGA help with? Show it. Might need a high-noise, high-lag airspeed source.
- [ ] What does TECS_HGT_OMEGA help with? Show it.
- [ ] Is there a system model that shows well why high values of TECS_PTCH_DAMP lead to pitch oscillation?
- [ ] Is there a set of parameters that bring out the positive effect of TECS_PTCH_DAMP?
- [ ] What can TECS_THR_DAMP help with?
  - In the PTCH2SRV_RMAX_UP=2 example, it helps a little with the initial damping, but can't completely dampen the oscillation.
- [ ] Ensure that in the run of AIRSPEED_CRUISE=30 the `integSEB_delta` is very large and causes the pitch integrators to freeze.
- [ ] Why does TEC3.PEDD stay 0 during the climb? Does it pull from TECS.hin?
- [ ] \_SPEdot_dem is defined as the difference between desired and achieved altitude. So in constant climbs it is very small. It would be better perhaps if there was a feed-forward gain based on the desired climb rate? Especially since `_SPEdot` is actually pulling from the real climb rate.
- [ ] How repeatable are the sampling runs?

## Remarks

### Common parameters

- [x] Too small TECS_TIME_CONST causes a lot of oscillation.
- [x] Decreasing TECS_HDEM_TCONST is a clear way to decrease rise time. It also increases overshoot and climb rate error. Making this value too small causes oscillations in climb rate and pitch reference.
  - TECS_HDEM_TCONST might be a more efficient way to dampen oscillations in case of a too slow pitch loop.

### Pitch control issues

- [x] Too slow a pitch control is detrimental to TECS. It can be that climb behaves differently to descent. Oscillations might happen due to the TECS pitch command saturating, triggering max_climb/descent wind-downs. However, TECS has its own pitch integrator, so it can at least reduce the steady-state error.
  - TECS_TIME_CONST=5, PTCH2SRV_TCONST=2.6 is a very good example of what a slow pitch loop can do by default to TECS.
- [x] Too jittery a pitch angle control is indeed detrimental.
- [x] In general it's hard to tell apart pitch control vs throttle control issues. In theory, energy balance issues relates to pitch control and energy/energy-rate issues relate to throttle control. But even though the corresponding error and demand signals are available, there's a lot of cross-talk.
  - For example, an isolated altitude rise demand (constant climb rate), will introduce a demand in pitch AND in throttle.
- [x] Regarding TECS_PTCH_DAMP: It acts as a proportional gain regulating the relation from the Specific Energy Balance Derivative (SEBD) to the pitch demand. There is a feed-forward term, but may not fast enough, it goes with the natural pitch time constant. There are also integrators at play, but they are also slow. So TECS_PTCH_DAMP increases this regulation gain, and makes the SEBD system pole faster. But make it too fast and oscillations start to develop. These are probably stemming from inability of attitude control to follow the pitch reference (no "phase margin"), leading to inability to regulate kinetic and potential energy. This manifests as oscillation in airspeed and altitude, which feeds back into the pitch control.
  - In the simulation, values above 0.4 start raising major pitch oscillations and secondary airspeed and altitude oscillations and generally degraded control.
  - The beneficial effect of TECS_PTCH_DAMP isn't visible in the default simulation. Meaning that by tuning it you can only make things worse, not better.
- [x] Increasing TECS_INTEG_GAIN too much leads to a high-frequency pitch oscillation. This is through the pitch demand mechanism, not the throttle demand integrator, at least for the default parameters.
  - Adding just a little bit (0.3 in the default simulation) helps with airspeed and altitude overshoot and rise time.
  - A non-zero value is quite necessary to have zero steady-state energy error (altitude and airspeed).

### Max/min climb performance

- [x] TECS_CLMB_MAX will be capped as max_climb_condition probably due to expected pitch saturation well before throttle saturation. Same for TECS_SINK_MIN.
- [x] When PTCH_LIM_MAX_DEG is set past the required pitch for a max climb, then any higher value isn't harmful.
- [x] Both a max pitch and max throttle will trigger a max climb condition, leading to reduction of climb rate limit. So don't try to hit a sustained climb with 100% throttle.
- [ ] During an overspeed dive, the unconstrained pitch can easily hit the lower limit. The `integSEB_delta` is probably large enough that the integrators aren't wound any more. This results in pitch not reducing anymore and the descent rate isn't being met. In general the max descent condition is overly pessimistic.

### Other parameters

- [x] TECS_HGT_OMEGA is applicable only if EKF can't provide a climb rate. So it doesn't apply by default.
- [x] TECS_SPD_OMEGA must not be set to zero. It will completely cripple the airspeed estimator, making it merely integrate longitudinal acceleration. This will lead either to overspeed or stall.

### Unclear parameter effects

- [x] TECS_THR_DAMP doesn't seem to have a positive effect in the default simulation. At 0 the performance is OK. As the value increases, the airspeed/altitude overshoot becomes more and more. This parameter seems to works as a true damper to energy regulation.

## Don't forget

- [x] Explain methodology.
- [x] Mention FFT details.
- [x] Mention total number of simulations.
- [x] When discussing the effect of pitch tuning, show some attitude control plots.
- [x] Mention PlotJuggler and my layout.
- [x] Mention the DrawIO diagram.
- [x] Ask for TECS questions and logs.
