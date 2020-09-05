import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.game || !body.hashtag)
      throw new Error("problem with data in body");

    const response = await Firestore.getInstance().add_game({
      game: body.game,
      hashtag: body.hashtag,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(response) });
  } catch (err) {
    callback(null, { statusCode: 200, body: JSON.stringify({ error: err }) });
  }
};
