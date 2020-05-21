const TikTokScraper = require("tiktok-scraper");
// Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method
exports.handler = (event, context, callback) => {
  try {
    const url = event.queryStringParameters.url || null;
    if (!url) throw new Error("problem with url");

    (async () => {
      try {
        const videoMeta = await TikTokScraper.getVideoMeta(url);
        callback(null, {
          statusCode: 200,
          body: JSON.stringify({ video: videoMeta }),
        });
      } catch (error) {
        callback(null, { statusCode: 500, body: { error } });
      }
    })();
  } catch (err) {
    callback(null, { statusCode: 500, body: err.toString() });
  }
};
