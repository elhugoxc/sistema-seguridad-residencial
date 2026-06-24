"""
Sistema Integral de Seguridad Residencial
==========================================
Autor: Hugo Herrera

Sistema automatizado de seguridad para hogares y edificios.
Detecta intrusos mediante sensores de movimiento, controla
una puerta automática, activa alarma sonora/visual y
captura imágenes con cámara al detectar movimiento.

Desarrollado originalmente para Cisco Packet Tracer (simulación IoT).
Compatible con Raspberry Pi usando RPi.GPIO.
"""

from time import sleep, time, strftime, localtime

# ──────────────────────────────────────────────────────────────
#  Importar GPIO según el entorno disponible
# ──────────────────────────────────────────────────────────────
try:
    # Entorno Packet Tracer (simulación)
    from gpio import (digitalRead, analogWrite, digitalWrite,
                      add_event_detect, customWrite, LOW, HIGH)
    ENV = "packet_tracer"

except ImportError:
    try:
        # Raspberry Pi real
        import RPi.GPIO as _GPIO
        _GPIO.setmode(_GPIO.BCM)
        _GPIO.setwarnings(False)

        LOW  = False
        HIGH = True
        _listeners = {}

        def digitalRead(pin):
            return _GPIO.input(pin)

        def digitalWrite(pin, value):
            _GPIO.output(pin, value)

        def analogWrite(pin, value):
            _GPIO.output(pin, value)

        def customWrite(pin, value):
            _GPIO.output(pin, value)

        def add_event_detect(pin, callback):
            _GPIO.setup(pin, _GPIO.IN)
            _GPIO.add_event_detect(pin, _GPIO.RISING,
                                   callback=lambda ch: callback())

        ENV = "raspberry_pi"

    except ImportError:
        # Sin hardware — modo simulación para pruebas en PC
        LOW  = False
        HIGH = True
        _listeners = {}

        def digitalRead(pin):
            return 0

        def digitalWrite(pin, value):
            print(f"  [GPIO] digitalWrite(pin={pin}, value={'HIGH' if value else 'LOW'})")

        def analogWrite(pin, value):
            print(f"  [GPIO] analogWrite(pin={pin}, value={'HIGH' if value else 'LOW'})")

        def customWrite(pin, value):
            print(f"  [GPIO] customWrite(pin={pin}, value={'HIGH' if value else 'LOW'})")

        def add_event_detect(pin, callback):
            print(f"  [GPIO] Sensor registrado en pin {pin}")

        ENV = "simulation"


# ──────────────────────────────────────────────────────────────
#  Configuración de pines y constantes
# ──────────────────────────────────────────────────────────────
ALARMPIN       = 2    # Pin buzzer / alarma sonora
DOOR_PIN       = 6    # Pin relé de puerta
LED_RED_PIN    = 3    # Pin LED rojo (intruso detectado)
CAMERA_PIN     = 4    # Pin señal cámara
MOTION_TIMEOUT = 10   # Segundos que permanece activa la alarma
CHECK_INTERVAL = 1    # Segundos entre cada revisión del bucle

# ──────────────────────────────────────────────────────────────
#  Variables globales de estado
# ──────────────────────────────────────────────────────────────
alarm_active_until = 0   # timestamp hasta el que está activa la alarma (0 = inactiva)
imageLoop          = 0   # índice de la próxima imagen a capturar


# ──────────────────────────────────────────────────────────────
#  Manejo de sensores
# ──────────────────────────────────────────────────────────────
def handle_sensor_data(port):
    """
    Procesa la lectura de un sensor de movimiento.
    - value == 0 → sin movimiento → handle_no_intruder
    - value != 0 → movimiento detectado → handle_intruder
    """
    global alarm_active_until, imageLoop

    value = digitalRead(port)

    if value == 0:
        handle_no_intruder(port)
    else:
        handle_intruder(port)
        alarm_active_until = time() + MOTION_TIMEOUT
        digitalWrite(DOOR_PIN, LOW)   # cerrar puerta
        activate_camera()


def handle_no_intruder(port):
    """Sin intrusos: desactivar alarma y abrir puerta."""
    print("NO HAY INTRUSOS EN EL PERÍMETRO")
    analogWrite(ALARMPIN, LOW)
    alarm_active_until = 0
    digitalWrite(DOOR_PIN, HIGH)   # abrir puerta


def handle_intruder(port):
    """Intruso detectado: activar alarma, encender LED rojo."""
    print("¡INTRUSO DETECTADO!")
    print(f"  Sensor activado: pin {port}")
    activate_alarm()
    customWrite(LED_RED_PIN, HIGH)


# ──────────────────────────────────────────────────────────────
#  Control de puerta según horario
# ──────────────────────────────────────────────────────────────
def check_door_status():
    """
    Lógica horaria de seguridad nocturna:
      01:00–05:00 → modo alarma activo
      05:00       → abrir puerta (inicio del día)
      fuera de rango y alarma expirada → desactivar alarma
    """
    global alarm_active_until

    current_hour = int(strftime("%H", localtime()))

    if 1 <= current_hour < 5:
        if alarm_active_until == 0:
            activate_alarm()

    elif current_hour == 5:
        digitalWrite(DOOR_PIN, HIGH)   # abrir puerta al amanecer

    elif time() > alarm_active_until > 0:
        deactivate_alarm()


# ──────────────────────────────────────────────────────────────
#  Cámara
# ──────────────────────────────────────────────────────────────
def activate_camera():
    """Captura imagen y la guarda como camera_image<N>.png."""
    global imageLoop
    filename = f"camera_image{imageLoop}.png"
    print(f"Activando la cámara — guardando: {filename}")
    digitalWrite(CAMERA_PIN, HIGH)
    sleep(0.5)
    digitalWrite(CAMERA_PIN, LOW)
    imageLoop += 1


# ──────────────────────────────────────────────────────────────
#  Alarma
# ──────────────────────────────────────────────────────────────
def activate_alarm():
    """Activar buzzer y registrar tiempo de expiración."""
    global alarm_active_until
    print("Activando la alarma.")
    analogWrite(ALARMPIN, HIGH)
    customWrite(LED_RED_PIN, HIGH)
    if alarm_active_until == 0:
        alarm_active_until = time() + MOTION_TIMEOUT


def deactivate_alarm():
    """Desactivar buzzer, apagar LED rojo, abrir puerta."""
    global alarm_active_until
    print("Desactivando la alarma.")
    analogWrite(ALARMPIN, LOW)
    customWrite(LED_RED_PIN, LOW)
    digitalWrite(DOOR_PIN, HIGH)
    alarm_active_until = 0   # resetear para desactivar la alarma


# ──────────────────────────────────────────────────────────────
#  Función principal
# ──────────────────────────────────────────────────────────────
def main():
    """
    Punto de entrada del sistema:
    1. Registrar callbacks para los sensores en pines 0, 4 y 5
    2. Bucle infinito revisando estado de puerta/alarma
    """
    print(f"[INFO] Sistema iniciado — entorno: {ENV}")
    print("[INFO] Registrando sensores en pines 0, 4 y 5...")

    add_event_detect(0, lambda: handle_sensor_data(0))
    add_event_detect(4, lambda: handle_sensor_data(4))
    add_event_detect(5, lambda: handle_sensor_data(5))

    print("[INFO] Sistema activo. Monitoreando...\n")

    while True:
        check_door_status()
        sleep(CHECK_INTERVAL)


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
