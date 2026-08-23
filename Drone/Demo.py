from vex import *

# =========================================================
# VEX AIR Hybrid Flight Script
# Pilot flies manually with the normal Controller joysticks
# (VEXcode AIR handles that natively once Propeller Lock is
# off) — this script layers autonomy on TOP of that:
#   - a safety watchdog running the whole flight
#   - an autonomous sequence you trigger mid-flight with a
#     controller button
#
# NOTE: Lines marked "# confirm" use plausible VEX AIR method
# names based on the drone/controller/console patterns VEX
# uses across its Python API. VEXcode AIR's editor autocompletes
# exact device methods as you type "drone.", "controller.",
# "vision_front.", etc. — check those against this script and
# rename anything that doesn't match before you fly.
# =========================================================

# ---------- CONFIG ----------
BATTERY_ABORT_PCT = 15      # auto-land if battery drops below this
OBSTACLE_STOP_CM = 30       # hover if something gets this close
AUTO_BUTTON = "buttonL1"    # controller button that triggers autonomy

mission_active = False


# ---------- PRE-FLIGHT ----------
def preflight_check():
    console.print("Calibrating — keep the drone still...")
    drone.calibrate()                      # confirm: inertial sensor calibration
    wait(2, SECONDS)

    battery = drone.battery_level()        # confirm
    console.print("Battery: " + str(battery) + "%")

    if battery < BATTERY_ABORT_PCT:
        console.print("Battery too low to fly. Charge before takeoff.")
        return False
    return True


# ---------- SAFETY WATCHDOG (runs continuously in the background) ----------
def safety_watchdog():
    while True:
        battery = drone.battery_level()    # confirm
        if battery < BATTERY_ABORT_PCT:
            console.print("LOW BATTERY — AUTO LANDING")
            drone.land()
            break

        front_dist = range_front.distance(MM)  # confirm units/method name
        if front_dist < OBSTACLE_STOP_CM * 10:
            console.print("Obstacle close — holding position")
            drone.hover()                  # confirm

        wait(100, MSEC)


# ---------- AUTONOMOUS SEQUENCE (triggered mid-flight by a button) ----------
def autonomous_capture_mission():
    global mission_active
    if mission_active:
        console.print("Autonomous sequence already running")
        return

    mission_active = True
    console.print("Starting autonomous sequence...")

    drone.move_for(FORWARD, 300, MM)       # confirmed pattern: drone.move_for(direction, distance)
    wait(1, SECONDS)

    if vision_front.detect_tag():          # confirm
        tag_id = vision_front.get_tag_id() # confirm
        console.print("Found AprilTag: " + str(tag_id))
        drone.move_for(FORWARD, 150, MM)
        camera_front.capture_image()       # confirm
        console.print("Image captured")
    else:
        console.print("No tag found — returning")

    drone.move_for(REVERSE, 450, MM)
    console.print("Autonomous sequence complete")
    mission_active = False


# ---------- MAIN ----------
def main():
    if not preflight_check():
        return

    # Background safety net — runs the whole flight regardless
    # of whether you're flying manually or mid-autonomous-sequence
    start_thread(safety_watchdog)

    # Bind the autonomous sequence to a controller button.
    # Everything else stays on normal manual joystick control.
    controller.buttonL1.pressed(autonomous_capture_mission)  # confirm button name

    console.print("Ready. Fly manually with the joysticks.")
    console.print("Press L1 to run the autonomous capture sequence.")

    # Keep the project alive so the watchdog + button binding
    # stay active for the whole flight. Manual flight itself is
    # handled by the Controller/firmware, not this loop.
    while True:
        wait(500, MSEC)


start_thread(main)
