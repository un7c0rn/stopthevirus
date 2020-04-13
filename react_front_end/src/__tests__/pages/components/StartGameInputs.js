import '@testing-library/jest-dom'
import React from "react";
import {render, fireEvent, screen} from '@testing-library/react'
import StartGameInputs from "../../../pages/components/StartGameInputs";




test("TikTok input", () => {
  const testMessage = 'Test Message'
  render(<StartGameInputs />)
  fireEvent.change(screen.getByLabelText("Tik Tok"), {
    target: {value: testMessage},
  });
  expect(screen.getByLabelText("Tik Tok").value).toEqual(testMessage);
});

test("Phone number input", async () => {
});

test("Game name input", async () => {
});
