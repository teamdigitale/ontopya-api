#!/usr/bin/env python3
import connexion


app = connexion.App(
    __name__, specification_dir="openapi/", options={"swagger_ui": True}
)
app.add_api("ontopia.yaml")

if __name__ == "__main__":
    app.run(port=8080, debug=True)
