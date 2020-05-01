(function(e, a) { for(var i in a) e[i] = a[i]; }(exports, /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./count_votes.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "../src/services/Firestore.js":
/*!************************************!*\
  !*** ../src/services/Firestore.js ***!
  \************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "default", function() { return Firestore; });
/* harmony import */ var dotenv__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dotenv */ "dotenv");
/* harmony import */ var dotenv__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dotenv__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var firebase_admin__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! firebase-admin */ "firebase-admin");
/* harmony import */ var firebase_admin__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(firebase_admin__WEBPACK_IMPORTED_MODULE_1__);
function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }



dotenv__WEBPACK_IMPORTED_MODULE_0___default.a.config();
class Firestore {}

_defineProperty(Firestore, "firebase", void 0);

_defineProperty(Firestore, "firestore", void 0);

_defineProperty(Firestore, "getInstance", () => {
  if (firebase_admin__WEBPACK_IMPORTED_MODULE_1__["apps"].length < 1) {
    const {
      firebase,
      firestore
    } = Firestore.initialise();
    Firestore.firebase = firebase;
    Firestore.firestore = firestore;
  }

  Firestore.firebase = firebase_admin__WEBPACK_IMPORTED_MODULE_1__;
  Firestore.firestore = firebase_admin__WEBPACK_IMPORTED_MODULE_1__["app"]("VIR-US").firestore();
  return Firestore;
});

_defineProperty(Firestore, "initialise", () => {
  // Web app's Firebase configuration
  var credentials = {
    type: process.env.REACT_APP_type,
    project_id: process.env.REACT_APP_project_id,
    private_key_id: process.env.REACT_APP_private_key_id,
    private_key: process.env.REACT_APP_private_key.replace(/\\n/g, "\n"),
    client_email: process.env.REACT_APP_client_email,
    client_id: process.env.REACT_APP_client_id,
    auth_uri: process.env.REACT_APP_auth_uri,
    token_uri: process.env.REACT_APP_token_uri,
    auth_provider_x509_cert_url: process.env.REACT_APP_auth_provider_x509_cert_url,
    client_x509_cert_url: process.env.REACT_APP_client_x509_cert_url
  };
  const app = firebase_admin__WEBPACK_IMPORTED_MODULE_1__["initializeApp"]({
    credential: firebase_admin__WEBPACK_IMPORTED_MODULE_1__["credential"].cert(credentials),
    databaseURL: "https://stv-game-db-test.firebaseio.com"
  }, "VIR-US");
  const defaultFirebase = firebase_admin__WEBPACK_IMPORTED_MODULE_1__;
  const defaultFirestore = firebase_admin__WEBPACK_IMPORTED_MODULE_1__["firestore"](app);
  return {
    firebase: defaultFirebase,
    firestore: defaultFirestore
  };
});

_defineProperty(Firestore, "tribe_from_id", async (game = null, id = null) => {
  return await (await Firestore.firestore.doc(`games/${game}/tribes/${id}`).get()).data();
});

_defineProperty(Firestore, "count_players", async ({
  game = null,
  from_tribe = null,
  from_team = null
}) => {
  if (from_tribe) {
    return (await Firestore.firestore.doc(`games/${game}/tribes/${from_tribe}`).get()).data().count_players;
  } else if (from_team) {
    return (await Firestore.firestore.doc(`games/${game}/teams/${from_team}`).get()).data().count_players;
  } else {
    return (await Firestore.firestore.doc(`games/${game}`).get()).data().count_players;
  }
});

_defineProperty(Firestore, "count_teams", async ({
  game = null,
  from_tribe = null,
  active_team_predicate_value = true
}) => {
  let query;

  if (from_tribe) {
    query = Firestore.firestore.doc(`games/${game}/tribes/${from_tribe}`);
  } else {
    query = Firestore.firestore.doc(`games/${game}`);
  }

  return (await query.get()).data().count_teams;
});

_defineProperty(Firestore, "batch_update_tribe", async ({
  game = null,
  from_tribe = null,
  to_tribe = null
}) => {
  const teams = Firestore.firestore.collection(`games/${game}/teams`).where("tribe_id", "==", from_tribe);
  const players = Firestore.firestore.collection(`games/${game}/players`).where("tribe_id", "==", from_tribe);
  const player_count = await Firestore.count_players({
    game,
    from_tribe
  });
  const team_count = await Firestore.count_teams({
    game,
    from_tribe
  });
  const batch1 = Firestore.firestore.batch();
  (await teams.get()).forEach(async document_iter => {
    batch1.update(document_iter.ref, {
      tribe_id: to_tribe
    });
  });
  (await players.get()).forEach(async document_iter => {
    batch1.update(document_iter.ref, {
      tribe_id: to_tribe
    });
  });
  await batch1.commit();
  const batch2 = Firestore.firestore.batch();
  let ref = Firestore.firestore.doc(`games/${game}/tribes/${to_tribe}`);
  let count = (await ref.get()).data().count_players;
  let total = count + player_count;
  batch2.update(ref, {
    count_players: total
  });
  ref = Firestore.firestore.doc(`games/${game}/tribes/${to_tribe}`);
  count = (await ref.get()).data().count_teams;
  total = count + team_count;
  batch2.update(ref, {
    count_teams: total
  });
  ref = Firestore.firestore.doc(`games/${game}/tribes/${from_tribe}`);
  count = (await ref.get()).data().count_players;
  total = count - player_count;
  batch2.update(ref, {
    count_teams: total
  });
  ref = Firestore.firestore.doc(`games/${game}/tribes/${from_tribe}`);
  count = (await ref.get()).data().count_teams;
  total = count - team_count;
  batch2.update(ref, {
    count_teams: total
  });
  return await batch2.commit();
});

_defineProperty(Firestore, "player_from_id", async ({
  game = null,
  id = null
}) => {
  return (await Firestore.firestore.doc(`games/${game}/players/${id}`).get()).data();
});

_defineProperty(Firestore, "team_from_id", async ({
  game = null,
  id = null
}) => {
  return (await Firestore.firestore.doc(`games/${game}/teams/${id}`).get()).data();
});

_defineProperty(Firestore, "count_votes", async ({
  game = null,
  from_team = null,
  is_for_win = false
}) => {
  let player_counts = {};
  const query = Firestore.firestore.collection(`games/${game}/votes`);

  if (from_team) {
    query.where("team_id", "==", from_team);
    const voteFromIds = [];
    (await query.get()).forEach(vote => {
      voteFromIds.push(vote.data());
    });
    const playerPromises = voteFromIds.map(async ({
      from_id
    }) => {
      return Firestore.player_from_id({
        game,
        id: from_id
      });
    });
    const players = await Promise.all(playerPromises);
    const teamPromises = players.map(player => {
      return Firestore.team_from_id({
        game,
        id: player.team_id
      });
    });
    const teams = await Promise.all(teamPromises);

    for (let i = 0; i < teams.length; i++) {
      const team = teams[i];
      const player = players[i];
      const vote = voteFromIds[i];
      const value = player_counts[vote.to_id];

      if (isNaN(value)) {
        player_counts[vote.to_id] = 1;
      } else {
        player_counts[vote.to_id] += 1;
      }
    }
  } else {
    const voteFromIds = [];
    (await query.get()).forEach(vote => {
      const data = vote.data();
      const value = player_counts[data.to_id];

      if (isNaN(value)) {
        player_counts[data.to_id] = 1;
      } else {
        player_counts[data.to_id] += 1;
      }
    });
  }

  return player_counts;
});

_defineProperty(Firestore, "get_game_info", async ({
  game = null
}) => {
  if (!game) return false;
  const response = (await Firestore.firestore.collection(`games`).doc(`${game}`).get()).data();
  return response;
});

_defineProperty(Firestore, "add_game", async ({
  game = null,
  hashtag = null,
  testId = null
}) => {
  if (!game) return false;
  if (!hashtag) return false;
  const response = await Firestore.firestore.collection(`games`).add({
    game,
    hashtag,
    count_players: 0,
    count_teams: 0,
    count_tribes: 0
  });
  const map = {
    id: testId ? testId : response.id,
    ...(await response.get()).data()
  };
  await response.set(map);
  return response.id;
});

_defineProperty(Firestore, "add_challenge", async ({
  game = null,
  name = null,
  message = null,
  testId = null
}) => {
  if (!game) return false;
  if (!name) return false;
  if (!message) return false;
  const response = await Firestore.firestore.collection(`games`).doc(`${game}`).collection(`challenges`).add({
    name,
    message,
    start_timestamp: Date.now(),
    end_timestamp: Date.now() + 10080000
  });
  const map = {
    id: testId ? testId : response.id,
    ...(await response.get()).data()
  };
  await response.set(map);
  return (await response.get()).data();
});

_defineProperty(Firestore, "add_submission_entry", async ({
  game = null,
  likes = null,
  views = null,
  player_id = null,
  team_id = null,
  tribe_id = null,
  challenge_id = null,
  url = null,
  testId = null
}) => {
  if (!game || !likes || !views || !player_id, !team_id, !tribe_id || !challenge_id || !url) return false;
  const response = await Firestore.firestore.collection(`games`).doc(`${game}`).collection(`entries`).add({
    likes,
    views,
    player_id,
    team_id,
    tribe_id,
    challenge_id,
    url
  });
  const map = {
    id: testId ? testId : response.id,
    ...(await response.get()).data()
  };
  await response.set(map);
  return (await response.get()).data();
});

_defineProperty(Firestore, "add_player", async ({
  game = null,
  tiktok = null,
  email = null,
  tribe_id = null,
  team_id = null,
  active = null,
  testId = null
}) => {
  if (!game || !tiktok || !email || !tribe_id, !team_id, !active) return false;
  const response = await Firestore.firestore.collection(`games`).doc(`${game}`).collection(`players`).add({
    tiktok,
    email,
    tribe_id,
    team_id,
    active
  });
  const map = {
    id: testId ? testId : response.id,
    ...(await response.get()).data()
  };
  await response.set(map);
  const data = (await response.get()).data();
  return data;
});

_defineProperty(Firestore, "add_vote", async ({
  game = null,
  from_id = null,
  to_id = null,
  team_id = null,
  is_for_win = null,
  testId = null
}) => {
  if (!game || !from_id || !to_id || !team_id || !is_for_win) return false;
  const response = await Firestore.firestore.collection(`games`).doc(`${game}`).collection(`votes`).add({
    from_id,
    to_id,
    team_id,
    is_for_win
  });
  const map = {
    id: testId ? testId : response.id,
    ...(await response.get()).data()
  };
  await response.set(map);
  return (await response.get()).data();
});

/***/ }),

/***/ "./count_votes.js":
/*!************************!*\
  !*** ./count_votes.js ***!
  \************************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _src_services_Firestore__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../src/services/Firestore */ "../src/services/Firestore.js");
 // Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method

exports.handler = async (event, context, callback) => {
  try {
    const body = JSON.parse(event.body) || null;
    if (!body.game || !body.from_tribe || !body.is_for_win) throw new Error("problem with data in body");
    _src_services_Firestore__WEBPACK_IMPORTED_MODULE_0__["default"].initialise();
    const response = await _src_services_Firestore__WEBPACK_IMPORTED_MODULE_0__["default"].count_votes({
      game: body.game,
      from_tribe: body.from_tribe,
      is_for_win: body.is_for_win
    });
    callback(null, {
      statusCode: 200,
      body: JSON.stringify(response)
    });
  } catch (err) {
    callback(null, {
      statusCode: 500,
      body: err.toString()
    });
  }
};

/***/ }),

/***/ "dotenv":
/*!*************************!*\
  !*** external "dotenv" ***!
  \*************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = require("dotenv");

/***/ }),

/***/ "firebase-admin":
/*!*********************************!*\
  !*** external "firebase-admin" ***!
  \*********************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = require("firebase-admin");

/***/ })

/******/ })));