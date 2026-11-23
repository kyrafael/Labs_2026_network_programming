# Lab 3 — Store Catalog REST API (Medium)

The Flask API stores demo accounts in `users.json` and the product catalog in
`items.json`. Changes to products are saved to disk. The user file stores
password hashes, not plaintext passwords.

## Run

Open the project folder in PyCharm and run these commands from the folder
that contains `Lab5`:

```sh
python -m pip install -r Lab5/requirements.txt
python Lab3/app.py
```

The server listens on `http://127.0.0.1:8001`.

## Test in Postman

For every request, select **Authorization → Basic Auth**. Use the demo
username `student` and password `lab5-demo`. These credentials are for local
testing only.

| Method | URL path | Expected result |
| --- | --- | --- |
| GET | /items | 200, list of products |
| POST | /items | 201, created product with an ID |
| GET | /items/3 | 200, product details |
| PUT | /items/3 | 200, updated product |
| DELETE | /items/3 | 200, deletion confirmation |
| GET | /items/3 | 404 after deletion |

Use the ID returned by POST instead of `3` if it differs. For POST and PUT,
choose **Body → raw → JSON** and send all three fields:

```json
{"name": "Backpack", "price": 29.99, "color": "blue"}
```

For PUT, change the price to `34.99`. To check persistence, restart the
server after PUT and send GET again before deleting the product. To check
authentication, send GET /items without credentials and expect 401.
