import fetch from "node-fetch";
import { getProfile, metricParser } from "../services/TikTok";
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
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/add_game`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/add_game`,
    {
      method: "POST",
      body: JSON.stringify(gameData),
    }
  );

  const gameId = await addedGameId.json();

  if (!gameId?.length) return false;

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

  const createPlayer = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/add_player`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/add_player`,
    {
      method: "POST",
      body: JSON.stringify(playerData),
    }
  );

  const createPlayerResponse = await createPlayer.json();

  if (!createPlayerResponse?.id) return false;

  const verifyData = {
    phone: number,
    code,
    game: gameId,
  };

  const sendCodeResponse = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/verify_player`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/verify_player`,
    {
      method: "POST",
      body: JSON.stringify(verifyData),
    }
  );

  const sendCodeData = await sendCodeResponse.json();

  if (sendCodeData?.error) return false;
  return true;
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
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/add_challenge`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/add_challenge`,
    {
      method: "POST",
      body: JSON.stringify(challengePayload),
    }
  );

  return createChallengeResponse.status === 200;
};

export const joinGame = async ({
  game = null,
  tiktok = null,
  phone = null,
  testId = "a1b2c3d4e5f6g7h8i9j",
}) => {
  if (!game || !tiktok || !phone) return false;

  const code = uuidv4();

  const playerData = {
    game,
    tiktok,
    email: 1,
    tribe_id: 1,
    team_id: 1,
    active: 1,
    testId,
    phone,
    code,
  };

  const addPlayerResponse = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/add_player`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/add_player`,
    {
      method: "POST",
      body: JSON.stringify(playerData),
    }
  );

  const createPlayerResponse = await addPlayerResponse.json();

  if (!createPlayerResponse?.id) return false;

  const verifyData = {
    phone,
    code,
    game,
  };

  const sendCodeResponse = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/verify_player`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/verify_player`,
    {
      method: "POST",
      body: JSON.stringify(verifyData),
    }
  );

  const sendCodeData = await sendCodeResponse.json();

  if (sendCodeData?.error) return false;
  return true;
};

export const submitChallenge = async ({
  phone = null,
  game = null,
  url = null,
  challenge = null,
  testId = "a1b2c3d4e5f6g7h8i9j",
}) => {
  if (!phone || !game || !url || !challenge) return false;

  const data = await metricParser(url);

  const requestGamePlayer = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/get_game_player`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/get_game_player`,
    {
      method: "POST",
      body: JSON.stringify({ game, phone }),
    }
  );

  const playerData = await requestGamePlayer.json();

  const challengePayload = {
    game,
    likes: data.diggCount,
    views: data.playCount,
    player_id: playerData.id,
    team_id: playerData.team_id,
    tribe_id: playerData.tribe_id,
    challenge_id: challenge,
    url,
    testId: "a1b2c3d4e5f6g7h8i9j",
  };

  const createChallengeResponse = await fetch(
    process.env?.REACT_APP_DEVELOPMENT_ENV === "development"
      ? `http://localhost:8888/.netlify/functions/add_submission_entry`
      : `${process.env?.WEBHOOK_REDIRECT_URL}/.netlify/functions/add_submission_entry`,
    {
      method: "POST",
      body: JSON.stringify(challengePayload),
    }
  );

  return createChallengeResponse.status === 200;
};
