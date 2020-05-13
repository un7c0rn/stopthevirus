/**
 * @jest-environment node
 */

import { metricParser, getProfile } from "./TikTok";

describe("TikTok service", () => {
  it("should return video metadata", async () => {
    jest.setTimeout(10000);
    const url = "https://www.tiktok.com/@tiktok/video/6807491984882765062";
    const data = await metricParser(url);
    expect(data.id).toBe("6807491984882765062");
  });

  it("should not return information about a video when no url is provided", async () => {
    const url = null;
    const data = await metricParser(url);
    expect(data).toBe(undefined);
  });

  it("should not return information about a person when no url is provided", async () => {
    const url = null;
    const data = await getProfile(url);
    expect(data).toBe(undefined);
  });

  it("should return information about a person when url is provided", async () => {
    jest.setTimeout(10000);
    const handle = "who";
    const { user } = await getProfile(handle);
    console.log("..", user);
    expect(user.uniqueId).toBe(handle);
  });
});
