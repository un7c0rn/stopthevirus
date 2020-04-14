// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body) throw new Error("problem with data in body");
    callback(null, { statusCode: 200, body: "ok" });
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
