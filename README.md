To generate the logs:

1. Open a shell at

```bash
"/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2"
```

2. Run the simulations with

```bash
uv run ./sample_params.py
```

The logs will be created in `tecs_analysis_2/artifacts`.

3. Run

```bash
~/user_programs/plotjuggler_ws/install/bin/plotjuggler -n -l "/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2/pj_layout.xml" -d logs/00000002.BIN &
```

to inspect the log.

4. Run

```bash
uv run ./parse_tecs_logs.py
```

to extract the response metadata from the logs.
