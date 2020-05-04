import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const game = event.queryStringParameters.game || null;
    if (!game) throw new Error("problem with game");
    const phone = event.queryStringParameters.phone || null;
    if (!phone) throw new Error("problem with phone");
    const code = event.queryStringParameters.code || null;
    if (!code) throw new Error("problem with code");

    const response = await Firestore.getInstance().verify_code({
      game,
      phone,
      code,
    });

    callback(null, {
      statusCode: 301,
      headers: {
        "Content-Type": "text/richtext",
        Location: `${process.env.WEBHOOK_REDIRECT_URL}`,
      },
      body: JSON.stringify(response),
    });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
