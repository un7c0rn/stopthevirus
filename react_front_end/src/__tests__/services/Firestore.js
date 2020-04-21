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
  const _TEST_GAME_THAT_HAS_UUID_AS_ID = "f49f0cfd-c93b-4132-8c5b-ebea4bf81eae";
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

  const _TEST_GAME_NAME = "A NEW GAME";
  const _TEST_GAME_HASHTAG = "#ANEWGAME";
  const _TEST_ADD_GAME__GAME_ID = "a1b2c3CJaiSkxYgDocGDw4";

  const { firebase, firestore } = Firestore.initialise();

  beforeAll(async () => {
    let batch = firestore.batch();
    for (let path in collections_dict) {
      for (let document_id in collections_dict[path]) {
        const document_ref = firestore
          .collection(`${path}`)
          .doc(`${document_id}`);
        const properties_dict = collections_dict[path][document_id];
        properties_dict["id"] = document_id;
        batch.set(document_ref, properties_dict, { merge: true });
      }
    }
    await batch.commit();
  });

  it("should return an instance of Firebase Admin", () => {
    expect(firebase.SDK_VERSION).toBeDefined();
  });

  it("should return an instance of the firestore client", async () => {
    expect(firestore.settings.length).toBe(1);
  });

  it("should return a tribe ID", async () => {
    const response = await Firestore.tribe_from_id(
      _TEST_GAME_ID,
      _TEST_TRIBE_SIDAMA_ID
    );
    expect(response.id).toBe(_TEST_TRIBE_SIDAMA_ID);
  });

  it("should count the players in a game", async () => {
    const response = await Firestore.count_players({
      game: _TEST_GAME_ID,
    });
    expect(response).toBe(2);
  });

  it("should count the players in a tribe", async () => {
    const response = await Firestore.count_players({
      game: _TEST_GAME_ID,
      from_tribe: _TEST_TRIBE_SIDAMA_ID,
    });
    expect(response).toBe(2);
  });

  it("should count the players in a different tribe", async () => {
    const response = await Firestore.count_players({
      game: _TEST_GAME_ID,
      from_tribe: _TEST_TRIBE_TIGRAWAY_ID,
    });
    expect(response).toBe(0);
  });

  it("should count the players in a team", async () => {
    const response = await Firestore.count_players({
      game: _TEST_GAME_ID,
      from_team: _TEST_TEAM_BLUE_ID,
    });
    expect(response).toBe(0);
  });

  it("should count the teams in a game", async () => {
    const response = await Firestore.count_teams({
      game: _TEST_GAME_ID,
    });
    expect(response).toBe(6);
  });

  it("should count the teams in a tribe", async () => {
    const response = await Firestore.count_teams({
      game: _TEST_GAME_ID,
      from_tribe: _TEST_TRIBE_SIDAMA_ID,
    });
    expect(response).toBe(1);
  });

  it("should count the teams in a different tribe", async () => {
    const response = await Firestore.count_teams({
      game: _TEST_GAME_ID,
      from_tribe: _TEST_TRIBE_TIGRAWAY_ID,
    });
    expect(response).toBe(4);
  });

  it("should perform a batch update from one tribe to another", async () => {
    const response = await Firestore.batch_update_tribe({
      game: _TEST_GAME_ID,
      from_tribe: _TEST_TRIBE_TIGRAWAY_ID,
      to_tribe: _TEST_TRIBE_SIDAMA_ID,
    });
    expect(response.length).toBeGreaterThan(-1);
  });

  it("should get a player from an ID", async () => {
    const response = await Firestore.player_from_id({
      game: _TEST_GAME_ID,
      id: _TEST_BOSTON_ROB_PLAYER_ID,
    });
    expect(response.id).toBe(_TEST_BOSTON_ROB_PLAYER_ID);
  });

  it("should get a player from an ID", async () => {
    const response = await Firestore.team_from_id({
      game: _TEST_GAME_ID,
      id: _TEST_TEAM_BLUE_ID,
    });
    expect(response.id).toBe(_TEST_TEAM_BLUE_ID);
  });

  it("should count the votes", async () => {
    const obj = {};
    obj[_TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID] = 5;

    const response = await Firestore.count_votes({
      game: _TEST_GAME_ID,
      from_team: _TEST_TEAM_YELLOW_ID,
      is_for_win: false,
    });
    expect(response).toEqual(obj);
  });

  it("should count the votes for a player in a team", async () => {
    const obj = {};
    obj[_TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID] = 5;

    const response = await Firestore.count_votes({
      game: _TEST_GAME_ID,
      from_team: _TEST_TEAM_YELLOW_ID,
      is_for_win: false,
    });
    expect(response).toEqual(obj);
  });

  it("should count the votes a player in in a game", async () => {
    const obj = {};
    obj[_TEST_YELLOW_TEAM_ACTIVE_PLAYER_ID] = 5;

    const response = await Firestore.count_votes({
      game: _TEST_GAME_ID,
      is_for_win: false,
    });
    expect(response).toEqual(obj);
  });

  it("should return false if no ID parameter is provided when requesting game information", async () => {
    const obj = {};
    const response = await Firestore.get_game_info({});
    expect(response).toBe(false);
  });

  it("should return undeind if the ID for a game is not found when requesting game information", async () => {
    const obj = { game: ";lhsdfk3lrhkl3" };
    const response = await Firestore.get_game_info(obj);
    expect(response).toBe(undefined);
  });

  it("should return game information for a given game ID", async () => {
    const obj = { id: _TEST_GAME_THAT_HAS_UUID_AS_ID };
    const response = await Firestore.get_game_info({
      game: _TEST_GAME_THAT_HAS_UUID_AS_ID,
    });
    expect(response.id).toBe(obj.id);
  });

  it("should return false if no name or hashtag is provided", async () => {
    const obj = {};
    const response = await Firestore.add_game(obj);
    expect(response).toBe(false);
  });

  it("should add a game", async () => {
    const obj = {
      game: _TEST_GAME_NAME,
      hashtag: _TEST_GAME_HASHTAG,
      testId: _TEST_ADD_GAME__GAME_ID,
    };
    const response = await Firestore.add_game(obj);
    expect(response.id).toBe(_TEST_ADD_GAME__GAME_ID);
  });
});
