import React from "react";
import { render, waitFor } from "@testing-library/react";
import App from "../../src/App";

test("renders progressbar", async () => {
  const { getByRole } = render(<App />);
  const element = getByRole(/progressbar/i);
  expect(element).toBeInTheDocument();
});
