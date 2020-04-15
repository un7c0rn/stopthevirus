/**
 * @jest-environment node
 */

import { metricParser } from "../../services/TikTok";

describe("TikTok service", () => {
  it("should return video metadata", async () => {
    jest.setTimeout(10000);
    const url = "https://www.tiktok.com/@tiktok/video/6807491984882765062";
    const data = await metricParser(url);
    expect(data.id).toBe("6807491984882765062");
  });

  test("no url for video metadata", async () => {
    const url = null;
    const data = await metricParser(url);
    expect(data).toBe(undefined);
  });
});
