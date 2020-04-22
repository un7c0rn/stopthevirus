import "@testing-library/jest-dom";
import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
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
    expect(true).toBe(true);
  });

  describe("GameInfo component", () => {
    describe("GameName component", () => {
      it ("should exist", async () => {
        const gameInfo = {};
        const setGameInfo = () => {};
        render(<AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <GameInfoPage />
        </AppContext.Provider>);
        expect(screen.getByText("Game")).toBeTruthy();
      });
    });
  });

});
