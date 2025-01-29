from flask import Blueprint, request, jsonify
from utils.scraper import scrape_all_platforms  # Import the unified scraper
import time

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        start_time = time.time()  # Start tracking response time

        # Call the multi-threaded scraper
        results = scrape_all_platforms(query)

        end_time = time.time()  # Stop tracking time
        elapsed_time = round(end_time - start_time, 2)

        print(f"Search completed in {elapsed_time} seconds")

        return jsonify({"query": query, "results": results, "response_time": elapsed_time})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
