import cv2

from src.zone_editor import ZoneEditor
from src.zone_storage import ZoneStorage


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    editor = ZoneEditor()
    storage = ZoneStorage()

    window_name = "TacticalVision - Zone Editor"

    cv2.namedWindow(window_name)

    cv2.setMouseCallback(
        window_name,
        editor.mouse_callback
    )

    print()
    print("TACTICALVISION ZONE EDITOR")
    print("--------------------------")
    print("Arrastra con el botón izquierdo para crear una zona.")
    print("Presiona S para guardar.")
    print("Presiona R para borrar todas las zonas.")
    print("Presiona Q para salir.")
    print()

    while True:
        success, frame = camera.read()

        if not success:
            break

        editor.draw(frame)

        cv2.putText(
            frame,
            "Drag = Create Zone | S = Save | R = Reset | Q = Quit",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            storage.save(editor.zones)

            print(
                f"{len(editor.zones)} zona(s) guardada(s)."
            )

        elif key == ord("r"):
            editor.zones.clear()
            editor.zone_counter = 1

            print("Zonas eliminadas.")

        elif key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()