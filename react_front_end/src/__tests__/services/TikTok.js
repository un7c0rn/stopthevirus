/**
 * @jest-environment node
 */

import { metricParser } from "../../services/TikTok";

test("video metadata", async () => {
  const url = "https://www.tiktok.com/@tiktok/video/6807491984882765062";
  const data = await metricParser(url);
  expect(data.id).toBe("6807491984882765062");
});

test("no url for video metadata", async () => {
  const url = null;
  const data = await metricParser(url);
  expect(data).toBe(undefined);
});
