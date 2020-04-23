import "@testing-library/jest-dom";
import React from "react";
import { render, screen } from "@testing-library/react";
import GameInfoPage from "../../pages/GameInfoPage";
import {AppContext} from "../../App";
import "@testing-library/jest-dom";


describe("GameInfoPage", () => {
  it("should pass a smoke test", async () => {
    const gameInfo = {};
    const setGameInfo = () => {};
    render(<AppContext.Provider value={{ gameInfo, setGameInfo }}>
      <GameInfoPage />
    </AppContext.Provider>);
    //will throw errors if the component fails to initialize
    expect(true).toBe(true);
  });

  it("should exist", async () => {
    const gameInfo = {};
    const setGameInfo = () => {};
    render(<AppContext.Provider value={{ gameInfo, setGameInfo }}>
      <GameInfoPage />
    </AppContext.Provider>);
    expect(screen.getByTestId("Game Info Page")).toBeTruthy();
  });

  describe("GameInfo component", () => {
    describe("GameName component", () => {
      it ("should exist", async () => {
        const gameInfo = {};
        const setGameInfo = () => {};
        render(<AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <GameInfoPage />
        </AppContext.Provider>);
        expect(screen.getByTestId("Game Name")).toBeTruthy();
      });

      it ("should display the game name", async () => {
        const testName = "My Test";
        const gameInfo = {name: testName};
        const setGameInfo = () => {};
        render(<AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <GameInfoPage />
        </AppContext.Provider>);
        let el = screen.getByTestId("Game Name");
        expect(el).toHaveTextContent(testName);
      });
    });
  });

});
