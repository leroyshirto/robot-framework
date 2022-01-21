# Robot Framework

A WIP robot framework written in micro python

## Project setup

Micropy-cli

install micropy-cli `pip install --upgrade micropy-cli`

Searching for the MicroPython Stubs `micropy stubs search esp32` and select the latest firmware

Add stubs `micropy stubs add esp32-micropython-1.15.0`

init a new project (Not required for this repo only listing this step for future ref) `micropy init`

# Libs

- websocket server https://github.com/BetaRavener/upy-websocket-server
- logger https://github.com/micropython/micropython-lib/blob/master/python-stdlib/logging/logging.py

## MicroPython tips

view memory usage

```python
import micropython
micropython.mem_info()
```
