import cv2
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from picamera2 import Picamera2
from time import time
from roboCarHelper import RobocarHelper

class Camera:
    def __init__(self, resolution, rotation=True):
        self._dispW, self._dispH = resolution
        self._centerX = int(self._dispW / 2)
        self._centerY = int(self._dispH / 2)
        self._rotation: bool = rotation

        self._picam2 = None

        # text on video properties
        self._colour: tuple = (0, 255, 0)
        self._textPositions: list = self._set_text_positions()
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._scale: int = 1
        self._thickness: int = 1

        self._zoomValue: float = 1.0
        self._hudActive: bool = True

        self._carEnabled: bool = False
        self._servoEnabled: bool = False

        self._fps: float = 0.0
        self._fpsPos: tuple = (10, 30)

        self._arrayDict: dict[str: int] = {
            "HUD": 0,
            "Zoom": 1
        }
        self._indexCounter: int = len(self._arrayDict)

        self._number_to_directionValue: dict = {
            0: "Stopped",
            1: "Left",
            2: "Right",
            3: "Forward",
            4: "Reverse"
        }

    def show_camera_feed(self, flag, shared_array) -> None:
        self._setup()

        while not flag.value:
            tStart: float = time() # start timer for calculating fps

            # get raw image
            im = self._picam2.capture_array()

            # flip image if specified by user
            if self._rotation:
                im = cv2.flip(im, -1)

            # set HUD active or inactive
            self._set_HUD_active_value(shared_array)

            # set zoom value
            self._set_zoom_value(shared_array)

            # resize image when zooming
            if self._zoomValue != 1.0:
                im = self._get_zoomed_image(im)

            # add fps and control values to cam feed
            self._add_text_to_cam_feed(im, shared_array)

            cv2.imshow("Camera", im)
            cv2.waitKey(1)

            # calculate fps
            self._calculate_fps(tStart)

    def cleanup(self) -> None:
        cv2.destroyAllWindows()
        self._picam2.close()

    def set_car_enabled(self) -> None:
        self._carEnabled = True

        self._arrayDict.update({"speed": self._indexCounter, "direction": self._indexCounter + 1})
        self._indexCounter += 2

    def set_servo_enabled(self) -> None:
        self._servoEnabled = True

        self._arrayDict.update({"horizontal servo": self._indexCounter, "vertical servo": self._indexCounter + 1})
        self._indexCounter += 2

    @property
    def array_dict(self) -> dict[str: int]:
        return self._arrayDict

    def _setup(self) -> None:
        self._picam2 = Picamera2()

        # set resolution, format and rotation of camera feed
        config = self._picam2.create_preview_configuration(
            {"size": (self._dispW, self._dispH), "format": "RGB888"}
        )
        self._picam2.configure(config)
        self._picam2.start()

    def _set_text_positions(self) -> list[tuple]:
        spacingVertical: int = 30

        horizontalCoord: int = 10
        verticalCoord: int = self._dispH - 15

        positions: list = []
        for i in range(4):
            position = (horizontalCoord, verticalCoord - i * spacingVertical)
            positions.append(position)

        return positions

    def _calculate_fps(self, startTime: float) -> None:
        endTime: float = time()
        loopTime: float = endTime - startTime

        self._fps = RobocarHelper.low_pass_filter(self._fps, (1 / loopTime))

    def _get_zoomed_image(self, image) -> None:
        halfZoomDisplayWidth = int(self._dispW / (2 * self._zoomValue))
        halfZoomDisplayHeight = int(self._dispH / (2 * self._zoomValue))

        regionOfInterest = image[self._centerY - halfZoomDisplayHeight:self._centerY + halfZoomDisplayHeight,
                           self._centerX - halfZoomDisplayWidth:self._centerX + halfZoomDisplayWidth]

        im = cv2.resize(regionOfInterest, (self._dispW, self._dispH), cv2.INTER_LINEAR)

        return im

    def _add_text_to_cam_feed(self, image, shared_array) -> None:
        # display fps
        cv2.putText(image, self._get_fps_text(), self._fpsPos, self._font, self._scale, self._colour,
                    self._thickness)

        # add external control values if HUD is enabled
        if self._hudActive:
            counter: int = 0
            cv2.putText(image, f"Zoom: {self._zoomValue}x", self._get_origin(counter), self._font, self._scale,
                        self._colour,
                        self._thickness)
            counter += 1

            if self._servoEnabled:
                horizontalAngleValue = int(shared_array[self._arrayDict["horizontal servo"]])
                verticalAngleValue = int(shared_array[self._arrayDict["vertical servo"]])

                angleText: str = f"Angle: H{horizontalAngleValue}/V{verticalAngleValue}"
                cv2.putText(image, angleText, self._get_origin(counter), self._font, self._scale, self._colour,
                            self._thickness)
                counter += 1

            if self._carEnabled:
                speedValue = int(shared_array[self._arrayDict["speed"]])
                speedText: str = f"Speed: {speedValue}%"
                cv2.putText(image, speedText, self._get_origin(counter), self._font, self._scale, self._colour,
                            self._thickness)
                counter += 1

                directionValue: str = self._get_direction_value(shared_array[self._arrayDict["direction"]])
                directionText: str = f"Direction: {directionValue}"
                cv2.putText(image, directionText, self._get_origin(counter), self._font, self._scale, self._colour,
                            self._thickness)
                counter += 1

    def _get_fps_text(self) -> str:
        return str(int(self._fps)) + " FPS"

    def _set_HUD_active_value(self, shared_array) -> None:
        self._hudActive = shared_array[self._arrayDict["HUD"]]

    def _set_zoom_value(self, shared_array) -> None:
        self._zoomValue = shared_array[self._arrayDict["Zoom"]]

    def _get_direction_value(self, number: int) -> str:
        return self._number_to_directionValue[number]

    def _get_origin(self, count: int) -> tuple:
        return self._textPositions[count]