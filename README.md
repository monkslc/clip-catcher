# Clip Catcher

Application for automatically capturing a video clip when a loud sound was detected.

## Dev Guideline (Mac only at the moment)

### Structure

Code that encapsulates a majority of the functionality can be found in `src/lib`

The implementation for my particular use case, automatically recording my golf swing, can be found in the `src/main.py` file.

### Prereqs

- install python3 / pip3
- install [PortAudio](https://www.portaudio.com/) `brew install portaudio`
- install requirements `pip3 install -r requirements.txt`

### Runnning

`python3 src/main.py`
