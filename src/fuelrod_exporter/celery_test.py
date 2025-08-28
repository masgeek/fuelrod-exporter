import sys
from celery.__main__ import main as celery_main


def main():
    sys.argv = [
        "celery",
        "-A",
        "fuelrod_exporter.test_celery",
        "worker",
        "--loglevel=info",
    ]
    celery_main()


if __name__ == "__main__":
    main()
