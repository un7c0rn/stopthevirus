import '@testing-library/jest-dom'
import React from "react";
import {render, fireEvent, screen} from '@testing-library/react'
import StartGameInputs from "../../../pages/components/StartGameInputs";




test("TikTok input", () => {
  const testMessage = 'Test Message';
  render(<StartGameInputs />)
  fireEvent.change(screen.getByLabelText("Tik Tok"), {
    target: {value: testMessage},
  });
  expect(screen.getByLabelText("Tik Tok").value).toEqual(testMessage);
});

test("Phone number input", async () => {
  const testMessage = '+1 (23)';//this component will automatically add parenthesis
  render(<StartGameInputs />)
  fireEvent.change(screen.getByLabelText("SMS Phone Number"), {
    target: {value: testMessage},
  });
  expect(screen.getByLabelText("SMS Phone Number").value).toEqual(testMessage);
});

test("Game name input", async () => {
  const testMessage = 'Test Message';
  render(<StartGameInputs />)
  fireEvent.change(screen.getByLabelText("Your Game Name"), {
    target: {value: testMessage},
  });
  expect(screen.getByLabelText("Your Game Name").value).toEqual(testMessage);
});

test("Phone number submit", async () => {
  render(<StartGameInputs />)
  //expect(screen.getByLabelText("SMS Phone Number").className).toNotContain("error");
  fireEvent.change(screen.getByText("Start a game"), new MouseEvent('click'));

  screen.debug(screen.getByLabelText("SMS Phone Number"))
  expect(screen.getByLabelText("SMS Phone Number").className).toContain("error");
});
