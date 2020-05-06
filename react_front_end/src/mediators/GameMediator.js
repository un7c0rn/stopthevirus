import fetch from "node-fetch";
import { getProfile } from "../services/TikTok";
import { v4 as uuidv4 } from "uuid";

export const startGame = async ({
  handle = null,
  phone = null,
  hashtag = null,
  testId = "a1b2c3d4e5f6g7h8i9j",
}) => {
  if (!handle || !phone || !hashtag) return false;

  await getProfile(handle);

  // TODO where is the game name coming from
  const gameData = {
    game: "PREDEFINED GAME NAME",
    hashtag,
    testId,
  };

  const addedGameId = await fetch(
    process.env?.REACT_DEVELOPMENT_ENV === "development"
      ? "http://localhost:8888" + `/.netlify/functions/add_game`
      : process.env?.WEBHOOK_REDIRECT_URL + `/.netlify/functions/add_game`,
    {
      method: "POST",
      body: JSON.stringify(gameData),
    }
  );

  const gameId = await addedGameId.json();

  const code = uuidv4();
  const number = phone.replace("+", "").replace(/ /g, "");

  const playerData = {
    game: gameId,
    tiktok: handle,
    email: 1,
    tribe_id: 1,
    team_id: 1,
    active: 1,
    testId,
    phone: number,
    code,
  };

  await fetch(
    process.env?.REACT_DEVELOPMENT_ENV === "development"
      ? "http://localhost:8888" + `/.netlify/functions/add_player`
      : process.env?.WEBHOOK_REDIRECT_URL + `/.netlify/functions/add_player`,
    {
      method: "POST",
      body: JSON.stringify(playerData),
    }
  );

  // TODO: Debug data not being in response

  const verifyData = {
    phone: number,
    code,
    game: gameId,
  };

  const sendCodeResponse = await fetch(
    process.env?.REACT_DEVELOPMENT_ENV === "development"
      ? "http://localhost:8888" + `/.netlify/functions/verify_player`
      : process.env?.WEBHOOK_REDIRECT_URL + `/.netlify/functions/verify_player`,
    {
      method: "POST",
      body: JSON.stringify(verifyData),
    }
  );

  return sendCodeResponse.status === 200;
};

export const createChallenge = async ({
  game = null,
  name = null,
  message = null,
  phone = null,
  testId = "a1b2c3d4e5f6g7h8i9j",
}) => {
  if (!phone || !game || !name) return false;

  const challengePayload = {
    game,
    name,
    message,
    phone,
    testId: "a1b2c3d4e5f6g7h8i9j",
  };

  const createChallengeResponse = await fetch(
    process.env?.REACT_DEVELOPMENT_ENV === "development"
      ? "http://localhost:8888" + `/.netlify/functions/add_challenge`
      : process.env?.WEBHOOK_REDIRECT_URL + `/.netlify/functions/add_challenge`,
    {
      method: "POST",
      body: JSON.stringify(challengePayload),
    }
  );

  return createChallengeResponse.status === 200;
};
