#  Sistema Integral de Seguridad Residencial

**Autor: Hugo Herrera**

---

##  Descripción

Sistema automatizado de seguridad para hogares y edificios. Detecta intrusos mediante sensores de movimiento, controla una puerta automática, activa alarma sonora y visual, y captura imágenes con cámara al detectar movimiento. Incluye lógica horaria de seguridad nocturna.

Desarrollado originalmente en **Cisco Packet Tracer** (simulación IoT). Compatible con **Raspberry Pi** usando RPi.GPIO. Corre en **modo simulación** en cualquier PC sin hardware.

---

## Características

| Módulo | Descripción |
|---|---|
|  **Detección de intrusos** | Sensores de movimiento en pines 0, 4 y 5 con respuesta en tiempo real |
|  **Control de puerta** | Cierre automático al detectar intruso, apertura programada a las 05:00 |
|  **Cámara** | Se activa ante cada detección, guarda `camera_image<N>.png` |
|  **Alarma** | Buzzer sonoro + LED rojo, desactivación automática tras `MOTION_TIMEOUT` segundos |
|  **Modo nocturno** | Alarma activa automáticamente entre 01:00 y 05:00 hrs |
|  **Multi-entorno** | Corre en Packet Tracer, Raspberry Pi o cualquier PC en modo simulación |

---

##  Diagrama de Flujo

```
INICIO
  │
  ├─ Registrar sensores en pines 0, 4 y 5
  │
  └─ BUCLE PRINCIPAL (cada 1 segundo)
       │
       ├─ Hora entre 01:00–05:00 y alarma inactiva → Activar alarma
       ├─ Hora == 05:00                             → Abrir puerta
       └─ Alarma activa y tiempo expiró             → Desactivar alarma

EVENTO SENSOR
  │
  ├─ valor == 0 (sin movimiento)
  │    ├─ Print: "NO HAY INTRUSOS EN EL PERÍMETRO"
  │    ├─ Desactivar alarma
  │    └─ Abrir puerta
  │
  └─ valor != 0 (movimiento detectado)
       ├─ Print: "¡INTRUSO DETECTADO!"
       ├─ Activar alarma (buzzer + LED rojo)
       ├─ Cerrar puerta
       └─ Activar cámara → guardar camera_image<N>.png
```

---

##  Hardware (Raspberry Pi)

| Componente | Pin GPIO |
|---|---|
| Sensor de movimiento 1 | 0 |
| Sensor de movimiento 2 | 4 |
| Sensor de movimiento 3 | 5 |
| Buzzer (alarma) | 2 |
| Relé puerta | 6 |
| LED Rojo | 3 |
| Señal cámara | 4 |

---

## ⚙️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/elhugoxc/sistema-seguridad-residencial.git
cd sistema-seguridad-residencial

# En Raspberry Pi, instalar dependencia
pip install RPi.GPIO

# Ejecutar
python security_system.py
```

> En PC sin hardware corre automáticamente en **modo simulación** — no requiere ninguna instalación adicional.

---

##  Compatibilidad de Entornos

El script detecta automáticamente el entorno y se adapta:

```
Cisco Packet Tracer  →  usa módulo gpio nativo del simulador
Raspberry Pi         →  usa RPi.GPIO
PC / Mac / Linux     →  modo simulación (stub de GPIO por consola)
```

---

##  Estructura

```
sistema-seguridad-residencial/
├── security_system.py   # Código principal
└── README.md            # Este archivo
```
