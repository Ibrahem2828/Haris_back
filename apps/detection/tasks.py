try:
    from celery import shared_task
except ImportError:  # pragma: no cover - local fallback before celery is installed
    class _ImmediateResult:
        id = None

    class _TaskWrapper:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def delay(self, *args, **kwargs):
            self.func(*args, **kwargs)
            return _ImmediateResult()

    def shared_task(func):
        return _TaskWrapper(func)

from .models import DetectionJob
from .services.engine import DetectionEngine


@shared_task
def run_detection_job(job_id):
    job = DetectionJob.objects.get(pk=job_id)
    return DetectionEngine().run_detection(
        from_timestamp=job.from_timestamp,
        to_timestamp=job.to_timestamp,
        rule_types=job.rules_requested,
        job=job,
        triggered_by=job.triggered_by,
        mode=job.mode,
    ).id


@shared_task
def run_detection_for_time_range(job_id, from_timestamp=None, to_timestamp=None, rules=None):
    job = DetectionJob.objects.get(pk=job_id)
    return DetectionEngine().run_detection(
        from_timestamp=from_timestamp or job.from_timestamp,
        to_timestamp=to_timestamp or job.to_timestamp,
        rule_types=rules or job.rules_requested,
        job=job,
        triggered_by=job.triggered_by,
        mode=job.mode,
    ).id
