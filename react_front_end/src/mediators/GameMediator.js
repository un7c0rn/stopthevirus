import fetch from "node-fetch";
import { getProfile } from "../services/TikTok";

export const startGame = async ({
  handle = null,
  phone = null,
  hashtag = null,
  testId = "a1b2c3d4e5f6g7h8i9j",
}) => {
  if (!handle || !phone || !hashtag) return false;

  const { user } = await getProfile(handle);

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

  const playerData = {
    game: gameId,
    tiktok: handle,
    email: 1,
    tribe_id: 1,
    team_id: 1,
    active: 1,
    testId,
  };

  const addedPlayer = await fetch(
    "http://localhost:8888/.netlify/functions/add_player",
    {
      method: "POST",
      body: JSON.stringify(playerData),
    }
  );

  // TODO: Debug data not being in response

  return addedPlayer.status === 200;
};
