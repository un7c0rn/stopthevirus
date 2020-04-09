import fetch from "node-fetch";

export const metricParser = async (url = null) => {
  try {
    if (!url) throw Error("TikTok URL not provided");
    const response = await fetch(
      `http://localhost:8888/.netlify/functions/tiktok?url=${url}`
    );
    const data = await response.json();
    console.dir(data.video);
    return data.video;
  } catch (e) {
    console.warn(e);
  } finally {
    // google analytics
  }
};
