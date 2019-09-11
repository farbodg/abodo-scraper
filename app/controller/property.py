from flask import Blueprint, request
from ..service import scraper as scraper_service

app = Blueprint('app', __name__)


@app.route('/', methods=['GET'])
def get_properties():
    bedrooms = request.args.get("bedrooms")
    bathrooms = request.args.get("bathrooms")

    return scraper_service.find_properties(bedrooms, bathrooms)
