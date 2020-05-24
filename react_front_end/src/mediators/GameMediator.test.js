/**
 * @jest-environment node
 */
import {
  startGame,
  createChallenge,
  joinGame,
  submitChallenge,
} from "./GameMediator";

describe("StartGame", () => {
  it("should not start a new game if data is missing", async () => {
    const obj = {
      handle: "who",
      phone: null,
      hashtag: null,
    };

    const response = await startGame(obj);

    expect(response).toBe(false);
  });

  it("should start a new game", async () => {
    jest.setTimeout(30000);
    const obj = {
      handle: "who",
      // phone: process.env.REACT_APP_phone_number,
      phone: "15555555555",
      hashtag: "#who",
    };

    const response = await startGame(obj);

    expect(response).toBe(true);
  });

  it("should not create a challenge if data is missing", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      name: null,
      message: "These are the instructions for the mime me challenge.",
    };
    const response = await createChallenge(payload);

    expect(response).toBe(false);
  });

  it("should create a challenge", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      name: "Mime me",
      message: "These are the instructions for the mime me challenge.",
      phone: "XXXXXXXXXXXX",
      testId: true,
    };
    const response = await createChallenge(payload);

    expect(response).toBe(true);
  });

  it("should not join a game if data is missing", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      tiktok: null,
    };
    const response = await joinGame(payload);

    expect(response).toBe(false);
  });

  it("should join a game", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      tiktok: "how",
      phone: "XXXXXXXXXXXX",
      testId: true,
    };
    const response = await joinGame(payload);

    expect(response).toBe(true);
  });

  it("should not submit a challenge video if data is missing", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      tiktok: null,
    };
    const response = await submitChallenge(payload);

    expect(response).toBe(false);
  });

  it("should submit a challenge video for a game", async () => {
    const payload = {
      game: "0H3RzPqfq4dnf47BSgve",
      phone: "XXXXXXXXXXXX",
      url: "https://www.tiktok.com/@tiktok/video/6807491984882765062",
      challenge: "2IADVgFgQ0lryWtxiMEr",
      testId: true,
    };
    const response = await submitChallenge(payload);

    console.log(response);

    expect(response).toBe(true);
  });
});
