import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.game) throw new Error("problem with game data in body");
    if (!body.phone) throw new Error("problem with phone data in body");

    const response = await Firestore.getInstance().player_from_phone_number({
      game: body.game,
      phone: body.phone,
    });

    if (response) {
      callback(null, {
        statusCode: 200,
        body: JSON.stringify(response),
      });
    } else {
      callback(null, {
        statusCode: 200,
        body: JSON.stringify({ error: true }),
      });
    }
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
