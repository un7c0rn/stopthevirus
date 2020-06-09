import firebase_admin
from firebase_admin import credentials, firestore
from game_engine.firestore import FirestoreDB

_FIRESTORE_PROD_CONF_JSON_PATH = ''
_TEST_FIRESTORE_INSTANCE_JSON_PATH = '../firebase/stv-game-db-test-4c0ec2310b2e.json'
json_config_path = _TEST_FIRESTORE_INSTANCE_JSON_PATH

_gamedb = FirestoreDB(
    json_config_path=_TEST_FIRESTORE_INSTANCE_JSON_PATH, game_id=123)
_gamedb.find_matchmaker_games()
# cred = credentials.Certificate(json_config_path)
# if not firebase_admin._apps:
#     firebase_admin.initialize_app(cred)
# db = firestore.Client()
# collection_ref = db.collection(u'users')
# def on_snapshot(collection_snapshot):
#     for doc in collection_snapshot.documents:
#         print(u'{} => {}'.format(doc.id, doc.to_dict()))
# collection_watch = collection_ref.on_snapshot(on_snapshot)
