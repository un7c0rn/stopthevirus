import '@testing-library/jest-dom'
import React from "react";
import {render, fireEvent, screen} from '@testing-library/react'
import StartGameInputs from "../../../pages/components/StartGameInputs";
import { act } from 'react-dom/test-utils';
import '@testing-library/jest-dom'




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

test("Phone number submit invalid", async () => {
  render(<StartGameInputs />)
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(screen.getByText("Start a game"));
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "true");
});

test("Phone number submit short invalid", async () => {
  render(<StartGameInputs />)
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "false");

  //enter invalid phone #
  const testMessage = '+1';
  fireEvent.change(screen.getByLabelText("SMS Phone Number"), {
    target: {value: testMessage},
  });

  fireEvent.click(screen.getByText("Start a game"));
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "true");
});

test("Phone number submit valid", async () => {
  render(<StartGameInputs />)
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "false");

  //enter valid phone #
  const testMessage = '+1 (234) 567-8900';
  fireEvent.change(screen.getByLabelText("SMS Phone Number"), {
    target: {value: testMessage},
  });

  fireEvent.click(screen.getByText("Start a game"));
  expect(screen.getByLabelText("SMS Phone Number")).toHaveAttribute("aria-invalid", "false");
});

test("game name submit valid", async () => {
  const testMessage = 'Test Message';
  render(<StartGameInputs />)
  expect(screen.getByLabelText("Your Game Name")).toHaveAttribute("aria-invalid", "false");
  fireEvent.change(screen.getByLabelText("Your Game Name"), {
    target: {value: testMessage},
  });
  fireEvent.click(screen.getByText("Start a game"));

  expect(screen.getByLabelText("Your Game Name")).toHaveAttribute("aria-invalid", "false");
});

test("game name submit invalid", async () => {
  render(<StartGameInputs />)
  expect(screen.getByLabelText("Your Game Name")).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(screen.getByText("Start a game"));

  expect(screen.getByLabelText("Your Game Name")).toHaveAttribute("aria-invalid", "true");
});

test("tiktok submit valid", async () => {
  const testMessage = 'Test Message';
  render(<StartGameInputs />)
  expect(screen.getByLabelText("Your Game Name")).toHaveAttribute("aria-invalid", "false");
  fireEvent.change(screen.getByLabelText("Tik Tok"), {
    target: {value: testMessage},
  });
  fireEvent.click(screen.getByText("Start a game"));

  expect(screen.getByLabelText("Tik Tok")).toHaveAttribute("aria-invalid", "false");
});

test("tiktok submit invalid", async () => {
  render(<StartGameInputs />)
  expect(screen.getByLabelText("Tik Tok")).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(screen.getByText("Start a game"));

  expect(screen.getByLabelText("Tik Tok")).toHaveAttribute("aria-invalid", "true");
});
