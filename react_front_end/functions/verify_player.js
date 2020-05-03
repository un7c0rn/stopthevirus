// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.phone) throw new Error("problem with data in body");
    if (!body.code) throw new Error("problem with data in body");
    if (!body.game) throw new Error("problem with data in body");

    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const client = require("twilio")(accountSid, authToken);

    const url = encodeURI(
      `${process.env.WEBHOOK_CODE_VERIFY}/.netlify/functions/verify_code?phone=${body.phone}&code=${body.code}&game=${body.game}`
    );

    const sms = await client.messages.create({
      body: `Hi there! Click the link to verify`,
      mediaUrl: url,
      from: "+12029527488",
      to: `+${body.phone}`,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(sms.sid) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
