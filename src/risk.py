from dataclasses import dataclass, field
from threading import RLock

import cv2
import numpy as np


# ============================================================
# MODEL CONFIGURATION
# ============================================================

PERSON_CLASS = "person"

REQUIRED_PPE = [
    "ear-mufs",
    "glasses",
    "gloves",
    "helmet",
    "shoes",
]


DISPLAY_NAMES = {
    "en": {
        "person": "Person",
        "ear-mufs": "Hearing Protection",
        "glasses": "Goggles",
        "gloves": "Gloves",
        "helmet": "Helmet",
        "shoes": "Boots",
    },

    "es": {
        "person": "Persona",
        "ear-mufs": "Protector Auditivo",
        "glasses": "Gafas",
        "gloves": "Guantes",
        "helmet": "Casco",
        "shoes": "Calzado",
    },
}


# ============================================================
# EVENT CONFIGURATION
# ============================================================

# Un evento se registra cuando una PERSON está visible y un EPP
# seleccionado permanece sin confirmar durante este periodo.
EVENT_MIN_DURATION = 3.0

# El evento se cierra cuando deja de existir la condición durante
# este periodo. Esto evita abrir/cerrar eventos por un solo frame.
EVENT_RECOVERY_DURATION = 1.0


# ============================================================
# GEOMETRY
# ============================================================

def box_center(box):
    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2,
    )


def point_inside_box(point, box):
    x, y = point
    x1, y1, x2, y2 = box

    return (
        x1 <= x <= x2
        and
        y1 <= y <= y2
    )


def expand_box(box, width, height, margin=0.06):
    x1, y1, x2, y2 = map(float, box)

    bw = x2 - x1
    bh = y2 - y1

    x1 -= bw * margin
    x2 += bw * margin
    y1 -= bh * margin
    y2 += bh * margin

    return [
        max(0, int(x1)),
        max(0, int(y1)),
        min(width, int(x2)),
        min(height, int(y2)),
    ]


def crop_person_for_ppe(frame, person_box, ppe):
    """
    Recorte compacto para insight visual rápido:
    - casco/gafas/auditivo: cabeza + torso superior
    - guantes: medio cuerpo
    - botas: cuerpo completo
    """
    if frame is None:
        return None

    h, w = frame.shape[:2]

    x1, y1, x2, y2 = map(float, person_box)

    person_h = max(1.0, y2 - y1)

    if ppe in {"helmet", "glasses", "ear-mufs"}:
        crop_box = [
            x1,
            y1,
            x2,
            y1 + person_h * 0.52,
        ]

    elif ppe == "gloves":
        crop_box = [
            x1,
            y1,
            x2,
            y1 + person_h * 0.72,
        ]

    else:
        crop_box = [
            x1,
            y1,
            x2,
            y2,
        ]

    x1i, y1i, x2i, y2i = expand_box(
        crop_box,
        w,
        h,
        margin=0.08,
    )

    if x2i <= x1i or y2i <= y1i:
        return None

    crop = frame[
        y1i:y2i,
        x1i:x2i,
    ].copy()

    if crop.size == 0:
        return None

    return crop


# ============================================================
# SCENE ANALYSIS
# ============================================================

@dataclass
class PersonFrameStatus:
    box: list = field(default_factory=list)
    detected: dict = field(default_factory=dict)


def analyze_scene(
    detections,
    selected_ppe,
):
    selected_ppe = list(selected_ppe)

    persons = detections.get(
        PERSON_CLASS,
        [],
    )

    person_statuses = []

    for person in persons:
        person_box = person["box"]

        status = PersonFrameStatus(
            box=person_box,
        )

        for ppe in selected_ppe:
            present = False

            for obj in detections.get(
                ppe,
                [],
            ):
                if point_inside_box(
                    box_center(obj["box"]),
                    person_box,
                ):
                    present = True
                    break

            status.detected[ppe] = present

        person_statuses.append(
            status
        )

    person_count = len(
        person_statuses
    )

    ppe_stats = {}

    for ppe in selected_ppe:
        confirmed = sum(
            person.detected.get(
                ppe,
                False,
            )
            for person in person_statuses
        )

        unconfirmed = (
            person_count - confirmed
        )

        percent = (
            confirmed
            / person_count
            * 100
            if person_count
            else 0.0
        )

        ppe_stats[ppe] = {
            "confirmed": confirmed,
            "unconfirmed": unconfirmed,
            "percent": percent,
        }

    total_checks = (
        person_count
        * len(selected_ppe)
    )

    confirmed_checks = sum(
        stats["confirmed"]
        for stats in ppe_stats.values()
    )

    compliance = (
        confirmed_checks
        / total_checks
        * 100
        if total_checks
        else 0.0
    )

    review_people = sum(
        any(
            not person.detected.get(
                ppe,
                False,
            )
            for ppe in selected_ppe
        )
        for person in person_statuses
    )

    priority = None

    if person_count and ppe_stats:
        priority = min(
            ppe_stats,
            key=lambda ppe: (
                ppe_stats[ppe]["percent"]
            ),
        )

    return {
        "persons": person_count,
        "compliance": compliance,
        "review_people": review_people,
        "priority": priority,
        "ppe_stats": ppe_stats,
        "person_statuses": person_statuses,
    }


# ============================================================
# TEMPORAL EVENT MONITOR
# ============================================================

@dataclass
class ReviewEvent:
    event_id: int
    ppe: str
    person_index: int
    start_time: float
    end_time: float | None = None
    duration: float = 0.0
    avg_persons: float = 0.0
    avg_confirmed_percent: float = 0.0
    min_confirmed_percent: float = 100.0
    snapshot: np.ndarray | None = None
    open: bool = True


@dataclass
class ActiveEvent:
    ppe: str
    candidate_start: float | None = None
    confirmed: bool = False
    events: list = field(default_factory=list)
    recovery_start: float | None = None
    samples: int = 0
    persons_sum: float = 0.0
    percent_sum: float = 0.0
    min_percent: float = 100.0


class SceneEventMonitor:
    """
    Monitor temporal sin tracking ni identidad persistente.

    Un evento solo puede comenzar cuando:
    1) existe al menos una PERSON;
    2) el EPP está seleccionado;
    3) al menos una PERSON no tiene ese EPP confirmado;
    4) la condición persiste EVENT_MIN_DURATION segundos.

    Importante: "no confirmado" no equivale automáticamente a
    ausencia física del EPP. El evento se presenta como revisión.
    """

    def __init__(
        self,
        min_duration=EVENT_MIN_DURATION,
        recovery_duration=EVENT_RECOVERY_DURATION,
    ):
        self._lock = RLock()
        self.min_duration = float(
            min_duration
        )
        self.recovery_duration = float(
            recovery_duration
        )
        self.reset()

    def reset(self):
        with getattr(
            self,
            "_lock",
            RLock(),
        ):
            self.active = {}
            self.events = []
            self.next_event_id = 1
            self.latest_scene = {
                "persons": 0,
                "compliance": 0.0,
                "review_people": 0,
                "priority": None,
                "ppe_stats": {},
                "person_statuses": [],
            }

    def _unconfirmed_people(
        self,
        scene,
        ppe,
    ):
        """Frame-local individuals with selected PPE unconfirmed."""
        return [
            person
            for person in scene["person_statuses"]
            if not person.detected.get(
                ppe,
                False,
            )
        ]

    def _person_snapshot(
        self,
        frame,
        person,
        ppe,
    ):
        if frame is None:
            return None

        return crop_person_for_ppe(
            frame,
            person.box,
            ppe,
        )

    def _accumulate(
        self,
        state,
        persons,
        percent,
    ):
        state.samples += 1
        state.persons_sum += persons
        state.percent_sum += percent
        state.min_percent = min(
            state.min_percent,
            percent,
        )

        for event in state.events:
            event.avg_persons = (
                state.persons_sum
                / state.samples
            )

            event.avg_confirmed_percent = (
                state.percent_sum
                / state.samples
            )

            event.min_confirmed_percent = (
                state.min_percent
            )

    def _reset_active_state(
        self,
        ppe,
    ):
        self.active[ppe] = ActiveEvent(
            ppe=ppe,
        )

    def update(
        self,
        detections,
        selected_ppe,
        timestamp,
        frame=None,
    ):
        selected_ppe = list(
            selected_ppe
        )

        with self._lock:
            scene = analyze_scene(
                detections,
                selected_ppe,
            )

            self.latest_scene = scene

            # Si el filtro cambia, dejamos de evaluar EPP que ya no
            # están seleccionados.
            for ppe in list(
                self.active.keys()
            ):
                if ppe not in selected_ppe:
                    state = self.active[ppe]

                    if (
                        state.confirmed
                        and
                        state.events
                    ):
                        self._close_events(
                            state,
                            timestamp,
                        )

                    del self.active[ppe]

            for ppe in selected_ppe:
                if ppe not in self.active:
                    self._reset_active_state(
                        ppe
                    )

                state = self.active[ppe]

                persons = scene["persons"]

                stats = scene[
                    "ppe_stats"
                ].get(
                    ppe,
                    {
                        "confirmed": 0,
                        "unconfirmed": 0,
                        "percent": 0.0,
                    },
                )

                percent = stats["percent"]

                # CONDICIÓN CLAVE:
                # nunca hay evento si no hay PERSON visible.
                condition = (
                    persons > 0
                    and
                    stats["unconfirmed"] > 0
                )

                if condition:
                    state.recovery_start = None

                    if state.candidate_start is None:
                        state.candidate_start = float(
                            timestamp
                        )

                        state.samples = 0
                        state.persons_sum = 0.0
                        state.percent_sum = 0.0
                        state.min_percent = 100.0


                    self._accumulate(
                        state,
                        persons,
                        percent,
                    )

                    if (
                        not state.confirmed
                        and
                        (
                            float(timestamp)
                            - state.candidate_start
                        )
                        >= self.min_duration
                    ):
                        # Sustained PPE condition confirmed. Create one event
                        # per unconfirmed individual in THIS frame. No tracking.
                        unconfirmed_people = self._unconfirmed_people(
                            scene,
                            ppe,
                        )

                        state.confirmed = True
                        state.events = []

                        for person_index, person in enumerate(
                            unconfirmed_people,
                            start=1,
                        ):
                            event = ReviewEvent(
                                event_id=self.next_event_id,
                                ppe=ppe,
                                person_index=person_index,
                                start_time=state.candidate_start,
                                snapshot=self._person_snapshot(
                                    frame,
                                    person,
                                    ppe,
                                ),
                            )

                            self.next_event_id += 1

                            event.avg_persons = (
                                state.persons_sum
                                / state.samples
                            )

                            event.avg_confirmed_percent = (
                                state.percent_sum
                                / state.samples
                            )

                            event.min_confirmed_percent = (
                                state.min_percent
                            )

                            state.events.append(
                                event
                            )

                            self.events.append(
                                event
                            )

                    if (
                        state.confirmed
                        and
                        state.events
                    ):
                        for event in state.events:
                            event.duration = (
                                float(timestamp)
                                - event.start_time
                            )

                else:
                    if state.candidate_start is None:
                        continue

                    if not state.confirmed:
                        # No llegó a ser sostenido.
                        self._reset_active_state(
                            ppe
                        )
                        continue

                    if state.recovery_start is None:
                        state.recovery_start = float(
                            timestamp
                        )

                    if (
                        float(timestamp)
                        - state.recovery_start
                    ) >= self.recovery_duration:
                        self._close_events(
                            state,
                            state.recovery_start,
                        )

                        self._reset_active_state(
                            ppe
                        )

            return self.snapshot()

    def _close_events(
        self,
        state,
        end_time,
    ):
        for event in state.events:
            event.end_time = float(
                end_time
            )

            event.duration = max(
                0.0,
                event.end_time
                - event.start_time,
            )

            event.open = False

    def finalize(
        self,
        timestamp,
    ):
        with self._lock:
            for ppe, state in list(
                self.active.items()
            ):
                if (
                    state.confirmed
                    and
                    state.events
                ):
                    self._close_events(
                        state,
                        timestamp,
                    )

                self._reset_active_state(
                    ppe
                )

    def snapshot(self):
        with self._lock:
            return {
                "scene": self.latest_scene,
                "events": list(
                    self.events
                ),
                "open_events": sum(
                    event.open
                    for event in self.events
                ),
            }

    def export_rows(self):
        with self._lock:
            rows = []

            for event in self.events:
                rows.append(
                    {
                        "event_id": event.event_id,
                        "ppe": event.ppe,
                        "person_index": event.person_index,
                        "start_s": round(
                            event.start_time,
                            2,
                        ),
                        "end_s": (
                            round(
                                event.end_time,
                                2,
                            )
                            if event.end_time is not None
                            else None
                        ),
                        "duration_s": round(
                            event.duration,
                            2,
                        ),
                        "avg_persons": round(
                            event.avg_persons,
                            2,
                        ),
                        "avg_confirmed_pct": round(
                            event.avg_confirmed_percent,
                            2,
                        ),
                        "min_confirmed_pct": round(
                            event.min_confirmed_percent,
                            2,
                        ),
                        "status": (
                            "OPEN"
                            if event.open
                            else "CLOSED"
                        ),
                        "snapshot": event.snapshot,
                    }
                )

            return rows
