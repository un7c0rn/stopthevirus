// Google FireStore implementation
import dotenv from "dotenv";
import firebase, { firestore as fb } from "firebase-admin";

dotenv.config();

export default class Firestore {
  static firestore;

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

    // Initialize Firebase
    const app = firebase.initializeApp(
      {
        credential: firebase.credential.cert(credentials),
        databaseURL: "https://stv-game-db-test.firebaseio.com",
      },
      "VIR-US"
    );

    Firestore.firestore = fb(app);

    return { firebase, firestore: Firestore.firestore };
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
        // if (team.id !== from_team || !player.active) {
        //   continue;
        // }
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
        // if (!data.is_for_win) {
        //   continue;
        // }
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
}

/*

def count_votes(self, from_team: Team = None, is_for_win: bool = False) -> Dict[Text, int]:
    player_counts = {}

    query = self._client.collection(
        'games/{}/votes'.format(self._game_id))
    if from_team:
        query = query.where('team_id', '==', from_team.id)

        for vote in FirestoreVoteStream(query.stream()):
            voter = self.player_from_id(vote.from_id)
            team = self.team_from_id(voter.team_id)
            if team.id != from_team.id or not voter.active:
                continue

            if vote.to_id not in player_counts:
                player_counts[vote.to_id] = 1
            else:
                player_counts[vote.to_id] = player_counts[vote.to_id] + 1
    else:
        for vote in FirestoreVoteStream(query.stream()):
            if not vote.is_for_win:
                continue

            if vote.to_id not in player_counts:
                player_counts[vote.to_id] = 1
            else:
                player_counts[vote.to_id] = player_counts[vote.to_id] + 1

    return player_counts
*/
