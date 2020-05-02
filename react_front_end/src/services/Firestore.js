import dotenv from "dotenv";
import * as admin from "firebase-admin";

dotenv.config();

export default class Firestore {
  static firebase;
  static firestore;

  static getInstance = () => {
    if (admin.apps.length < 1) {
      const { firebase, firestore } = this.initialise();
      this.firebase = firebase;
      this.firestore = firestore;
    }

    this.firebase = admin;
    this.firestore = admin.app("VIR-US").firestore();

    return this;
  };

  static initialise = () => {
    // Web app's Firebase configuration
    var credentials = {
      type: process.env.REACT_APP_type,
      project_id: process.env.REACT_APP_project_id,
      private_key_id: process.env.REACT_APP_private_key_id,
      private_key: process.env.REACT_APP_private_key.replace(/\\n/g, "\n"),
      client_email: process.env.REACT_APP_client_email,
      client_id: process.env.REACT_APP_client_id,
      auth_uri: process.env.REACT_APP_auth_uri,
      token_uri: process.env.REACT_APP_token_uri,
      auth_provider_x509_cert_url:
        process.env.REACT_APP_auth_provider_x509_cert_url,
      client_x509_cert_url: process.env.REACT_APP_client_x509_cert_url,
    };

    const app = admin.initializeApp(
      {
        credential: admin.credential.cert(credentials),
        databaseURL: "https://stv-game-db-test.firebaseio.com",
      },
      "VIR-US"
    );

    const defaultFirebase = admin;
    const defaultFirestore = admin.firestore(app);

    return {
      firebase: defaultFirebase,
      firestore: defaultFirestore,
    };
  };

  static tribe_from_id = async (game = null, id = null) => {
    return await (
      await this.firestore.doc(`games/${game}/tribes/${id}`).get()
    ).data();
  };

  static count_players = async ({
    game = null,
    from_tribe = null,
    from_team = null,
  }) => {
    if (from_tribe) {
      return (
        await this.firestore.doc(`games/${game}/tribes/${from_tribe}`).get()
      ).data().count_players;
    } else if (from_team) {
      return (
        await this.firestore.doc(`games/${game}/teams/${from_team}`).get()
      ).data().count_players;
    } else {
      return (await this.firestore.doc(`games/${game}`).get()).data()
        .count_players;
    }
  };

  static count_teams = async ({
    game = null,
    from_tribe = null,
    active_team_predicate_value = true,
  }) => {
    let query;
    if (from_tribe) {
      query = this.firestore.doc(`games/${game}/tribes/${from_tribe}`);
    } else {
      query = this.firestore.doc(`games/${game}`);
    }
    return (await query.get()).data().count_teams;
  };

  static batch_update_tribe = async ({
    game = null,
    from_tribe = null,
    to_tribe = null,
  }) => {
    const teams = this.firestore
      .collection(`games/${game}/teams`)
      .where("tribe_id", "==", from_tribe);

    const players = this.firestore
      .collection(`games/${game}/players`)
      .where("tribe_id", "==", from_tribe);

    const player_count = await this.count_players({
      game,
      from_tribe,
    });

    const team_count = await this.count_teams({
      game,
      from_tribe,
    });

    const batch1 = this.firestore.batch();

    (await teams.get()).forEach(async (document_iter) => {
      batch1.update(document_iter.ref, { tribe_id: to_tribe });
    });

    (await players.get()).forEach(async (document_iter) => {
      batch1.update(document_iter.ref, { tribe_id: to_tribe });
    });

    await batch1.commit();

    const batch2 = this.firestore.batch();

    let ref = this.firestore.doc(`games/${game}/tribes/${to_tribe}`);

    let count = (await ref.get()).data().count_players;

    let total = count + player_count;

    batch2.update(ref, { count_players: total });

    ref = this.firestore.doc(`games/${game}/tribes/${to_tribe}`);

    count = (await ref.get()).data().count_teams;

    total = count + team_count;

    batch2.update(ref, { count_teams: total });

    ref = this.firestore.doc(`games/${game}/tribes/${from_tribe}`);

    count = (await ref.get()).data().count_players;

    total = count - player_count;

    batch2.update(ref, { count_teams: total });

    ref = this.firestore.doc(`games/${game}/tribes/${from_tribe}`);

    count = (await ref.get()).data().count_teams;

    total = count - team_count;

    batch2.update(ref, { count_teams: total });

    return await batch2.commit();
  };

  static player_from_id = async ({ game = null, id = null }) => {
    return (
      await this.firestore.doc(`games/${game}/players/${id}`).get()
    ).data();
  };

  static team_from_id = async ({ game = null, id = null }) => {
    return (await this.firestore.doc(`games/${game}/teams/${id}`).get()).data();
  };

  static count_votes = async ({
    game = null,
    from_team = null,
    is_for_win = false,
  }) => {
    let player_counts = {};

    const query = this.firestore.collection(`games/${game}/votes`);

    if (from_team) {
      query.where("team_id", "==", from_team);

      const voteFromIds = [];
      (await query.get()).forEach((vote) => {
        voteFromIds.push(vote.data());
      });

      const playerPromises = voteFromIds.map(async ({ from_id }) => {
        return this.player_from_id({ game, id: from_id });
      });
      const players = await Promise.all(playerPromises);

      const teamPromises = players.map((player) => {
        return this.team_from_id({ game, id: player.team_id });
      });
      const teams = await Promise.all(teamPromises);

      for (let i = 0; i < teams.length; i++) {
        const team = teams[i];
        const player = players[i];
        const vote = voteFromIds[i];

        const value = player_counts[vote.to_id];
        if (isNaN(value)) {
          player_counts[vote.to_id] = 1;
        } else {
          player_counts[vote.to_id] += 1;
        }
      }
    } else {
      const voteFromIds = [];
      (await query.get()).forEach((vote) => {
        const data = vote.data();

        const value = player_counts[data.to_id];
        if (isNaN(value)) {
          player_counts[data.to_id] = 1;
        } else {
          player_counts[data.to_id] += 1;
        }
      });
    }

    return player_counts;
  };

  static get_game_info = async ({ game = null }) => {
    if (!game) return false;
    const response = (
      await this.firestore.collection(`games`).doc(`${game}`).get()
    ).data();
    return response;
  };

  static add_game = async ({ game = null, hashtag = null, testId = null }) => {
    if (!game) return false;
    if (!hashtag) return false;

    const response = await this.firestore.collection(`games`).add({
      game,
      hashtag,
      count_players: 0,
      count_teams: 0,
      count_tribes: 0,
    });

    const map = {
      id: testId ? testId : response.id,
      ...(await response.get()).data(),
    };

    await response.set(map);

    return response.id;
  };

  static add_challenge = async ({
    game = null,
    name = null,
    message = null,
    testId = null,
  }) => {
    if (!game) return false;
    if (!name) return false;
    if (!message) return false;

    const response = await this.firestore
      .collection(`games`)
      .doc(`${game}`)
      .collection(`challenges`)
      .add({
        name,
        message,
        start_timestamp: Date.now(),
        end_timestamp: Date.now() + 10080000,
      });

    const map = {
      id: testId ? testId : response.id,
      ...(await response.get()).data(),
    };

    await response.set(map);

    return (await response.get()).data();
  };

  static add_submission_entry = async ({
    game = null,
    likes = null,
    views = null,
    player_id = null,
    team_id = null,
    tribe_id = null,
    challenge_id = null,
    url = null,
    testId = null,
  }) => {
    if (
      (!game || !likes || !views || !player_id,
      !team_id,
      !tribe_id || !challenge_id || !url)
    )
      return false;

    const response = await this.firestore
      .collection(`games`)
      .doc(`${game}`)
      .collection(`entries`)
      .add({
        likes,
        views,
        player_id,
        team_id,
        tribe_id,
        challenge_id,
        url,
      });

    const map = {
      id: testId ? testId : response.id,
      ...(await response.get()).data(),
    };

    await response.set(map);

    return (await response.get()).data();
  };

  static add_player = async ({
    game = null,
    tiktok = null,
    email = null,
    tribe_id = null,
    team_id = null,
    active = null,
    testId = null,
    phone = null,
    code = null,
  }) => {
    if (
      !game ||
      !tiktok ||
      !email ||
      !tribe_id ||
      !team_id ||
      !active ||
      !phone ||
      !code
    )
      return false;

    const response = await this.firestore
      .collection(`games`)
      .doc(`${game}`)
      .collection(`players`)
      .add({
        tiktok,
        email,
        tribe_id,
        team_id,
        active,
        phone,
        code,
      });

    const map = {
      id: testId ? testId : response.id,
    };

    await response.update(map);

    const data = (await response.get()).data();

    return data;
  };

  static add_vote = async ({
    game = null,
    from_id = null,
    to_id = null,
    team_id = null,
    is_for_win = null,
    testId = null,
  }) => {
    if (!game || !from_id || !to_id || !team_id || !is_for_win) return false;

    const response = await this.firestore
      .collection(`games`)
      .doc(`${game}`)
      .collection(`votes`)
      .add({
        from_id,
        to_id,
        team_id,
        is_for_win,
      });

    const map = {
      id: testId ? testId : response.id,
      ...(await response.get()).data(),
    };

    await response.set(map);

    return (await response.get()).data();
  };

  static verify_code = async ({ phone = null, code = null, game = null }) => {
    if (!phone || !code || !game) return false;

    const player = this.firestore
      .collection(`games/${game}/players`)
      .where("phone", "==", phone)
      .where("code", "==", code)
      .limit(1);

    const query = await player.get();

    if (!query.docs.length) throw new Error("player not found");

    const data = query.docs[0];

    data.ref.update({ active: true });

    return "verified";
  };
}
