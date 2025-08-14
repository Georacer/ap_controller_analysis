# Notes

Thoughts and points to discuss in the presentation.

## Questions

- [ ] How does pitch control gain affect the metrics?
- [ ] Is there a relation between pitch rise time and the ideal TECS_TIME_CONST?
- [ ] Are there parameter combinations that are more unstable than sweeping one at a time?
  - E.g. TECS_VERT_ACC doesn't seem to do anything.
- [x] A higher TECS_INTEG_GAIN seems to help with airspeed transients and improves altitude transients too. Is there a downside?
- [x] Add metric for pitch demand oscillation.
- [ ] What does TECS_SPD_OMEGA help with? Show it. Might need a high-noise, high-lag airspeed source.
- [ ] What does TECS_HGT_OMEGA help with? Show it.
- [ ] Is there a system model that shows well why high values of TECS_PTCH_DAMP lead to pitch oscillation?
- [ ] Is there a set of parameters that bring out the positive effect of TECS_PTCH_DAMP?
- [ ] Are there tell-tale signs re. whether oscillation issues exist in the pitch-control side or throttle control side?
- [ ] Which parameter affects the maximum climb rate during the climbing segment?
- [ ] What can TECS_THR_DAMP help with?

## Remarks

- [ ] Too small TECS_TIME_CONST causes a lot of oscillation.
- [ ] Decreasing TECS_HDEM_TCONST is a clear way to decrease rise time. It also increases overshoot and climb rate error. Making this value too small causes oscillations in climb rate and pitch reference.
- [ ] Regarding TECS_PTCH_DAMP: It acts as a proportional gain regulating the relation from the Specific Energy Balance Derivative (SEBD) to the pitch demand. There is a feed-forward term, but may not fast enough, it goes with the natural pitch time constant. There are also integrators at play, but they are also slow. So TECS_PTCH_DAMP increases this regulation gain, and makes the SEBD system pole faster. But make it too fast and oscillations start to develop. These are probably stemming from inability of attitude control to follow the pitch reference (no "phase margin"), leading to inability to regulate kinetic and potential energy. This manifests as oscillation in airspeed and altitude, which feeds back into the pitch control.
  - In the simulation, values above 0.4 start raising major pitch oscillations and secondary airspeed and altitude oscillations and generally degraded control.
  - The beneficial effect of TECS_PTCH_DAMP isn't visible in the default simulation. Meaning that by tuning it you can only make things worse, not better.
- [ ] Increasing TECS_INTEG_GAIN too much leads to a high-frequency pitch oscillation. This is through the pitch demand mechanism, not the throttle demand integrator, at least for the default parameters.
  - Adding just a little bit (0.3 in the default simulation) helps with airspeed and altitude overshoot and rise time.
  - A non-zero value is quite necessary to have zero steady-state energy error (altitude and airspeed).
- [ ] TECS_HGT_OMEGA is applicable only if EKF can't provide a climb rate. So it doesn't apply by default.
- [ ] The difference between `SEBdot_dem` (TECS2.EBDD) and `SEBdom_dem_tot` (TECS2.EBDDT) is directly proportional to the `SEBdot_error`. Kind of a moot point, since we also have access to the error via TECS2.EBDD-TECS2.EBDE.
- [ ] TECS_SPD_OMEGA must not be set to zero. It will completely cripple the airspeed estimator, making it merely integrate longitudinal acceleration. This will lead either to overspeed or stall.
- [ ] TECS_THR_DAMP doesn't seem to have a positive effect in the default simulation. At 0 the performance is OK. As the value increases, the airspeed/altitude overshoot becomes more and more. This parameter seems to works as a true damper to energy regulation.
