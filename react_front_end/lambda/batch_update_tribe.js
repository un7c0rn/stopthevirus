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
/******/ 	return __webpack_require__(__webpack_require__.s = "./batch_update_tribe.js");
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
/* harmony import */ var firebase_admin__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! firebase-admin */ "firebase-admin");
/* harmony import */ var firebase_admin__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(firebase_admin__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _service_account_stv_game_db_test_0f631b94adde_json__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../service_account/stv-game-db-test-0f631b94adde.json */ "../service_account/stv-game-db-test-0f631b94adde.json");
var _service_account_stv_game_db_test_0f631b94adde_json__WEBPACK_IMPORTED_MODULE_1___namespace = /*#__PURE__*/__webpack_require__.t(/*! ../../service_account/stv-game-db-test-0f631b94adde.json */ "../service_account/stv-game-db-test-0f631b94adde.json", 1);
function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

// Google FireStore implementation


class Firestore {
  constructor() {
    _firestoreClient.set(this, {
      writable: true,
      value: void 0
    });

    _defineProperty(this, "initialise", () => {
      // Web app's Firebase configuration
      var firebaseConfig = {
        apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
        authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
        databaseURL: process.env.REACT_APP_FIREBASE_DB_URL,
        projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
        storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
        messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
        appId: process.env.REACT_APP_FIREBASE_APP_ID,
        measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID
      }; // Initialize Firebase

      const app = firebase_admin__WEBPACK_IMPORTED_MODULE_0___default.a.initializeApp({
        credential: firebase_admin__WEBPACK_IMPORTED_MODULE_0___default.a.credential.cert(_service_account_stv_game_db_test_0f631b94adde_json__WEBPACK_IMPORTED_MODULE_1__),
        databaseURL: "https://stv-game-db-test.firebaseio.com"
      });
      this.firestoreClient = firebase_admin__WEBPACK_IMPORTED_MODULE_0___default.a.firestore(app);
      const firestoreClient = this.firestoreClient;
      return {
        firebase: (firebase_admin__WEBPACK_IMPORTED_MODULE_0___default()),
        firestoreClient
      };
    });

    _defineProperty(this, "tribe_from_id", async (game = null, id = null) => {
      return await (await this.firestoreClient.doc(`games/${game}/tribes/${id}`).get()).data();
    });
  }

}

var _firestoreClient = new WeakMap();

/***/ }),

/***/ "./batch_update_tribe.js":
/*!*******************************!*\
  !*** ./batch_update_tribe.js ***!
  \*******************************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _src_services_Firestore__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../src/services/Firestore */ "../src/services/Firestore.js");
 // Docs on event and context https://www.netlify.com/docs/functions/#the-handler-method

exports.handler = (event, context, callback) => {
  try {
    const firestore = new _src_services_Firestore__WEBPACK_IMPORTED_MODULE_0__["default"]();
    firestore.initialise();
    const body = JSON.parse(event.body) || null;
    if (!body) throw new Error("problem with data in body");
    callback(null, {
      statusCode: 200,
      body: "ok"
    });
  } catch (err) {
    callback(null, {
      statusCode: 500,
      body: err.toString()
    });
  }
};

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
