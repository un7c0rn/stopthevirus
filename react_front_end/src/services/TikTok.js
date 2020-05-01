import fetch from "node-fetch";

export const metricParser = async (url = null) => {
  try {
    if (!url) throw Error("TikTok URL not provided");
    const response = await fetch(
      `http://localhost:8888/.netlify/functions/tiktok_video?url=${url}`
    );
    const data = await response.json();
    return data.video;
  } catch (e) {
    console.warn(e.message);
  } finally {
    // google analytics
  }
};

export const getProfile = async (handle = null) => {
  try {
    if (!handle) throw Error("TikTok handle not provided");
    const response = await fetch(
      `http://localhost:8888/.netlify/functions/tiktok_profile?handle=${handle}`
    );
    return await response.json();
  } catch (e) {
    console.warn(e.message);
  } finally {
    // google analytics
  }
};
