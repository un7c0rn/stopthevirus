/**
 * @jest-environment node
 */
import { startGame, createChallenge } from "../../mediators/GameMediator";

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

  xit("should start a new game", async () => {
    jest.setTimeout(30000);
    const obj = {
      handle: "who",
      phone: process.env.REACT_APP_phone_number,
      hashtag: "#who",
    };

    const response = await startGame(obj);

    console.dir(response);

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
      phone: "447305841979",
      testId: true,
    };
    const response = await createChallenge(payload);

    expect(response).toBe(true);
  });
});
