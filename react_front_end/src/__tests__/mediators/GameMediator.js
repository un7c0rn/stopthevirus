/**
 * @jest-environment node
 */
import { startGame } from "../../mediators/GameMediator";

describe("StartGame", () => {
  it("should not start a new game if data is missing", async () => {
    const obj = {
      handle: "who",
      phone: "+1 (098) 765-4321",
      hashtag: null,
    };

    const response = await startGame(obj);

    expect(response).toBe(false);
  });

  it("should start a new game", async () => {
    const obj = {
      handle: "who",
      phone: "+1 (098) 765-4321",
      hashtag: "#who",
    };

    const response = await startGame(obj);

    expect(response).toBe(true);
  });
});
