import os
from pathlib import Path
from flask import Flask, render_template, request, flash
from src.indexer.indexme import Index
from src.search.searchme import query_pipeline, get_url_mapping


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
    index_obj = Index(Path("inverted_index.json"))
    url_map = get_url_mapping(index_obj.corpus_mapping)

    # a simple page that says hello
    @app.route("/", methods=["GET", "POST"])
    def index():
        original_query = None
        corrected_query = None
        was_corrected = False
        results = None
        error = None

        if request.method == "POST":
            query = request.form.get("query", "").strip()
            original_query = query

            if not query:
                error = "Please provide a query!"
            else:
                try:
                    documents, q_corrected, flag = query_pipeline(
                        query, index_obj, url_map
                    )

                    results = [
                        (doc_id, score, url_map[doc_id]) for doc_id, score in documents
                    ]

                    corrected_query = " ".join(q_corrected)
                    was_corrected = flag
                    print(f"USER QUERY: {query}")
                    print(f"RESULTS: {len(results)} documents found")
                except ValueError as e:
                    error = str(e)
                except Exception as e:
                    error = f"An error occurred: {str(e)}"

        return render_template(
            "index.html",
            results=results,
            query=original_query,
            corrected_query=corrected_query,
            was_corrected=was_corrected,
            error=error,
        )

    return app
