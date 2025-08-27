# fuelrod_exporter/api/v1/routes.py
from flask import Blueprint
from fuelrod_exporter.api.v1.controllers.report_controller import ReportsController
from fuelrod_exporter.api.v1.controllers.health_controller import HealthController

report_controller = ReportsController()
health_controller = HealthController()

# Expose list of blueprints for the app factory
v1_blueprints = [
    health_controller.api,
    report_controller.api
]
