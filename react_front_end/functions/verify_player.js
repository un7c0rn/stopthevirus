// import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.phone) throw new Error("problem with data in body");

    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const client = require("twilio")(accountSid, authToken);

    const sms = await client.messages.create({
      body: "Hi there!",
      from: "+12029527488",
      to: body.phone,
    });

    // const response = Firestore.getInstance().add_player({
    //   game: body.game,
    //   tiktok: body.tiktok,
    //   email: body.email,
    //   tribe_id: body.tribe_id,
    //   team_id: body.team_id,
    //   active: body.active,
    //   phone: body.phone,
    // });

    callback(null, { statusCode: 200, body: JSON.stringify(sms.sid) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
