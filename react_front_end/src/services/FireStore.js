// Google FireStore implementation
import firebase from "firebase-admin";

export const initialise = () => {
  // Your web app's Firebase configuration
  var firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    authDomain: process.env.FIREBASE_AUTH_DOMAIN,
    databaseURL: process.env.FIREBASE_DB_URL,
    projectId: process.env.FIREBASE_PROJECT_ID,
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.FIREBASE_APP_ID,
    measurementId: process.env.FIREBASE_MEASUREMENT_ID,
  };
  // Initialize Firebase
  firebase.initializeApp(firebaseConfig, "VIR-US");
  return firebase;
};

export const countPlayers = (pool = null) => {
  // count the players in the pool
};

export const countTeams = (pool = null) => {
  // count the teams in the pool
};
