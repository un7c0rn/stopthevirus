import "@testing-library/jest-dom";
import React from "react";
import { render, fireEvent, screen } from "@testing-library/react";
import StartGameInputs from "../../../pages/components/StartGameInputs";
import "@testing-library/jest-dom";

function tikTokLocater() {
  return screen.getByLabelText("Tik Tok");
}

function phoneNumberLocator() {
  return screen.getByLabelText("SMS Phone Number");
}

function startGameLocator() {
  return screen.getByText("Start a game");
}

function gameNameLocator() {
  return screen.getByLabelText("Game Hashtag");
}

test("TikTok input", () => {
  const testMessage = "Test Message";
  render(<StartGameInputs />);
  fireEvent.change(tikTokLocater(), {
    target: { value: testMessage },
  });
  expect(tikTokLocater().value).toEqual(testMessage);
});

test("Phone number input", () => {
  const testMessage = "+1 (23)"; //this component will automatically add parenthesis
  render(<StartGameInputs />);
  fireEvent.change(phoneNumberLocator(), {
    target: { value: testMessage },
  });
  expect(phoneNumberLocator().value).toEqual(testMessage);
});

test("Game name input", () => {
  const testMessage = "Test Message";
  render(<StartGameInputs />);
  fireEvent.change(gameNameLocator(), {
    target: { value: testMessage },
  });
  expect(gameNameLocator().value).toEqual(testMessage);
});

test("Phone number submit invalid", () => {
  render(<StartGameInputs />);
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(startGameLocator());
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "true");
});

test("Phone number submit short invalid", () => {
  render(<StartGameInputs />);
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "false");

  //enter invalid phone #
  const testMessage = "+1";
  fireEvent.change(phoneNumberLocator(), {
    target: { value: testMessage },
  });

  fireEvent.click(startGameLocator());
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "true");
});

test("Phone number submit valid", () => {
  render(<StartGameInputs />);
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "false");

  //enter valid phone #
  const testMessage = "+1 (234) 567-8900";
  fireEvent.change(phoneNumberLocator(), {
    target: { value: testMessage },
  });

  fireEvent.click(startGameLocator());
  expect(phoneNumberLocator()).toHaveAttribute("aria-invalid", "false");
});

test("game name submit valid", () => {
  const testMessage = "Test Message";
  render(<StartGameInputs />);
  expect(gameNameLocator()).toHaveAttribute("aria-invalid", "false");
  fireEvent.change(gameNameLocator(), {
    target: { value: testMessage },
  });
  fireEvent.click(startGameLocator());

  expect(gameNameLocator()).toHaveAttribute("aria-invalid", "false");
});

test("game name submit invalid", () => {
  render(<StartGameInputs />);
  expect(gameNameLocator()).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(startGameLocator());

  expect(gameNameLocator()).toHaveAttribute("aria-invalid", "true");
});

test("tiktok submit valid", () => {
  const testMessage = "Test Message";
  render(<StartGameInputs />);
  expect(gameNameLocator()).toHaveAttribute("aria-invalid", "false");
  fireEvent.change(tikTokLocater(), {
    target: { value: testMessage },
  });
  fireEvent.click(startGameLocator());

  expect(tikTokLocater()).toHaveAttribute("aria-invalid", "false");
});

test("tiktok submit invalid", () => {
  render(<StartGameInputs />);
  expect(tikTokLocater()).toHaveAttribute("aria-invalid", "false");
  fireEvent.click(startGameLocator());

  expect(tikTokLocater()).toHaveAttribute("aria-invalid", "true");
});
