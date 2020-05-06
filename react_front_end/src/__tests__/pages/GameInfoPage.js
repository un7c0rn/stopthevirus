import "@testing-library/jest-dom";
import React from "react";
import { render, screen } from "@testing-library/react";
import GameInfoPage from "../../pages/GameInfoPage";
import { AppContext } from "../../App";
import useErrorBoundary from "use-error-boundary";
import { renderHook } from "@testing-library/react-hooks";
import { CustomUiError } from "../../utilities/Utilities";

describe("GameInfoPage", () => {
  /**
   * Store a reference to the console.
   * When a test completes, restore the console.
   */
  const consoleReference = console.error;

  afterEach(() => {
    console.error = consoleReference;
  });

  it("should fail gracefully", async () => {
    // We don't want to see the error
    console.error = () => {};

    const { result } = renderHook(() => useErrorBoundary());

    const { ErrorBoundary } = result.current;

    const { debug } = render(
      <ErrorBoundary
        render={() => <GameInfoPage />}
        renderError={({ error }) => <CustomUiError error={error} type="app" />}
      />
    );

    expect(screen.getByTestId("Game App Error Page")).toBeDefined();
  });

  it("should render the page", async () => {
    const gameInfo = {};
    const setGameInfo = () => {};

    render(
      <AppContext.Provider value={{ gameInfo, setGameInfo }}>
        <GameInfoPage />
      </AppContext.Provider>
    );

    expect(screen.getByTestId("Game Info Page")).toBeDefined();
  });
});
