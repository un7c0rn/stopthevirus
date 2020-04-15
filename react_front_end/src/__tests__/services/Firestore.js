/**
 * @jest-environment node
 */

import Firestore from "../../services/Firestore";
import collections_dict from "../mock_data/firestore.json";

describe("Firestore service", () => {
  const _TEST_FIRESTORE_INSTANCE_JSON_PATH =
    "../firebase/stv-game-db-test-4c0ec2310b2e.json";
  const _TEST_TRIBE_TIGRAWAY_ID = "77TMV9omdLeW7ORvuheX";
  const _TEST_TRIBE_SIDAMA_ID = "cbTgYdPh97K6rRTDdEPL";
  const _TEST_GAME_ID = "7rPwCJaiSkxYgDocGDw4";
  const _TEST_TEAM_BLUE_ID = "GQnxhYXnV86oJXLklbGB";
  const _TEST_TEAM_YELLOW_ID = "Q09FeEtoIgjNI57Bnl1E";
  const _TEST_CHALLENGE_KARAOKE_ID = "2JQ5ZvttkFafjxvrN07Q";
  const _TEST_CHALLENGE_KARAOKE_URL =
    "https://www.youtube.com/watch?v=irVIUvDTTB0";
  const _TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID = "2ZPmDfX9q82KY5PVf1LH";
  const _TEST_BOSTON_ROB_PLAYER_ID = "2ZPmDfX9q82KY5PVf1LH";
  const _TEST_COLLECTION_PATHS = [
    "games",
    "games/7rPwCJaiSkxYgDocGDw4/players",
    "games/7rPwCJaiSkxYgDocGDw4/teams",
    "games/7rPwCJaiSkxYgDocGDw4/tribes",
    "games/7rPwCJaiSkxYgDocGDw4/votes",
  ];

  const firestore = new Firestore();
  const { firebase, firestoreClient } = firestore.initialise();

  beforeAll(async () => {
    let batch = firestoreClient.batch();
    for (let path in collections_dict) {
      for (let document_id in collections_dict[path]) {
        const document_ref = firestoreClient
          .collection(`${path}`)
          .doc(`${document_id}`);
        // console.log(document_ref);
        const properties_dict = collections_dict[path][document_id];
        properties_dict["id"] = document_id;
        //     // console.log(properties_dict);
        batch.set(document_ref, properties_dict, { merge: true });
      }
    }
    await batch.commit();
  });

  it("should return an instance of Firebase Admin", () => {
    expect(firebase.SDK_VERSION).toBeDefined();
  });

  it("should return an instance of the firestore client", async () => {
    expect(firestoreClient.settings.length).toBe(1);
  });

  it("should return a tribe ID", async () => {
    const response = await firestore.tribe_from_id(
      _TEST_GAME_ID,
      _TEST_TRIBE_SIDAMA_ID
    );
    expect(response.id).toBe(_TEST_TRIBE_SIDAMA_ID);
  });
});
