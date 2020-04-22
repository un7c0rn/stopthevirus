import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;

    if (
      !body.game ||
      !body.from_id ||
      !body.to_id ||
      !body.team_id ||
      !body.is_for_win
    )
      throw new Error("problem with data in body");

    Firestore.initialise();

    const response = await Firestore.add_vote({
      game: body.game,
      from_id: body.from_id,
      to_id: body.to_id,
      team_id: body.team_id,
      is_for_win: body.is_for_win,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(response) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
