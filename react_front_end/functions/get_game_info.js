import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.game) throw new Error("problem with data in body");

    const response = await Firestore.getInstance().get_game_info({
      game: body.game,
    });

    callback(null, {
      statusCode: 200,
      body: JSON.stringify(response),
    });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
