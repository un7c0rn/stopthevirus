// Google FireStore implementation
import firebase, { firestore } from "firebase-admin";
import credentials from "../../service_account/stv-game-db-test-0f631b94adde.json";

export default class Firestore {
  #firestoreClient;

  initialise = () => {
    // Web app's Firebase configuration
    var firebaseConfig = {
      apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
      authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
      databaseURL: process.env.REACT_APP_FIREBASE_DB_URL,
      projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
      storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.REACT_APP_FIREBASE_APP_ID,
      measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
    };
    // Initialize Firebase
    const app = firebase.initializeApp({
      credential: firebase.credential.cert(credentials),
      databaseURL: "https://stv-game-db-test.firebaseio.com",
    });

    this.firestoreClient = firebase.firestore(app);
    const firestoreClient = this.firestoreClient;
    return { firebase, firestoreClient };
  };

  tribe_from_id = async (game = null, id = null) => {
    return await (
      await this.firestoreClient.doc(`games/${game}/tribes/${id}`).get()
    ).data();
  };

  count_players = async ({
    game = null,
    from_tribe = null,
    from_team = null,
  }) => {
    if (from_tribe) {
      return (
        await this.firestoreClient
          .doc(`games/${game}/tribes/${from_tribe}`)
          .get()
      ).data().count_players;
    } else if (from_team) {
      return (
        await this.firestoreClient.doc(`games/${game}/teams/${from_team}`).get()
      ).data().count_players;
    } else {
      return (await this.firestoreClient.doc(`games/${game}`).get()).data()
        .count_players;
    }
  };

  count_teams = async ({
    game = null,
    from_tribe = null,
    active_team_predicate_value = true,
  }) => {
    let query;
    if (from_tribe) {
      query = this.firestoreClient.doc(`games/${game}/tribes/${from_tribe}`);
    } else {
      query = this.firestoreClient.doc(`games/${game}`);
    }
    return (await query.get()).data().count_teams;
  };

  // def batch_update_tribe(self, from_tribe: Tribe, to_tribe: Tribe) -> None:
  batch_update_tribe = async ({
    game = null,
    from_tribe = null,
    to_tribe = null,
  }) => {
    const teams = this.firestoreClient
      .collection(`games/${game}/teams`)
      .where("tribe_id", "==", from_tribe);

    const players = this.firestoreClient
      .collection(`games/${game}/players`)
      .where("tribe_id", "==", from_tribe);

    const player_count = await this.count_players({ game, from_tribe });

    const team_count = await this.count_teams({ game, from_tribe });

    const batch1 = this.firestoreClient.batch();

    (await teams.get()).forEach(async (document_iter) => {
      batch1.update(document_iter.ref, { tribe_id: to_tribe });
    });

    (await players.get()).forEach(async (document_iter) => {
      batch1.update(document_iter.ref, { tribe_id: to_tribe });
    });

    let response = await batch1.commit();

    const batch2 = this.firestoreClient.batch();

    let ref = this.firestoreClient.doc(`games/${game}/tribes/${to_tribe}`);

    let count = (await ref.get()).data().count_players;

    let total = count + player_count;

    batch2.update(ref, { count_players: total });

    ref = this.firestoreClient.doc(`games/${game}/tribes/${to_tribe}`);

    count = (await ref.get()).data().count_teams;

    total = count + team_count;

    batch2.update(ref, { count_teams: total });

    ref = this.firestoreClient.doc(`games/${game}/tribes/${from_tribe}`);

    count = (await ref.get()).data().count_players;

    total = count - player_count;

    batch2.update(ref, { count_teams: total });

    ref = this.firestoreClient.doc(`games/${game}/tribes/${from_tribe}`);

    count = (await ref.get()).data().count_teams;

    total = count - team_count;

    batch2.update(ref, { count_teams: total });

    await batch2.commit();
  };
}
