# Notes

Thoughts and points to discuss in the presentation.

## Questions

- [ ] What does TECS_PTCH_DAMP help with? Show it.
- [ ] How does pitch control gain affect the metrics?
- [ ] Are there parameter combinations that are more unstable than sweeping one at a time?
  - E.g. TECS_VERT_ACC doesn't seem to do anything.
- [x] A higher TECS_INTEG_GAIN seems to help with airspeed transients and improves altitude transients too. Is there a downside?
- [x] Add metric for pitch demand oscillation.
- [ ] What does TECS_SPD_OMEGA help with? Show it. Might need a high-noise, high-lag airspeed source.
- [ ] What does TECS_HGT_OMEGA help with? Show it.

## Remarks

- [ ] Increasing TECS_PTCH_DAMP increases airspeed undershoot during prolonged sinks.
- [ ] Increasing TECS_PTCH_DAMP increases altitude overshoot in step inputs.
- [ ] Too small TECS_TIME_CONST causes a lot of oscillation.
- [ ] TECS_HDEM_CONST is a clear way to decrease rise time. It also increases overshoot.
- [ ] TECS_PTCH_DAMP from 0.5 to 0.8 excites a bad oscillation. It doesn't exist in lower values.
- [ ] The beneficial effect of TECS_PTCH_DAMP isn't visible in the default simulation.
- [ ] TECS_HGT_OMEGA is applicable only if EKF can't provide a climb rate. So it doesn't apply by default.
- [ ] Increasing TECS_INTEG_GAIN too much leads to a high-frequency pitch oscillation. This is through the pitch demand mechanism, not the throttle demand integrator, at least for the default parameters.
