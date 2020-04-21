import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (
      !body.game ||
      !body.likes ||
      !body.views ||
      !body.player_id ||
      !body.team_id ||
      !body.tribe_id ||
      !body.challenge_id ||
      !body.url
    )
      throw new Error("problem with data in body");

    Firestore.initialise();

    const response = await Firestore.add_submission_entry({
      game: body.game,
      likes: body.likes,
      views: body.views,
      player_id: body.player_id,
      team_id: body.team_id,
      tribe_id: body.tribe_id,
      challenge_id: body.challenge_id,
      url: body.url,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(response) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
