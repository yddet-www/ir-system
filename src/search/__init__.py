import os

from flask import Flask, render_template, request, flash
from src.indexer.indexme import Index
from src.search.searchme import query_pipeline, get_url_mapping
from util.config import CRWL_MAP_FP


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load inverted index
    index_obj = Index("inverted_index.json")
    url_map = get_url_mapping(CRWL_MAP_FP)

    # a simple page that says hello
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            query = request.form.get("query", type=str)

            if not query:
                flash("Please provide a query!")
            else:
                doc_list = query_pipeline(query, index_obj, url_map)
                print(doc_list)

            print(f"USER QUERRY: {query}")
        return render_template(
            "index.html",
        )

    return app
