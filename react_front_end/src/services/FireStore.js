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
}
