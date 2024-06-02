import subprocess

# Lista putanja do Python skripti koje želite da pokrenete
scripts = [
    "Controller.py",
    "temperature_sensor.py",
    "BPM_Sensor.py",
    "pressure_sensor.py",
    "button.py",
    "zvucnik.py",
    "vibration_motor.py",
    "pill_motor.py"
]

# Pokretanje svih skripti u zasebnim terminalima
for script in scripts:
    subprocess.Popen(["xfce4-terminal", "--hold", "--title", script, "--command=python3 " + script])
