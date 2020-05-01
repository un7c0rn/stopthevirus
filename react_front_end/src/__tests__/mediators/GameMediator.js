/**
 * @jest-environment node
 */
import { startGame } from "../../mediators/GameMediator";

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
    const obj = {
      handle: "who",
      phone: process.env.REACT_APP_phone_number,
      hashtag: "#who",
    };

    const response = await startGame(obj);

    expect(response).toBe(true);
  });
});
