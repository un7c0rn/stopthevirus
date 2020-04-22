const TikTokScraper = require("tiktok-scraper");
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = (event, context, callback) => {
  try {
    const handle = event.queryStringParameters.handle || null;

    (async () => {
      if (!handle) throw new Error("problem with TikTok handle");

      try {
        const user = await TikTokScraper.getUserProfileInfo(handle);

        callback(null, {
          statusCode: 200,
          body: JSON.stringify({ user }),
        });
      } catch (error) {
        callback(null, { statusCode: 500, body: error.toString() });
      }
    })();
  } catch (err) {
    callback(null, { statusCode: 600, body: err.toString() });
  }
};
