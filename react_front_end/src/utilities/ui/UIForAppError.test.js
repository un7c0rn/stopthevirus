import "@testing-library/jest-dom";
import React from "react";
import { render, screen } from "@testing-library/react";
import useErrorBoundary from "use-error-boundary";
import { renderHook } from "@testing-library/react-hooks";
import { CustomUiError } from "../Utilities";
import { Router } from "react-router-dom";
import { createMemoryHistory } from "history";

const WillThrowError = () => {
  const throwError = () => {
    throw new Error("Error thrown");
  };
  return <>{throwError()}</>;
};

describe("CustomUiError", () => {
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

    const { result, rerender } = renderHook(() => useErrorBoundary());

    const { ErrorBoundary } = result.current;

    const history = createMemoryHistory();

    const { debug } = render(
      <Router history={history}>
        <ErrorBoundary
          render={() => <WillThrowError />}
          renderError={({ error }) => (
            <CustomUiError error={error} type="app" />
          )}
        />
      </Router>
    );

    expect(screen.getByTestId("Game App Error Page")).toBeDefined();
    expect(screen.getByText(/error thrown/i)).toBeDefined();
  });
});
