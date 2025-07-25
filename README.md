To generate the logs:

1. Open a shell at

```bash
"/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2/temp_dir"
```

2. Enter

```bash
pyenv shell system
```

to use the system Python and not the one in this venv.

3. Run the autotest with

```bash
clear; /home/george/projects_no_dropbox/ardupilot/Tools/autotest/autotest.py test.Plane.fly_tecs_test
```

4. Run

```bash
~/user_programs/plotjuggler_ws/install/bin/plotjuggler -n -l "/home/george/Dropbox/George/60-69 Personal hobby projects/63 Aerospace/63.18_ardupilot_controller_analysis/tecs_analysis_2/pj_layout.xml" -d logs/00000002.BIN &
```

to inspect the log.
