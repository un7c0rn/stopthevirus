import Firestore from "../src/services/Firestore";
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (
      !body.game ||
      !body.tiktok ||
      !body.email ||
      !body.tribe_id ||
      !body.team_id ||
      !body.active ||
      !body.phone ||
      !body.code
    )
      throw new Error("problem with data in body");

    const response = await Firestore.getInstance().add_player({
      game: body.game,
      tiktok: body.tiktok,
      email: body.email,
      tribe_id: body.tribe_id,
      team_id: body.team_id,
      active: body.active,
      phone: body.phone,
      code: body.code,
    });

    callback(null, { statusCode: 200, body: JSON.stringify(response) });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
