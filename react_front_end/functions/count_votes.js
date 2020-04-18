import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.game || !body.from_tribe || !body.is_for_win)
      throw new Error("problem with data in body");

    Firestore.initialise();

    const response = await Firestore.count_votes({
      game: body.game,
      from_tribe: body.from_tribe,
      is_for_win: body.is_for_win,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(response) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
