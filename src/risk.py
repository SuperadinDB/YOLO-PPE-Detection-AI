from dataclasses import dataclass, field


PPE_CLASSES = {
    "helmet": "no_helmet",
    "gloves": "no_gloves",
    "boots": "no_boots",
    "goggles": "no_goggle",
}

REQUIRED_PPE = list(PPE_CLASSES.keys())


@dataclass
class WorkerStatus:
    worker_id: int
    detected: dict = field(default_factory=dict)
    missing: list = field(default_factory=list)
    uncertain: list = field(default_factory=list)

    @property
    def compliant(self):
        return len(self.missing) == 0 and len(self.uncertain) == 0

    @property
    def risk(self):
        if self.missing:
            return "HIGH"
        if self.uncertain:
            return "MEDIUM"
        return "LOW"


def point_inside_box(point, box):
    x, y = point
    x1, y1, x2, y2 = box

    return x1 <= x <= x2 and y1 <= y <= y2


def box_center(box):
    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2,
    )


def evaluate_workers(detections):

    persons = detections.get("Person", [])

    workers = []

    for worker_id, person in enumerate(persons, start=1):

        person_box = person["box"]

        status = WorkerStatus(
            worker_id=worker_id
        )

        for ppe_class in REQUIRED_PPE:

            present_objects = detections.get(ppe_class, [])
            absent_objects = detections.get(
                PPE_CLASSES[ppe_class],
                []
            )

            present = False
            absent = False

            # -----------------------------------------
            # PPE PRESENT
            # -----------------------------------------

            for obj in present_objects:

                center = box_center(obj["box"])

                if point_inside_box(
                    center,
                    person_box
                ):
                    present = True
                    break

            # -----------------------------------------
            # PPE ABSENT
            # -----------------------------------------

            for obj in absent_objects:

                center = box_center(obj["box"])

                if point_inside_box(
                    center,
                    person_box
                ):
                    absent = True
                    break

            if absent:

                status.detected[ppe_class] = False
                status.missing.append(ppe_class)

            elif present:

                status.detected[ppe_class] = True

            else:

                status.detected[ppe_class] = None
                status.uncertain.append(ppe_class)

        workers.append(status)

    return workers