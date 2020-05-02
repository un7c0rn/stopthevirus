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

  const gameData = {
    game: "PREDEFINED GAME NAME",
    hashtag,
    testId,
  };

  const addedGameId = await fetch(
    "http://localhost:8888/.netlify/functions/add_game",
    {
      method: "POST",
      body: JSON.stringify(gameData),
    }
  );

  const gameId = await addedGameId.json();

  const code = uuidv4();

  const playerData = {
    game: gameId,
    tiktok: handle,
    email: 1,
    tribe_id: 1,
    team_id: 1,
    active: 1,
    testId,
    phone: phone.replace("+", "").replace(/ /g, ""),
    code,
  };

  const addedPlayer = await fetch(
    "http://localhost:8888/.netlify/functions/add_player",
    {
      method: "POST",
      body: JSON.stringify(playerData),
    }
  );

  // TODO: Debug data not being in response

  const verifyData = {
    phone,
    code,
    game: gameId,
  };

  const sendCodeResponse = await fetch(
    "http://localhost:8888/.netlify/functions/verify_player",
    {
      method: "POST",
      body: JSON.stringify(verifyData),
    }
  );

  return sendCodeResponse.status === 200;
};
