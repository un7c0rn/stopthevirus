import "@testing-library/jest-dom";
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import GameInfoPage from "./GameInfoPage";
import { AppContext } from "../../App";

// Needs to be split into smaller test units
describe("GameInfo", () => {
  describe("GameName component", () => {
    xit("should exist", async () => {
      const gameInfo = {};
      const setGameInfo = () => {};
      render(
        <AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <GameInfoPage />
        </AppContext.Provider>
      );
      expect(screen.getByTestId("Game Name")).toBeTruthy();
    });

    xit("should display the game name", async () => {
      const testName = "My Test";
      const gameInfo = { name: testName };
      const setGameInfo = () => {};
      render(
        <AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <GameInfoPage />
        </AppContext.Provider>
      );
      let el = screen.getByTestId("Game Name");
      expect(el).toHaveTextContent(testName);
    });
  });
});
